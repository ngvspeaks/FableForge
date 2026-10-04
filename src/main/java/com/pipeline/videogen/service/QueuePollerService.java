package com.pipeline.videogen.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.pipeline.videogen.client.ComfyUIClient;
import com.pipeline.videogen.config.ComfyUIProperties;
import com.pipeline.videogen.model.GenerateVideoRequest;
import com.pipeline.videogen.model.VideoJob;
import com.pipeline.videogen.model.VideoJobStatus;
import com.pipeline.videogen.service.backoff.AdaptiveExponentialBackoff;
import com.pipeline.videogen.service.backoff.PollingBackoffStrategy;
import com.pipeline.videogen.storage.VideoJobRepository;
import com.pipeline.videogen.storage.VideoStorageService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.io.InputStream;
import java.time.Duration;
import java.time.Instant;
import java.util.Iterator;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;

@Service
public class QueuePollerService {

    private static final Logger log = LoggerFactory.getLogger(QueuePollerService.class);

    private final ComfyUIClient comfyUIClient;
    private final VideoStorageService videoStorageService;
    private final VideoJobRepository jobRepository;
    private final ComfyUIProperties properties;
    private final PollingBackoffStrategy backoffStrategy;

    @Autowired
    public QueuePollerService(ComfyUIClient comfyUIClient,
                              VideoStorageService videoStorageService,
                              VideoJobRepository jobRepository,
                              ComfyUIProperties properties,
                              PollingBackoffStrategy backoffStrategy) {
        this.comfyUIClient = comfyUIClient;
        this.videoStorageService = videoStorageService;
        this.jobRepository = jobRepository;
        this.properties = properties;
        this.backoffStrategy = backoffStrategy != null ? backoffStrategy : createDefaultBackoff(properties);
    }

    public QueuePollerService(ComfyUIClient comfyUIClient,
                              VideoStorageService videoStorageService,
                              VideoJobRepository jobRepository,
                              ComfyUIProperties properties) {
        this(comfyUIClient, videoStorageService, jobRepository, properties, createDefaultBackoff(properties));
    }

    private static PollingBackoffStrategy createDefaultBackoff(ComfyUIProperties properties) {
        return new AdaptiveExponentialBackoff(
                Duration.ofMillis(properties.effectiveInitialPollIntervalMs()),
                Duration.ofMillis(properties.effectiveMaxPollIntervalMs()),
                properties.backoffMultiplier(),
                properties.jitterFactor()
        );
    }

    /**
     * Polls ComfyUI asynchronously for prompt execution completion using adaptive backoff.
     */
    @Async
    public CompletableFuture<VideoJob> pollJobCompletionAsync(UUID jobId, String promptId, GenerateVideoRequest request) {
        Instant startTime = Instant.now();
        Duration timeout = Duration.ofSeconds(properties.timeoutSeconds());
        Duration currentDelay = Duration.ZERO;
        int attempt = 0;

        log.info("Starting adaptive polling for Job ID: {} (Prompt ID: {}) with timeout: {}s, initialBackoff: {}ms",
                jobId, promptId, timeout.toSeconds(), backoffStrategy.initialDelay().toMillis());

        while (Duration.between(startTime, Instant.now()).compareTo(timeout) < 0) {
            attempt++;
            try {
                JsonNode history = comfyUIClient.getExecutionHistory(promptId);

                if (history != null && history.has(promptId)) {
                    JsonNode promptHistory = history.get(promptId);

                    // Check for node execution errors
                    if (promptHistory.has("status")) {
                        JsonNode statusNode = promptHistory.get("status");
                        if ("error".equalsIgnoreCase(statusNode.path("status_str").asText())) {
                            String errorMsg = "ComfyUI execution error: " + statusNode.path("messages").toString();
                            log.error(errorMsg);
                            VideoJob failedJob = updateJobStatus(jobId, job -> job.withFailed(errorMsg));
                            return CompletableFuture.completedFuture(failedJob);
                        }
                    }

                    // Extract output media file
                    JsonNode outputsNode = promptHistory.path("outputs");
                    MediaOutputInfo outputMedia = extractOutputMedia(outputsNode);

                    if (outputMedia != null) {
                        Duration elapsed = Duration.between(startTime, Instant.now());
                        log.info("Detected rendered media for job {} on attempt {} (elapsed: {}ms): {}",
                                jobId, attempt, elapsed.toMillis(), outputMedia.filename());
                        updateJobStatus(jobId, job -> job.withStatus(VideoJobStatus.PROCESSING));

                        // Stream and store the output MP4
                        try (InputStream mediaStream = comfyUIClient.downloadMediaStream(
                                outputMedia.filename(), outputMedia.subfolder(), outputMedia.type())) {

                            VideoStorageService.StoredVideoInfo storedInfo = videoStorageService.storeRenderedVideo(
                                    jobId, outputMedia.filename(), mediaStream, request);

                            VideoJob completedJob = updateJobStatus(jobId, job ->
                                    job.withCompleted(storedInfo.fileName(), storedInfo.absolutePath()));

                            log.info("Job {} completed successfully! Stored at {}", jobId, storedInfo.absolutePath());
                            return CompletableFuture.completedFuture(completedJob);
                        }
                    }
                }

                // If not yet in history or output not ready, update to PROCESSING
                updateJobStatus(jobId, job -> job.withStatus(VideoJobStatus.PROCESSING));

                currentDelay = backoffStrategy.nextDelay(attempt, currentDelay);
                log.debug("Job {} attempt {} incomplete. Backing off for {}ms", jobId, attempt, currentDelay.toMillis());
                Thread.sleep(currentDelay.toMillis());

            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                VideoJob failedJob = updateJobStatus(jobId, job -> job.withFailed("Polling interrupted"));
                return CompletableFuture.completedFuture(failedJob);
            } catch (Exception e) {
                log.warn("Error during polling iteration {} for job {}: {}", attempt, jobId, e.getMessage());
                try {
                    currentDelay = backoffStrategy.nextDelay(attempt, currentDelay);
                    Thread.sleep(currentDelay.toMillis());
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    return CompletableFuture.completedFuture(updateJobStatus(jobId, job -> job.withFailed("Interrupted")));
                }
            }
        }

        String timeoutMsg = "Job timed out after " + timeout.toSeconds() + " seconds waiting for ComfyUI rendering (" + attempt + " attempts)";
        log.error(timeoutMsg);
        VideoJob timedOutJob = updateJobStatus(jobId, job -> job.withFailed(timeoutMsg));
        return CompletableFuture.completedFuture(timedOutJob);
    }

    private VideoJob updateJobStatus(UUID jobId, java.util.function.Function<VideoJob, VideoJob> updater) {
        return jobRepository.findById(jobId)
                .map(updater)
                .map(jobRepository::save)
                .orElse(null);
    }

    public MediaOutputInfo extractOutputMedia(JsonNode outputsNode) {
        if (outputsNode == null || outputsNode.isMissingNode() || outputsNode.isEmpty()) {
            return null;
        }

        for (Iterator<Map.Entry<String, JsonNode>> it = outputsNode.fields(); it.hasNext(); ) {
            Map.Entry<String, JsonNode> nodeEntry = it.next();
            JsonNode nodeOutputs = nodeEntry.getValue();

            // Look for videos / gifs / images lists
            for (String mediaKey : new String[]{"videos", "gifs", "images"}) {
                if (nodeOutputs.has(mediaKey) && nodeOutputs.get(mediaKey).isArray()) {
                    JsonNode mediaArray = nodeOutputs.get(mediaKey);
                    if (!mediaArray.isEmpty()) {
                        JsonNode firstItem = mediaArray.get(0);
                        String filename = firstItem.path("filename").asText();
                        String subfolder = firstItem.path("subfolder").asText("");
                        String type = firstItem.path("type").asText("output");
                        return new MediaOutputInfo(filename, subfolder, type);
                    }
                }
            }
        }
        return null;
    }

    public PollingBackoffStrategy getBackoffStrategy() {
        return backoffStrategy;
    }

    public record MediaOutputInfo(String filename, String subfolder, String type) {}
}

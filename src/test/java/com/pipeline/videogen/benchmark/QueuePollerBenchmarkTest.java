package com.pipeline.videogen.benchmark;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.pipeline.videogen.client.ComfyUIClient;
import com.pipeline.videogen.config.ComfyUIProperties;
import com.pipeline.videogen.model.GenerateVideoRequest;
import com.pipeline.videogen.model.VideoJob;
import com.pipeline.videogen.model.VideoJobStatus;
import com.pipeline.videogen.service.QueuePollerService;
import com.pipeline.videogen.service.backoff.AdaptiveExponentialBackoff;
import com.pipeline.videogen.service.backoff.PollingBackoffStrategy;
import com.pipeline.videogen.storage.VideoJobRepository;
import com.pipeline.videogen.storage.VideoStorageService;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.io.ByteArrayInputStream;
import java.time.Duration;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
public class QueuePollerBenchmarkTest {

    @Mock
    private ComfyUIClient comfyUIClient;

    @Mock
    private VideoStorageService videoStorageService;

    @Mock
    private VideoJobRepository jobRepository;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Test
    @DisplayName("Benchmark: Adaptive Backoff vs Fixed-Delay on Fast and Medium rendering completion")
    void runLatencyAndOverheadBenchmark() throws Exception {
        UUID jobId = UUID.randomUUID();
        String promptId = "bench-prompt";
        GenerateVideoRequest request = new GenerateVideoRequest("bench", null, 16, 512, 512, 20, 7.5, 123L);
        VideoJob initialJob = new VideoJob(jobId, null, VideoJobStatus.QUEUED, request, null, null, null, Instant.now(), null);

        when(jobRepository.findById(jobId)).thenAnswer(inv -> Optional.of(initialJob));
        when(jobRepository.save(any(VideoJob.class))).thenAnswer(inv -> inv.getArgument(0));
        when(comfyUIClient.downloadMediaStream(any(), any(), any()))
                .thenReturn(new ByteArrayInputStream(new byte[]{1, 2, 3}));
        when(videoStorageService.storeRenderedVideo(eq(jobId), any(), any(), eq(request)))
                .thenReturn(new VideoStorageService.StoredVideoInfo("bench.mp4", "/tmp/bench.mp4", 3L, "hash"));

        String emptyJson = "{}";
        String doneJson = """
                {
                    "bench-prompt": {
                        "outputs": {
                            "9": {
                                "videos": [{"filename": "bench.mp4", "subfolder": "", "type": "output"}]
                            }
                        }
                    }
                }
                """;

        // Setup scenario: Job completes after exactly 120ms
        long jobDurationMs = 120;

        // 1. Fixed delay poller (Fixed 500ms delay)
        AtomicInteger fixedCalls = new AtomicInteger();
        Instant fixedStartTime = Instant.now();
        when(comfyUIClient.getExecutionHistory(promptId)).thenAnswer(inv -> {
            fixedCalls.incrementAndGet();
            if (Duration.between(fixedStartTime, Instant.now()).toMillis() >= jobDurationMs) {
                return objectMapper.readTree(doneJson);
            }
            return objectMapper.readTree(emptyJson);
        });

        // Fixed backoff strategy (constant 500ms)
        PollingBackoffStrategy fixedStrategy = new PollingBackoffStrategy() {
            @Override public Duration nextDelay(int attempt, Duration previousDelay) { return Duration.ofMillis(500); }
            @Override public Duration initialDelay() { return Duration.ofMillis(500); }
            @Override public Duration maxDelay() { return Duration.ofMillis(500); }
        };

        ComfyUIProperties props = new ComfyUIProperties("http://localhost:8188", 500L, 500L, 500L, 1.0, 0.0, 10L, "./videos", "./temp");
        QueuePollerService fixedPoller = new QueuePollerService(comfyUIClient, videoStorageService, jobRepository, props, fixedStrategy);

        Instant t0Fixed = Instant.now();
        fixedPoller.pollJobCompletionAsync(jobId, promptId, request).get();
        long fixedElapsedMs = Duration.between(t0Fixed, Instant.now()).toMillis();

        // 2. Adaptive backoff poller (starts at 30ms, multiplier 1.5, max 500ms, no jitter for determinism)
        AtomicInteger adaptiveCalls = new AtomicInteger();
        Instant adaptiveStartTime = Instant.now();
        when(comfyUIClient.getExecutionHistory(promptId)).thenAnswer(inv -> {
            adaptiveCalls.incrementAndGet();
            if (Duration.between(adaptiveStartTime, Instant.now()).toMillis() >= jobDurationMs) {
                return objectMapper.readTree(doneJson);
            }
            return objectMapper.readTree(emptyJson);
        });

        PollingBackoffStrategy adaptiveStrategy = new AdaptiveExponentialBackoff(
                Duration.ofMillis(30), Duration.ofMillis(500), 1.5, 0.0);
        QueuePollerService adaptivePoller = new QueuePollerService(comfyUIClient, videoStorageService, jobRepository, props, adaptiveStrategy);

        Instant t0Adaptive = Instant.now();
        adaptivePoller.pollJobCompletionAsync(jobId, promptId, request).get();
        long adaptiveElapsedMs = Duration.between(t0Adaptive, Instant.now()).toMillis();

        System.out.println("=================================================");
        System.out.println("BENCHMARK RESULTS (Job ready at " + jobDurationMs + "ms):");
        System.out.println("Fixed Polling:    Elapsed = " + fixedElapsedMs + "ms, Calls = " + fixedCalls.get());
        System.out.println("Adaptive Backoff: Elapsed = " + adaptiveElapsedMs + "ms, Calls = " + adaptiveCalls.get());
        System.out.println("Latency reduction: " + (fixedElapsedMs - adaptiveElapsedMs) + "ms ("
                + String.format("%.1f", ((double)(fixedElapsedMs - adaptiveElapsedMs) / fixedElapsedMs * 100)) + "%)");
        System.out.println("=================================================");

        // Adaptive polling should detect completion significantly faster than fixed polling (since fixed slept 500ms!)
        assertThat(adaptiveElapsedMs).isLessThan(fixedElapsedMs);
    }
}

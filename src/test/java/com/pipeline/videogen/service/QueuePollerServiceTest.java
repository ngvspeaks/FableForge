package com.pipeline.videogen.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.pipeline.videogen.client.ComfyUIClient;
import com.pipeline.videogen.config.ComfyUIProperties;
import com.pipeline.videogen.model.GenerateVideoRequest;
import com.pipeline.videogen.model.VideoJob;
import com.pipeline.videogen.model.VideoJobStatus;
import com.pipeline.videogen.service.backoff.AdaptiveExponentialBackoff;
import com.pipeline.videogen.service.backoff.PollingBackoffStrategy;
import com.pipeline.videogen.storage.VideoJobRepository;
import com.pipeline.videogen.storage.VideoStorageService;
import org.junit.jupiter.api.BeforeEach;
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
import java.util.concurrent.CompletableFuture;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class QueuePollerServiceTest {

    @Mock
    private ComfyUIClient comfyUIClient;

    @Mock
    private VideoStorageService videoStorageService;

    @Mock
    private VideoJobRepository jobRepository;

    private final ObjectMapper objectMapper = new ObjectMapper();
    private ComfyUIProperties properties;
    private PollingBackoffStrategy fastBackoff;
    private QueuePollerService queuePollerService;

    @BeforeEach
    void setUp() {
        properties = new ComfyUIProperties(
                "http://localhost:8188",
                1000L,
                10L,
                100L,
                1.5,
                0.0,
                5L,
                "./storage/videos",
                "./storage/temp"
        );
        fastBackoff = new AdaptiveExponentialBackoff(Duration.ofMillis(10), Duration.ofMillis(50), 1.5, 0.0);
        queuePollerService = new QueuePollerService(comfyUIClient, videoStorageService, jobRepository, properties, fastBackoff);
    }

    private VideoJob createTestJob(UUID jobId, GenerateVideoRequest request) {
        return new VideoJob(jobId, null, VideoJobStatus.QUEUED, request, null, null, null, Instant.now(), null);
    }

    @Test
    @DisplayName("Immediate completion when outputs are available on first poll")
    void testImmediateCompletion() throws Exception {
        UUID jobId = UUID.randomUUID();
        String promptId = "test-prompt-001";
        GenerateVideoRequest request = new GenerateVideoRequest("prompt", null, 16, 512, 512, 20, 7.5, 123L);
        VideoJob initialJob = createTestJob(jobId, request);

        when(jobRepository.findById(jobId)).thenReturn(Optional.of(initialJob));
        when(jobRepository.save(any(VideoJob.class))).thenAnswer(inv -> inv.getArgument(0));

        String historyJson = """
                {
                    "test-prompt-001": {
                        "outputs": {
                            "9": {
                                "videos": [{"filename": "out.mp4", "subfolder": "", "type": "output"}]
                            }
                        }
                    }
                }
                """;
        when(comfyUIClient.getExecutionHistory(promptId)).thenReturn(objectMapper.readTree(historyJson));
        when(comfyUIClient.downloadMediaStream("out.mp4", "", "output"))
                .thenReturn(new ByteArrayInputStream(new byte[]{1, 2, 3}));
        when(videoStorageService.storeRenderedVideo(eq(jobId), eq("out.mp4"), any(), eq(request)))
                .thenReturn(new VideoStorageService.StoredVideoInfo("stored_out.mp4", "/storage/stored_out.mp4", 3L, "hash"));

        CompletableFuture<VideoJob> future = queuePollerService.pollJobCompletionAsync(jobId, promptId, request);
        VideoJob completed = future.get();

        assertThat(completed).isNotNull();
        assertThat(completed.status()).isEqualTo(VideoJobStatus.COMPLETED);
        assertThat(completed.outputFileName()).isEqualTo("stored_out.mp4");
        verify(comfyUIClient, times(1)).getExecutionHistory(promptId);
    }

    @Test
    @DisplayName("Poller retries with adaptive backoff until outputs appear")
    void testCompletionAfterMultipleBackoffAttempts() throws Exception {
        UUID jobId = UUID.randomUUID();
        String promptId = "test-prompt-multi";
        GenerateVideoRequest request = new GenerateVideoRequest("prompt", null, 16, 512, 512, 20, 7.5, 123L);
        VideoJob initialJob = createTestJob(jobId, request);

        when(jobRepository.findById(jobId)).thenReturn(Optional.of(initialJob));
        when(jobRepository.save(any(VideoJob.class))).thenAnswer(inv -> inv.getArgument(0));

        String emptyHistory = "{}";
        String readyHistory = """
                {
                    "test-prompt-multi": {
                        "outputs": {
                            "9": {
                                "videos": [{"filename": "multi.mp4", "subfolder": "", "type": "output"}]
                            }
                        }
                    }
                }
                """;
        when(comfyUIClient.getExecutionHistory(promptId))
                .thenReturn(objectMapper.readTree(emptyHistory))
                .thenReturn(objectMapper.readTree(emptyHistory))
                .thenReturn(objectMapper.readTree(readyHistory));

        when(comfyUIClient.downloadMediaStream("multi.mp4", "", "output"))
                .thenReturn(new ByteArrayInputStream(new byte[]{1, 2, 3}));
        when(videoStorageService.storeRenderedVideo(eq(jobId), eq("multi.mp4"), any(), eq(request)))
                .thenReturn(new VideoStorageService.StoredVideoInfo("multi.mp4", "/storage/multi.mp4", 3L, "hash"));

        CompletableFuture<VideoJob> future = queuePollerService.pollJobCompletionAsync(jobId, promptId, request);
        VideoJob completed = future.get();

        assertThat(completed).isNotNull();
        assertThat(completed.status()).isEqualTo(VideoJobStatus.COMPLETED);
        verify(comfyUIClient, times(3)).getExecutionHistory(promptId);
    }

    @Test
    @DisplayName("ComfyUI error status is detected and job marked as FAILED")
    void testComfyUIErrorStatus() throws Exception {
        UUID jobId = UUID.randomUUID();
        String promptId = "test-prompt-error";
        GenerateVideoRequest request = new GenerateVideoRequest("prompt", null, 16, 512, 512, 20, 7.5, 123L);
        VideoJob initialJob = createTestJob(jobId, request);

        when(jobRepository.findById(jobId)).thenReturn(Optional.of(initialJob));
        when(jobRepository.save(any(VideoJob.class))).thenAnswer(inv -> inv.getArgument(0));

        String errorHistory = """
                {
                    "test-prompt-error": {
                        "status": {
                            "status_str": "error",
                            "messages": ["Out of memory in VAE decode"]
                        }
                    }
                }
                """;
        when(comfyUIClient.getExecutionHistory(promptId)).thenReturn(objectMapper.readTree(errorHistory));

        CompletableFuture<VideoJob> future = queuePollerService.pollJobCompletionAsync(jobId, promptId, request);
        VideoJob failed = future.get();

        assertThat(failed).isNotNull();
        assertThat(failed.status()).isEqualTo(VideoJobStatus.FAILED);
        assertThat(failed.errorDetails()).contains("ComfyUI execution error");
    }

    @Test
    @DisplayName("Job times out when rendering exceeds deadline")
    void testTimeoutHandling() throws Exception {
        UUID jobId = UUID.randomUUID();
        String promptId = "test-prompt-timeout";
        GenerateVideoRequest request = new GenerateVideoRequest("prompt", null, 16, 512, 512, 20, 7.5, 123L);
        VideoJob initialJob = createTestJob(jobId, request);

        ComfyUIProperties shortTimeoutProperties = new ComfyUIProperties(
                "http://localhost:8188", 1000L, 50L, 100L, 1.5, 0.0, 1L, "./storage/videos", "./storage/temp");
        QueuePollerService shortPoller = new QueuePollerService(
                comfyUIClient, videoStorageService, jobRepository, shortTimeoutProperties,
                new AdaptiveExponentialBackoff(Duration.ofMillis(200), Duration.ofMillis(300), 1.5, 0.0));

        when(jobRepository.findById(jobId)).thenReturn(Optional.of(initialJob));
        when(jobRepository.save(any(VideoJob.class))).thenAnswer(inv -> inv.getArgument(0));
        when(comfyUIClient.getExecutionHistory(promptId)).thenReturn(objectMapper.readTree("{}"));

        CompletableFuture<VideoJob> future = shortPoller.pollJobCompletionAsync(jobId, promptId, request);
        VideoJob timedOut = future.get();

        assertThat(timedOut).isNotNull();
        assertThat(timedOut.status()).isEqualTo(VideoJobStatus.FAILED);
        assertThat(timedOut.errorDetails()).contains("Job timed out");
    }
}

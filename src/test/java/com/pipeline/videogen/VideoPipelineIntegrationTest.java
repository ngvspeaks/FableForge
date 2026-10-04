package com.pipeline.videogen;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.pipeline.videogen.model.GenerateVideoRequest;
import com.pipeline.videogen.model.VideoJob;
import com.pipeline.videogen.model.VideoJobStatus;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.Instant;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureMockMvc
class VideoPipelineIntegrationTest {

    private static MockWebServer mockComfyServer;

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @BeforeAll
    static void startServer() throws IOException {
        mockComfyServer = new MockWebServer();
        mockComfyServer.start();
    }

    @AfterAll
    static void stopServer() throws IOException {
        mockComfyServer.shutdown();
    }

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        String rawUrl = mockComfyServer.url("/").toString();
        final String baseUrl = rawUrl.endsWith("/") ? rawUrl.substring(0, rawUrl.length() - 1) : rawUrl;
        registry.add("comfyui.base-url", () -> baseUrl);
        registry.add("comfyui.poll-interval-ms", () -> 200);
        registry.add("comfyui.timeout-seconds", () -> 10);
    }

    @Test
    @DisplayName("End-to-End: Trigger generation, poll MockWebServer ComfyUI, store MP4, and stream output")
    void testEndToEndPipelineFlow() throws Exception {
        String testPromptId = "comfy-test-prompt-999";
        byte[] fakeMp4Content = "\u0000\u0000\u0000\u0018ftypmp42fake-video-payload".getBytes(StandardCharsets.UTF_8);

        // 1. Mock ComfyUI /prompt response
        mockComfyServer.enqueue(new MockResponse()
                .setResponseCode(200)
                .setHeader("Content-Type", "application/json")
                .setBody("""
                        {
                            "prompt_id": "comfy-test-prompt-999",
                            "number": 1,
                            "node_errors": {}
                        }
                        """));

        // 2. Mock ComfyUI /history response
        mockComfyServer.enqueue(new MockResponse()
                .setResponseCode(200)
                .setHeader("Content-Type", "application/json")
                .setBody("""
                        {
                            "comfy-test-prompt-999": {
                                "outputs": {
                                    "7": {
                                        "videos": [
                                            {
                                                "filename": "render_test_001.mp4",
                                                "subfolder": "",
                                                "type": "output"
                                            }
                                        ]
                                    }
                                }
                            }
                        }
                        """));

        // 3. Mock ComfyUI /view binary stream
        mockComfyServer.enqueue(new MockResponse()
                .setResponseCode(200)
                .setHeader("Content-Type", "video/mp4")
                .setBody(new okio.Buffer().write(fakeMp4Content)));

        // Trigger POST /api/v1/videos/generate
        GenerateVideoRequest request = new GenerateVideoRequest(
                "Futuristic cybernetic city with neon lights",
                "blurry, artifacts",
                16,
                512,
                512,
                20,
                7.5,
                99999L
        );

        MvcResult triggerResult = mockMvc.perform(post("/api/v1/videos/generate")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isAccepted())
                .andReturn();

        VideoJob initialJob = objectMapper.readValue(triggerResult.getResponse().getContentAsString(), VideoJob.class);
        assertThat(initialJob).isNotNull();
        assertThat(initialJob.jobId()).isNotNull();
        assertThat(initialJob.status()).isEqualTo(VideoJobStatus.QUEUED);

        // Wait/poll until COMPLETED status is reached
        Instant timeout = Instant.now().plus(Duration.ofSeconds(8));
        VideoJob completedJob = null;

        while (Instant.now().isBefore(timeout)) {
            MvcResult pollResult = mockMvc.perform(get("/api/v1/videos/jobs/" + initialJob.jobId()))
                    .andExpect(status().isOk())
                    .andReturn();

            VideoJob current = objectMapper.readValue(pollResult.getResponse().getContentAsString(), VideoJob.class);
            if (current.status() == VideoJobStatus.COMPLETED) {
                completedJob = current;
                break;
            }
            Thread.sleep(150);
        }

        assertThat(completedJob).isNotNull();
        assertThat(completedJob.status()).isEqualTo(VideoJobStatus.COMPLETED);
        assertThat(completedJob.outputFileName()).contains("render_test_001.mp4");

        // Verify stream endpoint serves the downloaded MP4
        MvcResult streamResult = mockMvc.perform(get("/api/v1/videos/stream/" + completedJob.outputFileName()))
                .andExpect(status().isOk())
                .andReturn();

        assertThat(streamResult.getResponse().getContentType()).isEqualTo("video/mp4");
        assertThat(streamResult.getResponse().getContentAsByteArray()).isEqualTo(fakeMp4Content);
    }
}

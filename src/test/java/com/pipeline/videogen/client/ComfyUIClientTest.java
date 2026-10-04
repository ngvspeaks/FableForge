package com.pipeline.videogen.client;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.pipeline.videogen.exception.ComfyUIWorkflowException;
import com.pipeline.videogen.model.ComfyPromptResponse;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import okhttp3.mockwebserver.RecordedRequest;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class ComfyUIClientTest {

    private MockWebServer mockWebServer;
    private ComfyUIClient comfyUIClient;
    private ObjectMapper objectMapper;

    @BeforeEach
    void setUp() throws IOException {
        mockWebServer = new MockWebServer();
        mockWebServer.start();

        objectMapper = new ObjectMapper();
        String baseUrl = mockWebServer.url("/").toString();
        // Strip trailing slash for RestClient compatibility
        if (baseUrl.endsWith("/")) {
            baseUrl = baseUrl.substring(0, baseUrl.length() - 1);
        }

        comfyUIClient = new ComfyUIClient(baseUrl, objectMapper);
    }

    @AfterEach
    void tearDown() throws IOException {
        mockWebServer.shutdown();
    }

    @Test
    @DisplayName("submitPrompt should send JSON payload and receive prompt_id")
    void testSubmitPromptSuccess() throws Exception {
        String mockResponseBody = """
                {
                    "prompt_id": "test-prompt-uuid-1234",
                    "number": 42,
                    "node_errors": {}
                }
                """;
        mockWebServer.enqueue(new MockResponse()
                .setResponseCode(200)
                .setHeader("Content-Type", "application/json")
                .setBody(mockResponseBody));

        Map<String, Object> workflow = Map.of("node1", Map.of("class_type", "KSampler"));
        ComfyPromptResponse response = comfyUIClient.submitPrompt(workflow);

        assertThat(response).isNotNull();
        assertThat(response.promptId()).isEqualTo("test-prompt-uuid-1234");
        assertThat(response.number()).isEqualTo(42);

        RecordedRequest recordedRequest = mockWebServer.takeRequest();
        assertThat(recordedRequest.getMethod()).isEqualTo("POST");
        assertThat(recordedRequest.getPath()).isEqualTo("/prompt");
        assertThat(recordedRequest.getBody().readUtf8()).contains("client_id", "prompt");
    }

    @Test
    @DisplayName("submitPrompt should throw ComfyUIWorkflowException on ComfyUI node errors")
    void testSubmitPromptWithNodeErrors() {
        String mockResponseBody = """
                {
                    "error": "validation_error",
                    "node_errors": {
                        "3": {"errors": ["Input 'model' is missing"]}
                    }
                }
                """;
        mockWebServer.enqueue(new MockResponse()
                .setResponseCode(400)
                .setHeader("Content-Type", "application/json")
                .setBody(mockResponseBody));

        Map<String, Object> workflow = Map.of("node1", Map.of());

        assertThatThrownBy(() -> comfyUIClient.submitPrompt(workflow))
                .isInstanceOf(ComfyUIWorkflowException.class)
                .hasMessageContaining("validation_error");
    }

    @Test
    @DisplayName("getExecutionHistory should retrieve execution details for a prompt")
    void testGetExecutionHistory() throws Exception {
        String promptId = "test-prompt-uuid-1234";
        String mockHistory = """
                {
                    "test-prompt-uuid-1234": {
                        "prompt": [1, "test-prompt-uuid-1234"],
                        "outputs": {
                            "7": {
                                "videos": [
                                    {"filename": "rendered_001.mp4", "subfolder": "", "type": "output"}
                                ]
                            }
                        }
                    }
                }
                """;
        mockWebServer.enqueue(new MockResponse()
                .setResponseCode(200)
                .setHeader("Content-Type", "application/json")
                .setBody(mockHistory));

        JsonNode history = comfyUIClient.getExecutionHistory(promptId);

        assertThat(history).isNotNull();
        assertThat(history.has(promptId)).isTrue();
        assertThat(history.get(promptId).path("outputs").path("7").path("videos").get(0).path("filename").asText())
                .isEqualTo("rendered_001.mp4");
    }

    @Test
    @DisplayName("downloadMediaStream should stream binary MP4 payload from /view endpoint")
    void testDownloadMediaStream() throws Exception {
        byte[] mockMp4Bytes = "FAKE_MP4_BINARY_DATA_HEADER".getBytes(StandardCharsets.UTF_8);

        mockWebServer.enqueue(new MockResponse()
                .setResponseCode(200)
                .setHeader("Content-Type", "video/mp4")
                .setBody(new okio.Buffer().write(mockMp4Bytes)));

        try (InputStream in = comfyUIClient.downloadMediaStream("rendered_001.mp4", "", "output")) {
            byte[] downloaded = in.readAllBytes();
            assertThat(downloaded).isEqualTo(mockMp4Bytes);
        }

        RecordedRequest request = mockWebServer.takeRequest();
        assertThat(request.getPath()).contains("/view?filename=rendered_001.mp4");
    }
}

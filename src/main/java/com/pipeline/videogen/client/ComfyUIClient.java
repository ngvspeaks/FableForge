package com.pipeline.videogen.client;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.pipeline.videogen.config.ComfyUIProperties;
import com.pipeline.videogen.exception.ComfyUICommunicationException;
import com.pipeline.videogen.exception.ComfyUIWorkflowException;
import com.pipeline.videogen.model.ComfyPromptRequest;
import com.pipeline.videogen.model.ComfyPromptResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.io.InputStream;
import java.net.http.HttpClient;
import java.time.Duration;
import java.util.Map;
import java.util.UUID;

@Component
public class ComfyUIClient {

    private static final Logger log = LoggerFactory.getLogger(ComfyUIClient.class);

    private final RestClient restClient;
    private final ObjectMapper objectMapper;
    private final String clientId;

    @org.springframework.beans.factory.annotation.Autowired
    public ComfyUIClient(ComfyUIProperties properties, ObjectMapper objectMapper) {
        this(properties.baseUrl(), objectMapper);
    }

    public ComfyUIClient(String baseUrl, ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
        this.clientId = "springboot-pipeline-" + UUID.randomUUID();

        HttpClient httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(10))
                .build();

        JdkClientHttpRequestFactory requestFactory = new JdkClientHttpRequestFactory(httpClient);
        requestFactory.setReadTimeout(Duration.ofSeconds(120));

        this.restClient = RestClient.builder()
                .baseUrl(baseUrl)
                .requestFactory(requestFactory)
                .defaultHeader("Accept", MediaType.APPLICATION_JSON_VALUE)
                .build();

        log.info("Initialized ComfyUI RestClient targeting {} with clientId: {}", baseUrl, clientId);
    }

    /**
     * Submits a workflow graph to ComfyUI /prompt endpoint.
     */
    public ComfyPromptResponse submitPrompt(Map<String, Object> workflow) {
        ComfyPromptRequest request = new ComfyPromptRequest(clientId, workflow);

        try {
            ComfyPromptResponse response = restClient.post()
                    .uri("/prompt")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(request)
                    .retrieve()
                    .onStatus(HttpStatusCode::isError, (req, res) -> {
                        String body = new String(res.getBody().readAllBytes());
                        throw new ComfyUIWorkflowException("ComfyUI /prompt returned error (" + res.getStatusCode() + "): " + body);
                    })
                    .body(ComfyPromptResponse.class);

            if (response == null || response.promptId() == null) {
                throw new ComfyUIWorkflowException("ComfyUI returned empty response or missing prompt_id");
            }
            if (response.hasErrors()) {
                throw new ComfyUIWorkflowException("ComfyUI prompt error: " + response.nodeErrors());
            }

            log.info("Prompt queued successfully in ComfyUI. PromptId: {}, QueueNumber: {}",
                    response.promptId(), response.number());
            return response;

        } catch (ComfyUIWorkflowException e) {
            throw e;
        } catch (Exception e) {
            log.error("Failed to submit prompt to ComfyUI: {}", e.getMessage());
            throw new ComfyUICommunicationException("Error communicating with ComfyUI /prompt: " + e.getMessage(), e);
        }
    }

    /**
     * Checks history of a specific prompt execution.
     */
    public JsonNode getExecutionHistory(String promptId) {
        try {
            String rawJson = restClient.get()
                    .uri("/history/{promptId}", promptId)
                    .retrieve()
                    .onStatus(HttpStatusCode::isError, (req, res) -> {
                        throw new ComfyUICommunicationException("ComfyUI /history returned error code: " + res.getStatusCode());
                    })
                    .body(String.class);

            if (rawJson == null || rawJson.isBlank()) {
                return null;
            }
            return objectMapper.readTree(rawJson);
        } catch (ComfyUICommunicationException e) {
            throw e;
        } catch (Exception e) {
            log.error("Failed to query execution history for prompt {}: {}", promptId, e.getMessage());
            throw new ComfyUICommunicationException("Error querying ComfyUI history for prompt: " + promptId, e);
        }
    }

    /**
     * Checks overall queue status from ComfyUI /queue endpoint.
     */
    public JsonNode getQueueStatus() {
        try {
            return restClient.get()
                    .uri("/queue")
                    .retrieve()
                    .body(JsonNode.class);
        } catch (Exception e) {
            throw new ComfyUICommunicationException("Error fetching ComfyUI queue status: " + e.getMessage(), e);
        }
    }

    /**
     * Streams rendered media (e.g. MP4 video) from ComfyUI /view endpoint.
     */
    public InputStream downloadMediaStream(String filename, String subfolder, String type) {
        try {
            Resource resource = restClient.get()
                    .uri(uriBuilder -> uriBuilder
                            .path("/view")
                            .queryParam("filename", filename)
                            .queryParam("subfolder", subfolder != null ? subfolder : "")
                            .queryParam("type", type != null ? type : "output")
                            .build())
                    .accept(MediaType.APPLICATION_OCTET_STREAM, MediaType.ALL)
                    .retrieve()
                    .body(Resource.class);

            if (resource == null) {
                throw new ComfyUICommunicationException("Received null media resource from ComfyUI for file: " + filename);
            }
            return resource.getInputStream();
        } catch (Exception e) {
            log.error("Failed to stream rendered video {} from ComfyUI: {}", filename, e.getMessage());
            throw new ComfyUICommunicationException("Error downloading media from ComfyUI: " + e.getMessage(), e);
        }
    }

    public String getClientId() {
        return clientId;
    }
}

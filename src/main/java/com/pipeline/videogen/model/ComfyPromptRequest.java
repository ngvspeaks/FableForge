package com.pipeline.videogen.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.Map;

public record ComfyPromptRequest(
        @JsonProperty("client_id")
        String clientId,

        @JsonProperty("prompt")
        Map<String, Object> prompt,

        @JsonProperty("extra_data")
        Map<String, Object> extraData
) {
    public ComfyPromptRequest(String clientId, Map<String, Object> prompt) {
        this(clientId, prompt, Map.of());
    }
}

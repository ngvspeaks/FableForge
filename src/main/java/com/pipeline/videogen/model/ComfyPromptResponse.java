package com.pipeline.videogen.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.Map;

@JsonIgnoreProperties(ignoreUnknown = true)
public record ComfyPromptResponse(
        @JsonProperty("prompt_id")
        String promptId,

        @JsonProperty("number")
        Integer number,

        @JsonProperty("node_errors")
        Map<String, Object> nodeErrors,

        @JsonProperty("error")
        Object error
) {
    public boolean hasErrors() {
        return (nodeErrors != null && !nodeErrors.isEmpty()) || error != null;
    }
}

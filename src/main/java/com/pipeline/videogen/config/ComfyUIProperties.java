package com.pipeline.videogen.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.DefaultValue;

@ConfigurationProperties(prefix = "comfyui")
public record ComfyUIProperties(
        @DefaultValue("http://localhost:8188") String baseUrl,
        @DefaultValue("1000") long pollIntervalMs,
        @DefaultValue("300") long timeoutSeconds,
        @DefaultValue("./storage/videos") String storageDir,
        @DefaultValue("./storage/temp") String tempDir
) {}

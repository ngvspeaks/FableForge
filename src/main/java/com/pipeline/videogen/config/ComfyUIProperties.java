package com.pipeline.videogen.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.DefaultValue;

@ConfigurationProperties(prefix = "comfyui")
public record ComfyUIProperties(
        @DefaultValue("http://localhost:8188") String baseUrl,
        @DefaultValue("1000") long pollIntervalMs,
        @DefaultValue("100") long minPollIntervalMs,
        @DefaultValue("3000") long maxPollIntervalMs,
        @DefaultValue("1.5") double backoffMultiplier,
        @DefaultValue("0.1") double jitterFactor,
        @DefaultValue("300") long timeoutSeconds,
        @DefaultValue("./storage/videos") String storageDir,
        @DefaultValue("./storage/temp") String tempDir
) {
    /**
     * Resolves the effective initial polling delay, respecting pollIntervalMs if explicitly set lower.
     */
    public long effectiveInitialPollIntervalMs() {
        return Math.min(minPollIntervalMs, pollIntervalMs);
    }

    /**
     * Resolves the effective maximum polling delay.
     */
    public long effectiveMaxPollIntervalMs() {
        return Math.max(maxPollIntervalMs, pollIntervalMs);
    }
}

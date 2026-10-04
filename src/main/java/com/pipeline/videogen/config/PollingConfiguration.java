package com.pipeline.videogen.config;

import com.pipeline.videogen.service.backoff.AdaptiveExponentialBackoff;
import com.pipeline.videogen.service.backoff.PollingBackoffStrategy;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.Duration;

@Configuration
public class PollingConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public PollingBackoffStrategy pollingBackoffStrategy(ComfyUIProperties properties) {
        return new AdaptiveExponentialBackoff(
                Duration.ofMillis(properties.effectiveInitialPollIntervalMs()),
                Duration.ofMillis(properties.effectiveMaxPollIntervalMs()),
                properties.backoffMultiplier(),
                properties.jitterFactor()
        );
    }
}

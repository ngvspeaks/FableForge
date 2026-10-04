package com.pipeline.videogen.service.backoff;

import java.time.Duration;
import java.util.concurrent.ThreadLocalRandom;

/**
 * Adaptive exponential backoff strategy with bounded jitter.
 * Polling begins with a low initial delay (minimizing reaction latency for fast completions),
 * and exponentially expands up to a maximum cap (minimizing execution overhead and network load
 * for lengthy rendering operations). Jitter is applied to prevent thundering-herd synchronization.
 */
public class AdaptiveExponentialBackoff implements PollingBackoffStrategy {

    private final Duration initialDelay;
    private final Duration maxDelay;
    private final double multiplier;
    private final double jitterFactor;

    public AdaptiveExponentialBackoff(Duration initialDelay, Duration maxDelay, double multiplier, double jitterFactor) {
        if (initialDelay == null || initialDelay.isNegative() || initialDelay.isZero()) {
            throw new IllegalArgumentException("initialDelay must be positive and non-null");
        }
        if (maxDelay == null || maxDelay.compareTo(initialDelay) < 0) {
            throw new IllegalArgumentException("maxDelay must be >= initialDelay and non-null");
        }
        if (multiplier < 1.0) {
            throw new IllegalArgumentException("multiplier must be >= 1.0");
        }
        if (jitterFactor < 0.0 || jitterFactor > 1.0) {
            throw new IllegalArgumentException("jitterFactor must be between 0.0 and 1.0");
        }
        this.initialDelay = initialDelay;
        this.maxDelay = maxDelay;
        this.multiplier = multiplier;
        this.jitterFactor = jitterFactor;
    }

    @Override
    public Duration nextDelay(int attempt, Duration previousDelay) {
        if (attempt <= 1 || previousDelay == null || previousDelay.isZero()) {
            return applyJitter(initialDelay);
        }

        long rawNextMs = Math.round(previousDelay.toMillis() * multiplier);
        long cappedMs = Math.min(rawNextMs, maxDelay.toMillis());
        return applyJitter(Duration.ofMillis(cappedMs));
    }

    private Duration applyJitter(Duration base) {
        if (jitterFactor <= 0.0) {
            return base;
        }
        long baseMs = base.toMillis();
        long variance = Math.round(baseMs * jitterFactor);
        if (variance == 0) {
            return base;
        }
        long min = Math.max(1, baseMs - variance);
        long max = baseMs + variance;
        long jitteredMs = ThreadLocalRandom.current().nextLong(min, max + 1);
        long bounded = Math.min(jitteredMs, maxDelay.toMillis());
        return Duration.ofMillis(Math.max(1, bounded));
    }

    @Override
    public Duration initialDelay() {
        return initialDelay;
    }

    @Override
    public Duration maxDelay() {
        return maxDelay;
    }

    public double multiplier() {
        return multiplier;
    }

    public double jitterFactor() {
        return jitterFactor;
    }
}

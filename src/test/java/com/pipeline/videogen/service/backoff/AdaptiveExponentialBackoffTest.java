package com.pipeline.videogen.service.backoff;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import java.time.Duration;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class AdaptiveExponentialBackoffTest {

    @Test
    @DisplayName("Initial attempt returns base initial delay without jitter when jitterFactor=0")
    void testInitialDelayDeterministic() {
        AdaptiveExponentialBackoff backoff = new AdaptiveExponentialBackoff(
                Duration.ofMillis(100), Duration.ofMillis(2000), 1.5, 0.0);

        Duration d1 = backoff.nextDelay(1, Duration.ZERO);
        assertThat(d1).isEqualTo(Duration.ofMillis(100));

        Duration d1Null = backoff.nextDelay(1, null);
        assertThat(d1Null).isEqualTo(Duration.ofMillis(100));
    }

    @Test
    @DisplayName("Subsequent attempts scale exponentially by multiplier")
    void testExponentialProgression() {
        AdaptiveExponentialBackoff backoff = new AdaptiveExponentialBackoff(
                Duration.ofMillis(100), Duration.ofMillis(1000), 2.0, 0.0);

        Duration d1 = backoff.nextDelay(1, Duration.ZERO);
        assertThat(d1.toMillis()).isEqualTo(100);

        Duration d2 = backoff.nextDelay(2, d1);
        assertThat(d2.toMillis()).isEqualTo(200);

        Duration d3 = backoff.nextDelay(3, d2);
        assertThat(d3.toMillis()).isEqualTo(400);

        Duration d4 = backoff.nextDelay(4, d3);
        assertThat(d4.toMillis()).isEqualTo(800);

        Duration d5 = backoff.nextDelay(5, d4);
        assertThat(d5.toMillis()).isEqualTo(1000); // capped at maxDelay
    }

    @Test
    @DisplayName("Delays are strictly bounded by maxDelay")
    void testMaxDelayCap() {
        AdaptiveExponentialBackoff backoff = new AdaptiveExponentialBackoff(
                Duration.ofMillis(100), Duration.ofMillis(500), 2.0, 0.0);

        Duration d = Duration.ofMillis(400);
        Duration next = backoff.nextDelay(4, d);
        assertThat(next.toMillis()).isEqualTo(500);

        Duration nextAfterMax = backoff.nextDelay(5, next);
        assertThat(nextAfterMax.toMillis()).isEqualTo(500);
    }

    @Test
    @DisplayName("Jitter stays within configured bounds")
    void testJitterBounds() {
        AdaptiveExponentialBackoff backoff = new AdaptiveExponentialBackoff(
                Duration.ofMillis(200), Duration.ofMillis(2000), 1.5, 0.2);

        for (int i = 0; i < 50; i++) {
            Duration delay = backoff.nextDelay(1, Duration.ZERO);
            // 200 ms with +/- 20% -> [160, 240]
            assertThat(delay.toMillis()).isBetween(150L, 250L);
        }
    }

    @Test
    @DisplayName("Constructor enforces valid argument constraints")
    void testValidationConstraints() {
        assertThatThrownBy(() -> new AdaptiveExponentialBackoff(
                Duration.ofMillis(0), Duration.ofMillis(500), 1.5, 0.1))
                .isInstanceOf(IllegalArgumentException.class);

        assertThatThrownBy(() -> new AdaptiveExponentialBackoff(
                Duration.ofMillis(500), Duration.ofMillis(100), 1.5, 0.1))
                .isInstanceOf(IllegalArgumentException.class);

        assertThatThrownBy(() -> new AdaptiveExponentialBackoff(
                Duration.ofMillis(100), Duration.ofMillis(500), 0.5, 0.1))
                .isInstanceOf(IllegalArgumentException.class);

        assertThatThrownBy(() -> new AdaptiveExponentialBackoff(
                Duration.ofMillis(100), Duration.ofMillis(500), 1.5, 1.5))
                .isInstanceOf(IllegalArgumentException.class);
    }
}

package com.pipeline.videogen.service.backoff;

import java.time.Duration;

/**
 * Strategy interface defining how delays between polling attempts should be calculated.
 */
public interface PollingBackoffStrategy {

    /**
     * Calculates the next backoff delay given the current attempt (1-based) and the previous delay.
     *
     * @param attempt       the 1-based attempt index (1 for the first delay)
     * @param previousDelay the duration slept in the previous iteration, or Duration.ZERO for initial
     * @return Duration to wait before the next polling attempt
     */
    Duration nextDelay(int attempt, Duration previousDelay);

    /**
     * @return the initial polling delay
     */
    Duration initialDelay();

    /**
     * @return the upper ceiling for polling delays
     */
    Duration maxDelay();
}

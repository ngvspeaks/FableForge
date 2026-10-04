package com.pipeline.videogen.exception;

import java.util.UUID;

public class JobNotFoundException extends RuntimeException {
    public JobNotFoundException(UUID jobId) {
        super("Video generation job not found with id: " + jobId);
    }
}

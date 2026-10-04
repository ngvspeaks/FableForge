package com.pipeline.videogen.exception;

public class ComfyUIException extends RuntimeException {
    public ComfyUIException(String message) {
        super(message);
    }

    public ComfyUIException(String message, Throwable cause) {
        super(message, cause);
    }
}

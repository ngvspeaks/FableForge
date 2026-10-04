package com.pipeline.videogen.exception;

public class ComfyUICommunicationException extends ComfyUIException {
    public ComfyUICommunicationException(String message) {
        super(message);
    }

    public ComfyUICommunicationException(String message, Throwable cause) {
        super(message, cause);
    }
}

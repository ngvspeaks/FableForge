package com.pipeline.videogen.model;

import java.time.Instant;
import java.util.UUID;

public record VideoJob(
        UUID jobId,
        String promptId,
        VideoJobStatus status,
        GenerateVideoRequest request,
        String outputFileName,
        String outputFilePath,
        String errorDetails,
        Instant createdAt,
        Instant completedAt
) {
    public static VideoJob createInitial(GenerateVideoRequest request) {
        return new VideoJob(
                UUID.randomUUID(),
                null,
                VideoJobStatus.SUBMITTED,
                request,
                null,
                null,
                null,
                Instant.now(),
                null
        );
    }

    public VideoJob withPromptId(String promptId) {
        return new VideoJob(
                this.jobId,
                promptId,
                VideoJobStatus.QUEUED,
                this.request,
                this.outputFileName,
                this.outputFilePath,
                this.errorDetails,
                this.createdAt,
                this.completedAt
        );
    }

    public VideoJob withStatus(VideoJobStatus status) {
        return new VideoJob(
                this.jobId,
                this.promptId,
                status,
                this.request,
                this.outputFileName,
                this.outputFilePath,
                this.errorDetails,
                this.createdAt,
                this.completedAt
        );
    }

    public VideoJob withCompleted(String outputFileName, String outputFilePath) {
        return new VideoJob(
                this.jobId,
                this.promptId,
                VideoJobStatus.COMPLETED,
                this.request,
                outputFileName,
                outputFilePath,
                null,
                this.createdAt,
                Instant.now()
        );
    }

    public VideoJob withFailed(String errorDetails) {
        return new VideoJob(
                this.jobId,
                this.promptId,
                VideoJobStatus.FAILED,
                this.request,
                this.outputFileName,
                this.outputFilePath,
                errorDetails,
                this.createdAt,
                Instant.now()
        );
    }
}

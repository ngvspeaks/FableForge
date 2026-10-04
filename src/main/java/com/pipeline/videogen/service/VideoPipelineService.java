package com.pipeline.videogen.service;

import com.pipeline.videogen.client.ComfyUIClient;
import com.pipeline.videogen.client.WorkflowPayloadInjector;
import com.pipeline.videogen.model.ComfyPromptResponse;
import com.pipeline.videogen.model.GenerateVideoRequest;
import com.pipeline.videogen.model.VideoJob;
import com.pipeline.videogen.storage.VideoJobRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.UUID;

@Service
public class VideoPipelineService {

    private static final Logger log = LoggerFactory.getLogger(VideoPipelineService.class);

    private final ComfyUIClient comfyUIClient;
    private final WorkflowPayloadInjector payloadInjector;
    private final QueuePollerService pollerService;
    private final VideoJobRepository jobRepository;

    public VideoPipelineService(ComfyUIClient comfyUIClient,
                                WorkflowPayloadInjector payloadInjector,
                                QueuePollerService pollerService,
                                VideoJobRepository jobRepository) {
        this.comfyUIClient = comfyUIClient;
        this.payloadInjector = payloadInjector;
        this.pollerService = pollerService;
        this.jobRepository = jobRepository;
    }

    /**
     * Triggers end-to-end text-to-video generation pipeline.
     */
    public VideoJob triggerGeneration(GenerateVideoRequest request) {
        log.info("Triggering video generation with prompt: '{}', frames: {}, steps: {}",
                request.prompt(), request.frames(), request.steps());

        // Create initial tracked job
        VideoJob job = VideoJob.createInitial(request);
        jobRepository.save(job);

        // Inject dynamic parameters into ComfyUI workflow JSON
        Map<String, Object> workflow = payloadInjector.injectPromptWorkflow(request);

        // Submit to ComfyUI /prompt
        ComfyPromptResponse promptResponse = comfyUIClient.submitPrompt(workflow);

        // Transition job status to QUEUED
        job = job.withPromptId(promptResponse.promptId());
        jobRepository.save(job);

        // Launch background poller on virtual thread
        pollerService.pollJobCompletionAsync(job.jobId(), promptResponse.promptId(), request);

        return job;
    }

    public VideoJob getJob(UUID jobId) {
        return jobRepository.findById(jobId)
                .orElseThrow(() -> new com.pipeline.videogen.exception.JobNotFoundException(jobId));
    }

    public java.util.List<VideoJob> getAllJobs() {
        return jobRepository.findAllRecent();
    }
}

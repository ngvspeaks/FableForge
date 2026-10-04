package com.pipeline.videogen.controller;

import com.pipeline.videogen.model.GenerateVideoRequest;
import com.pipeline.videogen.model.VideoJob;
import com.pipeline.videogen.service.VideoPipelineService;
import com.pipeline.videogen.storage.VideoStorageService;
import jakarta.validation.Valid;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/videos")
public class VideoGenerationController {

    private final VideoPipelineService pipelineService;
    private final VideoStorageService storageService;

    public VideoGenerationController(VideoPipelineService pipelineService, VideoStorageService storageService) {
        this.pipelineService = pipelineService;
        this.storageService = storageService;
    }

    @PostMapping("/generate")
    public ResponseEntity<VideoJob> triggerGeneration(@Valid @RequestBody GenerateVideoRequest request) {
        VideoJob job = pipelineService.triggerGeneration(request);
        return ResponseEntity.status(HttpStatus.ACCEPTED).body(job);
    }

    @GetMapping("/jobs/{jobId}")
    public ResponseEntity<VideoJob> getJobStatus(@PathVariable UUID jobId) {
        VideoJob job = pipelineService.getJob(jobId);
        return ResponseEntity.ok(job);
    }

    @GetMapping("/jobs")
    public ResponseEntity<List<VideoJob>> listRecentJobs() {
        return ResponseEntity.ok(pipelineService.getAllJobs());
    }

    @GetMapping("/stream/{filename}")
    public ResponseEntity<Resource> streamVideo(@PathVariable String filename) {
        Resource videoResource = storageService.loadVideoAsResource(filename);
        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType("video/mp4"))
                .header(HttpHeaders.CONTENT_DISPOSITION, "inline; filename=\"" + filename + "\"")
                .body(videoResource);
    }
}

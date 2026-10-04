package com.pipeline.videogen.storage;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.pipeline.videogen.config.ComfyUIProperties;
import com.pipeline.videogen.model.GenerateVideoRequest;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.core.io.Resource;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;

class VideoStorageServiceTest {

    @TempDir
    Path tempDir;

    private VideoStorageService storageService;
    private ObjectMapper objectMapper;

    @BeforeEach
    void setUp() {
        Path storagePath = tempDir.resolve("videos");
        Path scratchTempPath = tempDir.resolve("temp");
        objectMapper = new ObjectMapper();

        ComfyUIProperties props = new ComfyUIProperties(
                "http://localhost:8188",
                1000L,
                100L,
                3000L,
                1.5,
                0.1,
                300L,
                storagePath.toString(),
                scratchTempPath.toString()
        );

        storageService = new VideoStorageService(props, objectMapper);
        storageService.init();
    }

    @Test
    @DisplayName("storeRenderedVideo should store video atomically, generate sha256 and metadata json")
    void testStoreRenderedVideo() throws IOException {
        UUID jobId = UUID.randomUUID();
        String originalName = "animated_frame_001.mp4";
        byte[] videoContent = "SAMPLE_MP4_VIDEO_STREAM_BYTES_CONTENT".getBytes(StandardCharsets.UTF_8);
        GenerateVideoRequest request = new GenerateVideoRequest(
                "A dramatic ocean storm with lightning",
                "blurry",
                30,
                512,
                512,
                25,
                7.0,
                12345L
        );

        VideoStorageService.StoredVideoInfo storedInfo = storageService.storeRenderedVideo(
                jobId, originalName, new ByteArrayInputStream(videoContent), request
        );

        assertThat(storedInfo).isNotNull();
        assertThat(storedInfo.fileName()).contains(jobId.toString());
        assertThat(storedInfo.fileName()).endsWith("animated_frame_001.mp4");
        assertThat(storedInfo.sizeBytes()).isEqualTo(videoContent.length);
        assertThat(storedInfo.sha256()).isNotBlank();

        // Verify video file exists on disk
        Path storedFile = Path.of(storedInfo.absolutePath());
        assertThat(Files.exists(storedFile)).isTrue();
        assertThat(Files.readAllBytes(storedFile)).isEqualTo(videoContent);

        // Verify metadata companion JSON file
        Path metaFile = Path.of(storedInfo.absolutePath() + ".meta.json");
        assertThat(Files.exists(metaFile)).isTrue();
        JsonNode metaJson = objectMapper.readTree(metaFile.toFile());
        assertThat(metaJson.get("jobId").asText()).isEqualTo(jobId.toString());
        assertThat(metaJson.get("prompt").asText()).isEqualTo(request.prompt());
        assertThat(metaJson.get("sha256").asText()).isEqualTo(storedInfo.sha256());

        // Verify loading back as resource
        Resource resource = storageService.loadVideoAsResource(storedInfo.fileName());
        assertThat(resource.exists()).isTrue();
        assertThat(resource.isReadable()).isTrue();
    }
}

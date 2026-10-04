package com.pipeline.videogen.storage;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.pipeline.videogen.config.ComfyUIProperties;
import com.pipeline.videogen.exception.StorageException;
import com.pipeline.videogen.model.GenerateVideoRequest;
import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.security.DigestInputStream;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.HexFormat;
import java.util.Map;
import java.util.UUID;

@Service
public class VideoStorageService {

    private static final Logger log = LoggerFactory.getLogger(VideoStorageService.class);

    private final Path storagePath;
    private final Path tempPath;
    private final ObjectMapper objectMapper;

    public VideoStorageService(ComfyUIProperties properties, ObjectMapper objectMapper) {
        this.storagePath = Paths.get(properties.storageDir()).toAbsolutePath().normalize();
        this.tempPath = Paths.get(properties.tempDir()).toAbsolutePath().normalize();
        this.objectMapper = objectMapper;
    }

    @PostConstruct
    public void init() {
        try {
            Files.createDirectories(storagePath);
            Files.createDirectories(tempPath);
            log.info("Initialized video storage directory at: {}", storagePath);
            log.info("Initialized temp storage directory at: {}", tempPath);
        } catch (IOException e) {
            throw new StorageException("Could not initialize video storage directories", e);
        }
    }

    /**
     * Atomically stores rendered video stream from ComfyUI with SHA-256 validation and metadata persistence.
     */
    public StoredVideoInfo storeRenderedVideo(UUID jobId,
                                             String originalFileName,
                                             InputStream videoStream,
                                             GenerateVideoRequest request) {
        String sanitizedName = sanitizeFilename(originalFileName);
        String finalFileName = jobId + "_" + sanitizedName;
        Path tempFile = tempPath.resolve("temp_" + finalFileName);
        Path targetFile = storagePath.resolve(finalFileName);

        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            try (DigestInputStream dis = new DigestInputStream(videoStream, digest)) {
                Files.copy(dis, tempFile, StandardCopyOption.REPLACE_EXISTING);
            }

            String sha256Hex = HexFormat.of().formatHex(digest.digest());
            long fileSize = Files.size(tempFile);

            // Atomic move to permanent storage
            try {
                Files.move(tempFile, targetFile, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
            } catch (IOException atomicMoveEx) {
                log.warn("Atomic move failed, falling back to standard replace: {}", atomicMoveEx.getMessage());
                Files.move(tempFile, targetFile, StandardCopyOption.REPLACE_EXISTING);
            }

            // Write metadata companion JSON file
            Path metaFile = storagePath.resolve(finalFileName + ".meta.json");
            Map<String, Object> metadata = Map.ofEntries(
                    Map.entry("jobId", jobId.toString()),
                    Map.entry("fileName", finalFileName),
                    Map.entry("fileSizeBytes", fileSize),
                    Map.entry("sha256", sha256Hex),
                    Map.entry("prompt", request.prompt()),
                    Map.entry("negativePrompt", request.negativePrompt()),
                    Map.entry("frames", request.frames()),
                    Map.entry("width", request.width()),
                    Map.entry("height", request.height()),
                    Map.entry("steps", request.steps()),
                    Map.entry("cfgScale", request.cfgScale()),
                    Map.entry("seed", request.seed()),
                    Map.entry("storedAt", Instant.now().toString())
            );
            objectMapper.writerWithDefaultPrettyPrinter().writeValue(metaFile.toFile(), metadata);

            log.info("Successfully stored video {} ({} bytes, sha256: {})", finalFileName, fileSize, sha256Hex);
            return new StoredVideoInfo(finalFileName, targetFile.toString(), fileSize, sha256Hex);

        } catch (NoSuchAlgorithmException | IOException e) {
            try {
                Files.deleteIfExists(tempFile);
            } catch (IOException ignored) {}
            throw new StorageException("Failed to store rendered video for job: " + jobId, e);
        }
    }

    public Resource loadVideoAsResource(String filename) {
        try {
            Path filePath = storagePath.resolve(filename).normalize();
            if (!filePath.startsWith(storagePath)) {
                throw new StorageException("Cannot access files outside storage directory");
            }
            Resource resource = new UrlResource(filePath.toUri());
            if (resource.exists() && resource.isReadable()) {
                return resource;
            } else {
                throw new StorageException("Video file not found or not readable: " + filename);
            }
        } catch (Exception e) {
            throw new StorageException("Error loading video resource: " + filename, e);
        }
    }

    private String sanitizeFilename(String filename) {
        if (filename == null || filename.isBlank()) {
            return "output.mp4";
        }
        return filename.replaceAll("[^a-zA-Z0-9._-]", "_");
    }

    public Path getStoragePath() {
        return storagePath;
    }

    public record StoredVideoInfo(String fileName, String absolutePath, long sizeBytes, String sha256) {}
}

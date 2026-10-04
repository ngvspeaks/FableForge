package com.pipeline.videogen.storage;

import com.pipeline.videogen.model.VideoJob;
import org.springframework.stereotype.Repository;

import java.util.Collection;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

@Repository
public class VideoJobRepository {

    private final ConcurrentHashMap<UUID, VideoJob> jobs = new ConcurrentHashMap<>();

    public VideoJob save(VideoJob job) {
        jobs.put(job.jobId(), job);
        return job;
    }

    public Optional<VideoJob> findById(UUID jobId) {
        return Optional.ofNullable(jobs.get(jobId));
    }

    public List<VideoJob> findAllRecent() {
        return jobs.values().stream()
                .sorted(Comparator.comparing(VideoJob::createdAt).reversed())
                .limit(50)
                .toList();
    }

    public Collection<VideoJob> values() {
        return jobs.values();
    }
}

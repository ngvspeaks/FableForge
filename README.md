# Automated Text-to-Video Pipeline (Spring Boot 23 & ComfyUI)

An automated, asynchronous text-to-video generation pipeline engineered with **Java 23**, **Spring Boot 3.4**, and a local **ComfyUI** endpoint.

---

## Architecture & Coordinated Modules

1. **Backend Integration (Agent 1)**:
   - Modern `RestClient` with `JdkClientHttpRequestFactory` for HTTP/2 and low-latency I/O.
   - Dynamic node graph payload injection via `WorkflowPayloadInjector`.
   - Asynchronous queue poller (`QueuePollerService`) running on Java 23 Virtual Threads.

2. **Architecture & Storage (Agent 2)**:
   - Java 23 `record` classes with Jakarta Bean Validation for robust input validation.
   - Global RFC 7807 `ProblemDetail` exception handling.
   - Atomic local file storage (`VideoStorageService`) with SHA-256 integrity validation and companion `.meta.json` persistence.
   - Glassmorphic, real-time dark mode trigger dashboard (`/index.html`).

3. **Testing Harness (Agent 3)**:
   - Comprehensive test suite leveraging **JUnit 5**, **AssertJ**, and **MockWebServer**.
   - Simulates ComfyUI `/prompt`, `/queue`, `/history`, and binary `/view` streaming with full end-to-end integration validation.

---

## Requirements

- **Java JDK 23** (`javac 23.0.1+`)
- **Maven Wrapper** (included: `mvnw.cmd` / `./mvnw`)
- Optional: Local **ComfyUI** server running at `http://localhost:8188`

---

## Quick Start

### 1. Run the Test Suite
```bash
.\mvnw.cmd test
```

### 2. Launch the Application
```bash
.\mvnw.cmd spring-boot:run
```

### 3. Open the Trigger Dashboard
Navigate to `http://localhost:8080/` in your browser to configure prompts, adjust diffusion sliders, launch generation runs, and preview rendered MP4 outputs.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/videos/generate` | Trigger video generation from prompt payload (HTTP 202) |
| `GET` | `/api/v1/videos/jobs/{jobId}` | Poll status of a specific generation job |
| `GET` | `/api/v1/videos/jobs` | Retrieve recent pipeline execution records |
| `GET` | `/api/v1/videos/stream/{filename}` | Stream stored MP4 video output |

package com.pipeline.videogen.client;

import com.pipeline.videogen.model.GenerateVideoRequest;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Component
public class WorkflowPayloadInjector {

    /**
     * Builds and injects prompt parameters into a ComfyUI node graph workflow.
     */
    public Map<String, Object> injectPromptWorkflow(GenerateVideoRequest request) {
        Map<String, Object> nodes = new HashMap<>();

        // Node 1: Model Loader
        nodes.put("1", Map.of(
                "class_type", "CheckpointLoaderSimple",
                "inputs", Map.of("ckpt_name", "v1-5-pruned-emaonly.safetensors")
        ));

        // Node 2: Positive Prompt
        nodes.put("2", Map.of(
                "class_type", "CLIPTextEncode",
                "inputs", Map.of(
                        "text", request.prompt(),
                        "clip", List.of("1", 1)
                )
        ));

        // Node 3: Negative Prompt
        nodes.put("3", Map.of(
                "class_type", "CLIPTextEncode",
                "inputs", Map.of(
                        "text", request.negativePrompt(),
                        "clip", List.of("1", 1)
                )
        ));

        // Node 4: Empty Latent Video / Batch
        nodes.put("4", Map.of(
                "class_type", "EmptyLatentImage",
                "inputs", Map.of(
                        "width", request.width(),
                        "height", request.height(),
                        "batch_size", request.frames()
                )
        ));

        // Node 5: KSampler
        nodes.put("5", Map.of(
                "class_type", "KSampler",
                "inputs", Map.of(
                        "seed", request.seed(),
                        "steps", request.steps(),
                        "cfg", request.cfgScale(),
                        "sampler_name", "euler",
                        "scheduler", "normal",
                        "denoise", 1.0,
                        "model", List.of("1", 0),
                        "positive", List.of("2", 0),
                        "negative", List.of("3", 0),
                        "latent_image", List.of("4", 0)
                )
        ));

        // Node 6: VAE Decode
        nodes.put("6", Map.of(
                "class_type", "VAEDecode",
                "inputs", Map.of(
                        "samples", List.of("5", 0),
                        "vae", List.of("1", 2)
                )
        ));

        // Node 7: Video Save / Combine Node (Output Node)
        nodes.put("7", Map.of(
                "class_type", "VHS_VideoCombine",
                "inputs", Map.of(
                        "images", List.of("6", 0),
                        "frame_rate", 16,
                        "loop_count", 0,
                        "filename_prefix", "video_gen",
                        "format", "video/h264-mp4",
                        "pingpong", false,
                        "save_output", true
                )
        ));

        return nodes;
    }
}

package com.pipeline.videogen.model;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record GenerateVideoRequest(
        @NotBlank(message = "Prompt cannot be blank")
        @Size(min = 3, max = 2000, message = "Prompt length must be between 3 and 2000 characters")
        String prompt,

        String negativePrompt,

        @Min(value = 8, message = "Minimum frame count is 8")
        @Max(value = 240, message = "Maximum frame count is 240")
        Integer frames,

        @Min(value = 256, message = "Minimum width is 256px")
        @Max(value = 1920, message = "Maximum width is 1920px")
        Integer width,

        @Min(value = 256, message = "Minimum height is 256px")
        @Max(value = 1080, message = "Maximum height is 1080px")
        Integer height,

        @Min(value = 10, message = "Minimum inference steps is 10")
        @Max(value = 100, message = "Maximum inference steps is 100")
        Integer steps,

        @Min(value = 1, message = "Minimum CFG scale is 1.0")
        @Max(value = 25, message = "Maximum CFG scale is 25.0")
        Double cfgScale,

        Long seed
) {
    public GenerateVideoRequest {
        if (negativePrompt == null) negativePrompt = "blurry, low quality, distorted, deformed, flickering, watermark, artifacts";
        if (frames == null) frames = 25;
        if (width == null) width = 512;
        if (height == null) height = 512;
        if (steps == null) steps = 25;
        if (cfgScale == null) cfgScale = 7.0;
        if (seed == null || seed < 0) seed = System.currentTimeMillis();
    }
}

"""
FableForge Local Motion Generator (ComfyUI SVD / LTX Pipeline)
Generates high-quality animated physical movement (spinning wheels, body motion, dynamic camera)
from static keyframe images locally on NVIDIA GeForce RTX 4050 GPU (Zero Paid Services, Unlimited).
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
import subprocess
from pathlib import Path

COMFY_HOST = "127.0.0.1"
COMFY_PORT = 8188
COMFY_URL = f"http://{COMFY_HOST}:{COMFY_PORT}"
COMFY_OUTPUT_DIR = Path(r"C:\Users\NIBIN G VARGHESE\ComfyUI_windows_portable\ComfyUI\output")

def check_comfy_running():
    """Verify ComfyUI is listening on the expected port."""
    try:
        req = urllib.request.Request(f"{COMFY_URL}/system_stats")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return True, data
    except Exception as e:
        return False, str(e)

def upload_image_to_comfy(image_path):
    """Upload input image to ComfyUI input folder via API."""
    import mimetypes
    image_path = Path(image_path).resolve()
    if not image_path.exists():
        raise FileNotFoundError(f"Input image not found: {image_path}")

    filename = image_path.name
    boundary = "----FableForgeBoundary" + str(int(time.time()))
    
    with open(image_path, "rb") as f:
        file_bytes = f.read()

    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'.encode())
    body.extend(b"Content-Type: image/jpeg\r\n\r\n")
    body.extend(file_bytes)
    body.extend(b"\r\n")
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(b'Content-Disposition: form-data; name="overwrite"\r\n\r\n')
    body.extend(b"true\r\n")
    body.extend(f"--{boundary}--\r\n".encode())

    req = urllib.request.Request(
        f"{COMFY_URL}/upload/image",
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read().decode('utf-8'))
        return result.get("name", filename)

def build_svd_workflow(image_filename, checkpoint_name="svd_fp8_e4m3fn.safetensors", 
                       width=1024, height=576, frames=25, motion_bucket_id=127, 
                       fps=12, steps=20, cfg=2.5):
    """Build the node execution graph for Stable Video Diffusion Image-to-Video."""
    workflow = {
        "1": {
            "class_type": "ImageOnlyCheckpointLoader",
            "inputs": {
                "ckpt_name": checkpoint_name
            }
        },
        "2": {
            "class_type": "LoadImage",
            "inputs": {
                "image": image_filename
            }
        },
        "3": {
            "class_type": "SVD_img2vid_Conditioning",
            "inputs": {
                "clip_vision": ["1", 1],
                "init_image": ["2", 0],
                "vae": ["1", 2],
                "width": width,
                "height": height,
                "video_frames": frames,
                "motion_bucket_id": motion_bucket_id,
                "fps": fps,
                "augmentation_level": 0.02
            }
        },
        "4": {
            "class_type": "VideoLinearCFGGuidance",
            "inputs": {
                "model": ["1", 0],
                "min_cfg": 1.0
            }
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["4", 0],
                "positive": ["3", 0],
                "negative": ["3", 1],
                "latent_image": ["3", 2],
                "seed": int(time.time() * 1000) % 1000000007,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "euler",
                "scheduler": "karras",
                "denoise": 1.0
            }
        },
        "6": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["5", 0],
                "vae": ["1", 2]
            }
        },
        "7": {
            "class_type": "SaveAnimatedWEBP",
            "inputs": {
                "images": ["6", 0],
                "filename_prefix": "fableforge_motion",
                "fps": fps,
                "lossless": False,
                "quality": 92,
                "method": "default"
            }
        }
    }
    return workflow

def queue_prompt(workflow):
    """Submit prompt graph to ComfyUI queue."""
    client_id = f"fableforge_{int(time.time())}"
    payload = json.dumps({"prompt": workflow, "client_id": client_id}).encode('utf-8')
    req = urllib.request.Request(
        f"{COMFY_URL}/prompt",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        return res.get("prompt_id")

def wait_for_completion(prompt_id, timeout=300):
    """Poll ComfyUI until prompt execution finishes and return output files."""
    start = time.time()
    print(f"[*] Waiting for ComfyUI execution (Prompt ID: {prompt_id})...")
    while time.time() - start < timeout:
        time.sleep(2)
        try:
            req = urllib.request.Request(f"{COMFY_URL}/history/{prompt_id}")
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if prompt_id in data:
                    item = data[prompt_id]
                    outputs = item.get("outputs", {})
                    # Look for node 7 or any animated output
                    for node_id, out_data in outputs.items():
                        if "images" in out_data:
                            images = out_data["images"]
                            if images:
                                filename = images[0].get("filename")
                                subfolder = images[0].get("subfolder", "")
                                if subfolder:
                                    out_path = COMFY_OUTPUT_DIR / subfolder / filename
                                else:
                                    out_path = COMFY_OUTPUT_DIR / filename
                                return out_path
                    return None
        except Exception as e:
            pass
    raise TimeoutError(f"ComfyUI prompt {prompt_id} timed out after {timeout} seconds")

def convert_webp_to_mp4(webp_path, output_mp4_path, source_fps=12, target_fps=24):
    """Convert animated WEBP to high-quality MP4 using PIL frame unpacker and FFmpeg rawvideo pipe."""
    from PIL import Image, ImageSequence
    output_mp4_path = Path(output_mp4_path).resolve()
    output_mp4_path.parent.mkdir(parents=True, exist_ok=True)
    
    im = Image.open(webp_path)
    frames = [f.convert('RGB') for f in ImageSequence.Iterator(im)]
    if not frames:
        raise ValueError(f"No frames found in animated file: {webp_path}")
    
    w, h = frames[0].size
    
    ffmpeg_exe = "ffmpeg"
    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    
    cmd = [
        ffmpeg_exe, "-y",
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", f"{w}x{h}",
        "-r", str(source_fps),
        "-i", "-",
        "-vf", f"fps={target_fps}",
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "slow",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output_mp4_path)
    ]
    
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    for f in frames:
        proc.stdin.write(f.tobytes())
    proc.stdin.close()
    proc.wait()
    
    if proc.returncode != 0:
        err = proc.stderr.read().decode('utf-8', errors='ignore')
        raise RuntimeError(f"FFmpeg encoding failed with code {proc.returncode}: {err}")
    
    return output_mp4_path

def generate_motion_clip(image_path, output_mp4_path, frames=25, motion_bucket=135, steps=20, fps=12):
    """End-to-end function: Image -> Upload -> SVD Motion -> WEBP -> High-bitrate MP4."""
    is_running, info = check_comfy_running()
    if not is_running:
        raise RuntimeError("ComfyUI server is not running on port 8188. Please start ComfyUI first.")
    
    print(f"[*] Uploading image: {image_path}")
    uploaded_name = upload_image_to_comfy(image_path)
    print(f"[+] Image uploaded as: {uploaded_name}")
    
    print(f"[*] Building SVD motion workflow ({frames} frames, motion={motion_bucket}, steps={steps})...")
    workflow = build_svd_workflow(
        image_filename=uploaded_name,
        checkpoint_name="svd_fp8_e4m3fn.safetensors",
        width=1024,
        height=576,
        frames=frames,
        motion_bucket_id=motion_bucket,
        fps=fps,
        steps=steps
    )
    
    prompt_id = queue_prompt(workflow)
    print(f"[+] Prompt queued with ID: {prompt_id}")
    
    webp_path = wait_for_completion(prompt_id)
    if not webp_path or not webp_path.exists():
        raise RuntimeError("Motion generation completed but output file was not found.")
    
    print(f"[+] ComfyUI generated raw motion: {webp_path}")
    print(f"[*] Converting to smooth 30fps MP4: {output_mp4_path}")
    mp4_path = convert_webp_to_mp4(webp_path, output_mp4_path, target_fps=30)
    print(f"[SUCCESS] Motion video created: {mp4_path}")
    return mp4_path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate realistic motion video from static keyframe image")
    parser.add_argument("--image", required=True, help="Input keyframe image path")
    parser.add_argument("--output", required=True, help="Target MP4 video path")
    parser.add_argument("--frames", type=int, default=25, help="Number of motion frames (14 to 25)")
    parser.add_argument("--motion", type=int, default=135, help="Motion intensity bucket (1 to 255, 127 is default)")
    parser.add_argument("--steps", type=int, default=20, help="Sampling steps")
    args = parser.parse_args()
    
    generate_motion_clip(args.image, args.output, frames=args.frames, motion_bucket=args.motion, steps=args.steps)

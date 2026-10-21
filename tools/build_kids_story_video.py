import os
import sys
import subprocess
import re
import cv2
import numpy as np
from gtts import gTTS
import imageio_ffmpeg

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
OUTPUT_DIR = r"C:\Users\NIBIN G VARGHESE\.gemini\antigravity-ide\brain\f0b4c784-9e2f-4f72-b00a-d8c7e473538e"
SCRATCH_DIR = os.path.join(OUTPUT_DIR, "story_production")
os.makedirs(SCRATCH_DIR, exist_ok=True)

SCENES = [
    {
        "id": 1,
        "title": "Scene 1: David the Shepherd Boy",
        "image": os.path.join(OUTPUT_DIR, "david_shepherd_hills_1792592324311.jpg"),
        "narration": "Long ago, in the green hills of Bethlehem, lived a young shepherd boy named David. He loved taking care of his sheep and had a heart full of courage.",
        "subtitles": [
            (0.0, 5.0, "Long ago, in the green hills of Bethlehem,"),
            (5.0, 8.5, "lived a young shepherd boy named David."),
            (8.5, 13.0, "He loved taking care of his sheep and had a heart full of courage.")
        ],
        "motion": "zoom_in"
    },
    {
        "id": 2,
        "title": "Scene 2: The Giant Goliath Appears",
        "image": os.path.join(OUTPUT_DIR, "giant_goliath_challenge_1792592344206.jpg"),
        "narration": "One day, a huge giant named Goliath challenged the soldiers in the valley. Goliath was as tall as a tree and wore heavy bronze armor! Everyone was terrified.",
        "subtitles": [
            (0.0, 5.2, "One day, a huge giant named Goliath challenged the soldiers."),
            (5.2, 9.8, "Goliath was tall as a tree and wore heavy bronze armor!"),
            (9.8, 13.5, "Everyone in the valley was terrified.")
        ],
        "motion": "pan_up"
    },
    {
        "id": 3,
        "title": "Scene 3: Five Smooth Stones",
        "image": os.path.join(OUTPUT_DIR, "david_five_stones_1792592392765.jpg"),
        "narration": "David was not afraid. He walked down to a sparkling brook and chose five smooth stones for his sling, trusting that courage comes from doing what is right.",
        "subtitles": [
            (0.0, 3.5, "David was not afraid."),
            (3.5, 8.2, "He walked down to a sparkling brook and chose five smooth stones,"),
            (8.2, 13.2, "trusting that courage comes from doing what is right.")
        ],
        "motion": "zoom_in"
    },
    {
        "id": 4,
        "title": "Scene 4: The Great Confrontation",
        "image": os.path.join(OUTPUT_DIR, "david_goliath_battle_1792592432673.jpg"),
        "narration": "With his sling in hand, young David stepped forward. He swung his leather sling with all his might, and the smooth stone flew straight and true!",
        "subtitles": [
            (0.0, 4.2, "With his sling in hand, young David stepped forward."),
            (4.2, 8.5, "He swung his leather sling with all his might,"),
            (8.5, 12.8, "and the smooth stone flew straight and true!")
        ],
        "motion": "pan_right"
    },
    {
        "id": 5,
        "title": "Scene 5: Joy and Victory",
        "image": os.path.join(OUTPUT_DIR, "david_victory_celebration_1792592470436.jpg"),
        "narration": "The giant was defeated! The entire village cheered with joy. Young David proved that no matter how small you are, big courage can overcome any giant!",
        "subtitles": [
            (0.0, 4.0, "The giant was defeated! The entire village cheered with joy."),
            (4.0, 8.5, "Young David proved that no matter how small you are,"),
            (8.5, 13.5, "big courage can overcome any giant!")
        ],
        "motion": "zoom_out"
    }
]

def get_audio_duration(audio_file):
    cmd = [FFMPEG_EXE, "-i", audio_file]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
    if match:
        h, m, s = match.groups()
        return int(h) * 3600 + int(m) * 60 + float(s)
    return 10.0

import asyncio
import edge_tts

VOICE = "en-US-ChristopherNeural"

def generate_scene_audio(scene):
    audio_path = os.path.join(SCRATCH_DIR, f"scene_{scene['id']}_narration.mp3")
    print(f"Generating Natural English Voiceover ({VOICE}) for Scene {scene['id']}...")
    
    async def _synth():
        communicate = edge_tts.Communicate(scene["narration"], VOICE, rate="-4%", pitch="+0Hz")
        await communicate.save(audio_path)
    
    asyncio.run(_synth())
    duration = get_audio_duration(audio_path)
    print(f"Scene {scene['id']} narration duration: {duration:.2f}s")
    return audio_path, duration

def apply_subtitles(frame, text, width, height):
    if not text:
        return frame
    
    # Text configuration
    font = cv2.FONT_HERSHEY_DUPLEX
    font_scale = 0.85
    thickness = 2
    
    (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    
    # Subtitle bar background
    pad_x = 24
    pad_y = 12
    box_w = text_w + pad_x * 2
    box_h = text_h + pad_y * 2
    box_x = (width - box_w) // 2
    box_y = height - 90
    
    # Draw semi-transparent dark rounded bar
    overlay = frame.copy()
    cv2.rectangle(overlay, (box_x, box_y), (box_x + box_w, box_y + box_h), (15, 15, 20), -1)
    cv2.rectangle(overlay, (box_x, box_y), (box_x + box_w, box_y + box_h), (255, 215, 0), 2) # Golden border
    alpha = 0.78
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    
    # Draw text with subtle shadow
    text_x = box_x + pad_x
    text_y = box_y + pad_y + text_h
    cv2.putText(frame, text, (text_x + 1, text_y + 1), font, font_scale, (0, 0, 0), thickness + 1, cv2.LINE_AA)
    cv2.putText(frame, text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
    return frame

def render_scene_video(scene, audio_path, audio_dur, fps=30, out_w=1280, out_h=720):
    # Total duration = audio duration + 1.2s padding
    scene_dur = audio_dur + 1.2
    num_frames = int(scene_dur * fps)
    
    raw_img = cv2.imread(scene["image"])
    if raw_img is None:
        raise FileNotFoundError(f"Could not load image: {scene['image']}")
    
    orig_h, orig_w = raw_img.shape[:2]
    
    raw_video_path = os.path.join(SCRATCH_DIR, f"scene_{scene['id']}_visual.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(raw_video_path, fourcc, fps, (out_w, out_h))
    
    print(f"Rendering visual frames for Scene {scene['id']} ({num_frames} frames)...")
    
    motion = scene.get("motion", "zoom_in")
    
    for i in range(num_frames):
        t = i / float(num_frames) # 0.0 -> 1.0
        current_time = i / float(fps)
        
        # Ken Burns motion calculation
        if motion == "zoom_in":
            # Scale from 1.0 to 1.10
            scale = 1.0 + 0.10 * t
            crop_w = int(orig_w / scale)
            crop_h = int(orig_h / scale)
            cx, cy = orig_w // 2, orig_h // 2
            x1 = max(0, cx - crop_w // 2)
            y1 = max(0, cy - crop_h // 2)
        elif motion == "zoom_out":
            scale = 1.10 - 0.10 * t
            crop_w = int(orig_w / scale)
            crop_h = int(orig_h / scale)
            cx, cy = orig_w // 2, orig_h // 2
            x1 = max(0, cx - crop_w // 2)
            y1 = max(0, cy - crop_h // 2)
        elif motion == "pan_right":
            # Scale 1.08, pan x from 0 to max_shift
            scale = 1.08
            crop_w = int(orig_w / scale)
            crop_h = int(orig_h / scale)
            max_shift_x = orig_w - crop_w
            x1 = int(max_shift_x * t)
            y1 = (orig_h - crop_h) // 2
        elif motion == "pan_up":
            scale = 1.08
            crop_w = int(orig_w / scale)
            crop_h = int(orig_h / scale)
            max_shift_y = orig_h - crop_h
            x1 = (orig_w - crop_w) // 2
            y1 = int(max_shift_y * (1.0 - t))
        else:
            x1, y1 = 0, 0
            crop_w, crop_h = orig_w, orig_h
        
        x2 = min(orig_w, x1 + crop_w)
        y2 = min(orig_h, y1 + crop_h)
        cropped = raw_img[y1:y2, x1:x2]
        frame = cv2.resize(cropped, (out_w, out_h), interpolation=cv2.INTER_LINEAR)
        
        # Find active subtitle
        current_sub = ""
        # Adjust subtitle timestamps relative to audio duration
        time_ratio = audio_dur / 13.0
        for (sub_start, sub_end, sub_text) in scene["subtitles"]:
            actual_start = sub_start * time_ratio
            actual_end = sub_end * time_ratio
            if actual_start <= current_time <= actual_end:
                current_sub = sub_text
                break
        
        # Header Badge
        cv2.rectangle(frame, (25, 20), (380, 56), (15, 15, 25), -1)
        cv2.rectangle(frame, (25, 20), (380, 56), (255, 215, 0), 1)
        cv2.putText(frame, scene["title"].upper(), (35, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.46, (255, 220, 100), 1, cv2.LINE_AA)
        
        # Subtitle
        frame = apply_subtitles(frame, current_sub, out_w, out_h)
        
        # Fade-in at start (first 15 frames) & fade-out at end (last 15 frames)
        if i < 15:
            fade_alpha = i / 15.0
            frame = (frame * fade_alpha).astype(np.uint8)
        elif i > num_frames - 16:
            fade_alpha = (num_frames - 1 - i) / 15.0
            frame = (frame * fade_alpha).astype(np.uint8)
        
        out.write(frame)
    
    out.release()
    
    # Now mux visual video with narration audio using FFmpeg
    muxed_scene_path = os.path.join(SCRATCH_DIR, f"scene_{scene['id']}_final.mp4")
    # Pad audio with silence to match video duration
    ffmpeg_cmd = [
        FFMPEG_EXE, "-y",
        "-i", raw_video_path,
        "-i", audio_path,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        muxed_scene_path
    ]
    res = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FFmpeg mux error for scene {scene['id']}:", res.stderr)
        raise RuntimeError("FFmpeg muxing failed.")
    
    print(f"Scene {scene['id']} complete: {muxed_scene_path}")
    return muxed_scene_path

def main():
    scene_clips = []
    print("=== STARTING FULL DAVID & GOLIATH STORY PIPELINE ===")
    
    for scene in SCENES:
        audio_path, duration = generate_scene_audio(scene)
        scene_clip = render_scene_video(scene, audio_path, duration)
        scene_clips.append(scene_clip)
    
    # Concatenate all scenes into a final movie
    concat_list_path = os.path.join(SCRATCH_DIR, "concat_list.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for clip in scene_clips:
            # Escape path for ffmpeg concat demuxer
            safe_clip = clip.replace("\\", "/")
            f.write(f"file '{safe_clip}'\n")
    
    final_video_path = os.path.join(OUTPUT_DIR, "david_and_goliath_kids_story.mp4")
    print("\nConcatenating all scenes into final video...")
    
    concat_cmd = [
        FFMPEG_EXE, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_path,
        "-c", "copy",
        final_video_path
    ]
    res = subprocess.run(concat_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("FFmpeg concat error:", res.stderr)
        # Try re-encoding concat fallback
        print("Retrying concat with re-encoding...")
        concat_cmd = [
            FFMPEG_EXE, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list_path,
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            final_video_path
        ]
        res2 = subprocess.run(concat_cmd, capture_output=True, text=True)
        if res2.returncode != 0:
            raise RuntimeError(f"FFmpeg concat failed: {res2.stderr}")
    
    final_dur = get_audio_duration(final_video_path)
    final_size_mb = os.path.getsize(final_video_path) / (1024 * 1024)
    
    # Also copy to workspace root and static web resources
    import shutil
    ws_copy = r"c:\Users\NIBIN G VARGHESE\.gemini\antigravity-ide\scratch\text-to-video-pipeline\david_and_goliath_kids_story.mp4"
    static_copy = r"c:\Users\NIBIN G VARGHESE\.gemini\antigravity-ide\scratch\text-to-video-pipeline\src\main\resources\static\david_and_goliath_kids_story.mp4"
    shutil.copy2(final_video_path, ws_copy)
    shutil.copy2(final_video_path, static_copy)
    print(f"Copied to workspace: {ws_copy}")
    print(f"Copied to static web: {static_copy}")

    print(f"\nSUCCESS! Final video generated:")
    print(f"Path: {final_video_path}")
    print(f"Duration: {final_dur:.2f} seconds")
    print(f"File Size: {final_size_mb:.2f} MB")

if __name__ == "__main__":
    main()

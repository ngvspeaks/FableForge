# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import re
import asyncio
import cv2
import numpy as np
import edge_tts
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
OUTPUT_DIR = r"C:\Users\NIBIN G VARGHESE\.gemini\antigravity-ide\brain\f0b4c784-9e2f-4f72-b00a-d8c7e473538e"
SCRATCH_DIR = os.path.join(OUTPUT_DIR, "malayalam_production")
os.makedirs(SCRATCH_DIR, exist_ok=True)

# Microsoft Malayalam Neural Voice
VOICE = "ml-IN-MidhunNeural"
FONT_PATH = r"C:\Windows\Fonts\Nirmala.ttc"

SCENES = [
    {
        "id": 1,
        "title": "രംഗം 1: ദാവീദ് എന്ന ഇടയബാലൻ",
        "image": os.path.join(OUTPUT_DIR, "david_shepherd_hills_1792592324311.jpg"),
        "narration": "പണ്ട് പണ്ട്, ബെത്‌ലഹേമിലെ പച്ചപ്പുല്ലുള്ള മനോഹരമായ കുന്നുകളിൽ, ദാവീദ് എന്നൊരു കൊച്ചു ഇടയബാലൻ ജീവിച്ചിരുന്നു. അവൻ തന്റെ ആടുകളെ സ്നേഹത്തോടെ കാത്തുപരിപാലിക്കുകയും, ഉള്ളിൽ വലിയൊരു ധൈര്യം കാത്തുസൂക്ഷിക്കുകയും ചെയ്തു.",
        "subtitles": [
            (0.0, 5.0, "പണ്ട് പണ്ട്, ബെത്‌ലഹേമിലെ മനോഹരമായ കുന്നുകളിൽ,"),
            (5.0, 9.0, "ദാവീദ് എന്നൊരു കൊച്ചു ഇടയബാലൻ ജീവിച്ചിരുന്നു."),
            (9.0, 14.5, "അവൻ സ്നേഹത്തോടെ ആടുകളെ പരിപാലിച്ചു, വലിയൊരു ധൈര്യം കാത്തുസൂക്ഷിച്ചു.")
        ],
        "motion": "zoom_in"
    },
    {
        "id": 2,
        "title": "രംഗം 2: ഭീമനായ ഗോലിയാത്ത്",
        "image": os.path.join(OUTPUT_DIR, "giant_goliath_challenge_1792592344206.jpg"),
        "narration": "അങ്ങനെയിരിക്കെ ഒരു ദിവസം, താഴ്‌വരയിൽ ഗോലിയാത്ത് എന്നൊരു ഭീമാകാരനായ യോദ്ധാവ് പ്രത്യക്ഷപ്പെട്ടു. വെങ്കല പടച്ചട്ടയണിഞ്ഞ ആ ഭീമനെ കണ്ട് സൈനികരെല്ലാം ഭയന്നുവിറച്ചു. അവൻ എല്ലാവരെയും പോരാട്ടത്തിനായി വെല്ലുവിളിച്ചു.",
        "subtitles": [
            (0.0, 5.0, "ഒരു ദിവസം, താഴ്‌വരയിൽ ഗോലിയാത്ത് എന്ന ഭീമൻ പ്രത്യക്ഷപ്പെട്ടു."),
            (5.0, 9.5, "വെങ്കല പടച്ചട്ടയണിഞ്ഞ ആ ഭീമനെ കണ്ട് സൈനികർ ഭയന്നുവിറച്ചു."),
            (9.5, 14.0, "അവൻ എല്ലാവരെയും വെല്ലുവിളിച്ചു കൊണ്ടിരുന്നു.")
        ],
        "motion": "pan_up"
    },
    {
        "id": 3,
        "title": "രംഗം 3: അഞ്ച് മിനുസമുള്ള കല്ലുകൾ",
        "image": os.path.join(OUTPUT_DIR, "david_five_stones_1792592392765.jpg"),
        "narration": "എന്നാൽ ദാവീദ് ഒട്ടും ഭയന്നില്ല. അവൻ താഴ്‌വരയിലെ അരുവിയുടെ അരികിലേക്ക് നടന്നുപോയി, തന്റെ കവണയ്ക്കായി അഞ്ച് മിനുസമുള്ള ഉരുണ്ട കല്ലുകൾ തിരഞ്ഞെടുത്തു. ധൈര്യം വരുന്നത് സത്യത്തിൽ വിശ്വസിക്കുമ്പോഴാണെന്ന് അവനറിയാമായിരുന്നു.",
        "subtitles": [
            (0.0, 4.0, "എന്നാൽ ദാവീദ് ഒട്ടും ഭയന്നില്ല."),
            (4.0, 9.0, "അവൻ അരുവിയിൽ നിന്ന് അഞ്ച് മിനുസമുള്ള കല്ലുകൾ തിരഞ്ഞെടുത്തു."),
            (9.0, 14.5, "ധൈര്യം വരുന്നത് സത്യത്തിൽ വിശ്വസിക്കുമ്പോഴാണെന്ന് അവനറിയാമായിരുന്നു.")
        ],
        "motion": "zoom_in"
    },
    {
        "id": 4,
        "title": "രംഗം 4: മഹത്തായ പോരാട്ടം",
        "image": os.path.join(OUTPUT_DIR, "david_goliath_battle_1792592432673.jpg"),
        "narration": "കവണ കയ്യിലേന്തി ധീരനായ ദാവീദ് ഗോലിയാത്തിന് നേരെ ചുവടുവെച്ചു. ഗോലിയാത്ത് പരിഹസിച്ചു ചിരിച്ചെങ്കിലും, ദാവീദ് തന്റെ സർവ്വ ശക്തിയുമെടുത്ത് കവണ വീശി. ആ കല്ല് നേരെ ലക്ഷ്യത്തിലേക്ക് പാഞ്ഞുപോയി!",
        "subtitles": [
            (0.0, 4.5, "കവണ കയ്യിലേന്തി ദാവീദ് ഗോലിയാത്തിന് നേരെ മുന്നേറി."),
            (4.5, 9.0, "ദാവീദ് സർവ്വ ശക്തിയുമെടുത്ത് കവണ വീശി."),
            (9.0, 13.5, "ആ കല്ല് നേരെ ലക്ഷ്യത്തിലേക്ക് പാഞ്ഞുപോയി!")
        ],
        "motion": "pan_right"
    },
    {
        "id": 5,
        "title": "രംഗം 5: വിജയവും സന്തോഷവും",
        "image": os.path.join(OUTPUT_DIR, "david_victory_celebration_1792592470436.jpg"),
        "narration": "ഭീമനായ ഗോലിയാത്ത് നിലംപതിച്ചു! നാടൊട്ടുക്കും ജനങ്ങൾ സന്തോഷത്തോടെ ആർത്തുവിളിച്ചു. എത്ര ചെറിയ ആളാണെങ്കിലും, വലിയൊരു ധൈര്യമുണ്ടെങ്കിൽ ഏതൊരു പ്രതിസന്ധിയെയും കീഴടക്കാമെന്ന് കൊച്ചു ദാവീദ് തെളിയിച്ചു!",
        "subtitles": [
            (0.0, 4.5, "ഭീമനായ ഗോലിയാത്ത് നിലംപതിച്ചു! ജനങ്ങൾ സന്തോഷത്തോടെ ആർത്തുവിളിച്ചു."),
            (4.5, 9.0, "എത്ര ചെറിയ ആളാണെങ്കിലും, വലിയൊരു ധൈര്യമുണ്ടെങ്കിൽ,"),
            (9.0, 14.5, "ഏതൊരു പ്രതിസന്ധിയെയും കീഴടക്കാമെന്ന് ദാവീദ് തെളിയിച്ചു!")
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
    return 12.0

def generate_malayalam_audio(scene):
    audio_path = os.path.join(SCRATCH_DIR, f"scene_{scene['id']}_ml_narration.mp3")
    print(f"Generating Malayalam Neural Audio ({VOICE}) for Scene {scene['id']}...")
    
    async def _synth():
        comm = edge_tts.Communicate(scene["narration"], VOICE, rate="-2%")
        await comm.save(audio_path)
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(_synth())
    except RuntimeError:
        asyncio.run(_synth())
        
    duration = get_audio_duration(audio_path)
    print(f"Scene {scene['id']} Malayalam narration duration: {duration:.2f}s")
    return audio_path, duration

def apply_pillow_subtitles(cv2_frame, text, header_text, width, height):
    # Convert BGR (cv2) to RGB (PIL)
    rgb_img = cv2.cvtColor(cv2_frame, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb_img)
    draw = ImageDraw.Draw(pil_img, "RGBA")
    
    font_sub = ImageFont.truetype(FONT_PATH, 28)
    font_hdr = ImageFont.truetype(FONT_PATH, 20)
    
    # Header badge
    if header_text:
        hdr_bbox = font_hdr.getbbox(header_text)
        hdr_w = hdr_bbox[2] - hdr_bbox[0]
        hdr_h = hdr_bbox[3] - hdr_bbox[1]
        bx1, by1 = 25, 20
        bx2, by2 = bx1 + hdr_w + 30, by1 + hdr_h + 20
        draw.rounded_rectangle([bx1, by1, bx2, by2], radius=8, fill=(15, 15, 25, 220), outline=(255, 215, 0, 255), width=2)
        draw.text((bx1 + 15, by1 + 7), header_text, font=font_hdr, fill=(255, 225, 120))
    
    # Subtitle bar
    if text:
        bbox = font_sub.getbbox(text)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        
        pad_x, pad_y = 26, 14
        box_w = tw + pad_x * 2
        box_h = th + pad_y * 2
        box_x = (width - box_w) // 2
        box_y = height - 95
        
        draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h],
                               radius=12, fill=(15, 15, 20, 200), outline=(255, 215, 0, 240), width=2)
        
        # Shadow
        draw.text((box_x + pad_x + 1, box_y + pad_y + 1), text, font=font_sub, fill=(0, 0, 0, 255))
        # Text
        draw.text((box_x + pad_x, box_y + pad_y), text, font=font_sub, fill=(255, 255, 255, 255))
    
    # Convert back to cv2 BGR
    result_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    return result_bgr

def render_scene_video(scene, audio_path, audio_dur, fps=30, out_w=1280, out_h=720):
    scene_dur = audio_dur + 1.2
    num_frames = int(scene_dur * fps)
    
    raw_img = cv2.imread(scene["image"])
    if raw_img is None:
        raise FileNotFoundError(f"Could not load image: {scene['image']}")
    
    orig_h, orig_w = raw_img.shape[:2]
    
    raw_video_path = os.path.join(SCRATCH_DIR, f"scene_{scene['id']}_ml_visual.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(raw_video_path, fourcc, fps, (out_w, out_h))
    
    print(f"Rendering Malayalam visual frames for Scene {scene['id']} ({num_frames} frames)...")
    motion = scene.get("motion", "zoom_in")
    
    for i in range(num_frames):
        t = i / float(num_frames)
        current_time = i / float(fps)
        
        if motion == "zoom_in":
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
            scale = 1.08
            crop_w = int(orig_w / scale)
            crop_h = int(orig_h / scale)
            x1 = int((orig_w - crop_w) * t)
            y1 = (orig_h - crop_h) // 2
        elif motion == "pan_up":
            scale = 1.08
            crop_w = int(orig_w / scale)
            crop_h = int(orig_h / scale)
            x1 = (orig_w - crop_w) // 2
            y1 = int((orig_h - crop_h) * (1.0 - t))
        else:
            x1, y1 = 0, 0
            crop_w, crop_h = orig_w, orig_h
        
        x2 = min(orig_w, x1 + crop_w)
        y2 = min(orig_h, y1 + crop_h)
        cropped = raw_img[y1:y2, x1:x2]
        frame = cv2.resize(cropped, (out_w, out_h), interpolation=cv2.INTER_LINEAR)
        
        # Subtitle selection
        current_sub = ""
        time_ratio = audio_dur / 14.0
        for (sub_start, sub_end, sub_text) in scene["subtitles"]:
            actual_start = sub_start * time_ratio
            actual_end = sub_end * time_ratio
            if actual_start <= current_time <= actual_end:
                current_sub = sub_text
                break
        
        # Apply Pillow Unicode Malayalam rendering
        frame = apply_pillow_subtitles(frame, current_sub, scene["title"], out_w, out_h)
        
        # Fade-in and fade-out
        if i < 15:
            fade_alpha = i / 15.0
            frame = (frame * fade_alpha).astype(np.uint8)
        elif i > num_frames - 16:
            fade_alpha = (num_frames - 1 - i) / 15.0
            frame = (frame * fade_alpha).astype(np.uint8)
            
        out.write(frame)
        
    out.release()
    
    # Mux with Malayalam audio
    muxed_path = os.path.join(SCRATCH_DIR, f"scene_{scene['id']}_ml_final.mp4")
    ffmpeg_cmd = [
        FFMPEG_EXE, "-y",
        "-i", raw_video_path,
        "-i", audio_path,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        muxed_path
    ]
    res = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg mux failed: {res.stderr}")
        
    print(f"Malayalam Scene {scene['id']} complete: {muxed_path}")
    return muxed_path

def main():
    scene_clips = []
    print("=== STARTING FULL MALAYALAM DAVID & GOLIATH STORY PIPELINE ===")
    
    for scene in SCENES:
        audio_path, duration = generate_malayalam_audio(scene)
        scene_clip = render_scene_video(scene, audio_path, duration)
        scene_clips.append(scene_clip)
        
    concat_list_path = os.path.join(SCRATCH_DIR, "ml_concat_list.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for clip in scene_clips:
            safe_clip = clip.replace("\\", "/")
            f.write(f"file '{safe_clip}'\n")
            
    final_video_path = os.path.join(OUTPUT_DIR, "david_and_goliath_malayalam_story.mp4")
    print("\nConcatenating all Malayalam scenes into final video...")
    
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
            
    import shutil
    ws_copy = r"c:\Users\NIBIN G VARGHESE\.gemini\antigravity-ide\scratch\text-to-video-pipeline\david_and_goliath_malayalam_story.mp4"
    static_copy = r"c:\Users\NIBIN G VARGHESE\.gemini\antigravity-ide\scratch\text-to-video-pipeline\src\main\resources\static\david_and_goliath_malayalam_story.mp4"
    shutil.copy2(final_video_path, ws_copy)
    shutil.copy2(final_video_path, static_copy)
    print(f"Copied to workspace: {ws_copy}")
    print(f"Copied to static: {static_copy}")
    
    dur = get_audio_duration(final_video_path)
    size_mb = os.path.getsize(final_video_path) / (1024 * 1024)
    print(f"\nSUCCESS! Final Malayalam Video Generated:")
    print(f"Path: {final_video_path}")
    print(f"Duration: {dur:.2f} seconds")
    print(f"File Size: {size_mb:.2f} MB")

if __name__ == "__main__":
    main()

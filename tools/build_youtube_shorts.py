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
SCRATCH_DIR = os.path.join(OUTPUT_DIR, "shorts_production")
STATIC_DIR = r"c:\Users\NIBIN G VARGHESE\.gemini\antigravity-ide\scratch\text-to-video-pipeline\src\main\resources\static"
os.makedirs(SCRATCH_DIR, exist_ok=True)

FONT_EN = r"C:\Windows\Fonts\arial.ttf"
FONT_ML = r"C:\Windows\Fonts\Nirmala.ttc"

# High-impact fast hook for English Short (~30s)
EN_SHORT_SCENES = [
    {
        "id": 1,
        "image": os.path.join(OUTPUT_DIR, "giant_goliath_challenge_1792592344206.jpg"),
        "narration": "A giant warrior as tall as a tree challenged everyone in the valley, and all the soldiers ran away in fear!",
        "subtitle": "A giant warrior challenged the valley, and everyone ran in fear!",
        "title": "THE TERRIFYING GIANT"
    },
    {
        "id": 2,
        "image": os.path.join(OUTPUT_DIR, "david_goliath_battle_1792592432673.jpg"),
        "narration": "Only one young shepherd boy named David had the courage to step forward with nothing but a simple sling!",
        "subtitle": "Only young David had the courage to step forward!",
        "title": "DAVID'S BRAVE FAITH"
    },
    {
        "id": 3,
        "image": os.path.join(OUTPUT_DIR, "david_victory_celebration_1792592470436.jpg"),
        "narration": "The stone flew straight, the giant fell, and David proved: no matter how small you are, big courage can overcome any giant!",
        "subtitle": "No matter how small you are, big courage wins!",
        "title": "VICTORY & COURAGE"
    }
]

# Malayalam Short scenes (~35s)
ML_SHORT_SCENES = [
    {
        "id": 1,
        "image": os.path.join(OUTPUT_DIR, "giant_goliath_challenge_1792592344206.jpg"),
        "narration": "ഭീമാകാരനായ ഗോലിയാത്ത് എന്ന യോദ്ധാവിനെ കണ്ട് എല്ലാ സൈനികരും ഭയന്നോടി!",
        "subtitle": "ഭീമനായ ഗോലിയാത്തിനെ കണ്ട് എല്ലാവരും ഭയന്നോടി!",
        "title": "ഭീമനായ ഗോലിയാത്ത്"
    },
    {
        "id": 2,
        "image": os.path.join(OUTPUT_DIR, "david_goliath_battle_1792592432673.jpg"),
        "narration": "എന്നാൽ കൊച്ചു ഇടയബാലനായ ദാവീദ് തന്റെ കവണയുമായി ധൈര്യത്തോടെ മുന്നോട്ടു വന്നു!",
        "subtitle": "ദാവീദ് കവണയുമായി ധൈര്യത്തോടെ മുന്നോട്ടു വന്നു!",
        "title": "ദാവീദിന്റെ ധൈര്യം"
    },
    {
        "id": 3,
        "image": os.path.join(OUTPUT_DIR, "david_victory_celebration_1792592470436.jpg"),
        "narration": "ആ കല്ല് നേരെ പാഞ്ഞുപോയി, ഗോലിയാത്ത് നിലംപതിച്ചു! എത്ര ചെറിയ ആളാണെങ്കിലും ധൈര്യമുണ്ടെങ്കിൽ വിജയം ഉറപ്പ്!",
        "subtitle": "എത്ര ചെറിയ ആളാണെങ്കിലും ധൈര്യമുണ്ടെങ്കിൽ വിജയം ഉറപ്പ്!",
        "title": "വിജയവും ആഹ്ലാദവും"
    }
]

# German Short scenes (~22s)
DE_SHORT_SCENES = [
    {
        "id": 1,
        "image": os.path.join(OUTPUT_DIR, "giant_goliath_challenge_1792592344206.jpg"),
        "narration": "Ein riesiger Krieger namens Goliath forderte alle heraus, und die Soldaten flohen voller Angst!",
        "subtitle": "Der Riese Goliath forderte alle heraus – alle flohen voller Angst!",
        "title": "DER RIESE GOLIATH"
    },
    {
        "id": 2,
        "image": os.path.join(OUTPUT_DIR, "david_goliath_battle_1792592432673.jpg"),
        "narration": "Doch der junge Hirtenjunge David trat dem Riesen mit einer einfachen Schleuder furchtlos entgegen!",
        "subtitle": "Nur der junge David trat dem Riesen furchtlos entgegen!",
        "title": "DAVIDS GROSSER MUT"
    },
    {
        "id": 3,
        "image": os.path.join(OUTPUT_DIR, "david_victory_celebration_1792592470436.jpg"),
        "narration": "Der Stein traf, der Riese fiel, und David bewies: Mit großem Mut kannst du jeden Riesen besiegen!",
        "subtitle": "Mit großem Mut kannst du jeden Riesen besiegen!",
        "title": "SIEG UND FREUDE"
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

def build_vertical_frame(raw_img, progress, subtitle_text, title_text, lang="en", out_w=1080, out_h=1920):
    # 1. Background: Blurred and darkened full bleed
    h, w = raw_img.shape[:2]
    bg_resized = cv2.resize(raw_img, (out_w, out_h), interpolation=cv2.INTER_LINEAR)
    bg_blurred = cv2.GaussianBlur(bg_resized, (75, 75), 0)
    bg_dark = (bg_blurred * 0.45).astype(np.uint8)
    
    # 2. Foreground: Center focal view with dynamic slow zoom (1.0x to 1.12x)
    scale = 1.0 + 0.12 * progress
    crop_w = int(w / scale)
    crop_h = int(h / scale)
    cx, cy = w // 2, h // 2
    x1 = max(0, cx - crop_w // 2)
    y1 = max(0, cy - crop_h // 2)
    cropped = raw_img[y1:y1 + crop_h, x1:x1 + crop_w]
    
    # Target height for center cinematic 16:9 frame on vertical phone screen
    fg_w = out_w - 40
    fg_h = int(fg_w * (9 / 16))
    fg_resized = cv2.resize(cropped, (fg_w, fg_h), interpolation=cv2.INTER_LINEAR)
    
    # Paste center image
    center_y = (out_h - fg_h) // 2 - 50
    center_x = (out_w - fg_w) // 2
    
    # Add border and shadow to center image
    cv2.rectangle(bg_dark, (center_x - 4, center_y - 4), (center_x + fg_w + 4, center_y + fg_h + 4), (255, 215, 0), 3)
    bg_dark[center_y:center_y + fg_h, center_x:center_x + fg_w] = fg_resized
    
    # Convert to PIL for crisp typography & emoji/Unicode support
    rgb_img = cv2.cvtColor(bg_dark, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb_img)
    draw = ImageDraw.Draw(pil_img, "RGBA")
    
    font_file = FONT_ML if lang == "ml" else FONT_EN
    font_top = ImageFont.truetype(font_file, 40)
    font_sub = ImageFont.truetype(font_file, 38)
    font_cta = ImageFont.truetype(font_file, 34)
    
    # Top Header Banner
    header_w = 780
    header_h = 70
    hx = (out_w - header_w) // 2
    hy = center_y - 120
    draw.rounded_rectangle([hx, hy, hx + header_w, hy + header_h], radius=16, fill=(15, 15, 25, 230), outline=(255, 215, 0, 255), width=3)
    
    bbox_t = font_top.getbbox(title_text)
    tw = bbox_t[2] - bbox_t[0]
    th = bbox_t[3] - bbox_t[1]
    draw.text(((out_w - tw) // 2, hy + (header_h - th) // 2 - 4), title_text, font=font_top, fill=(255, 220, 100))
    
    # Subtitle Card (Below center video)
    if subtitle_text:
        bbox_s = font_sub.getbbox(subtitle_text)
        sw = bbox_s[2] - bbox_s[0]
        sh = bbox_s[3] - bbox_s[1]
        
        box_w = min(out_w - 60, sw + 60)
        box_h = sh + 40
        bx = (out_w - box_w) // 2
        by = center_y + fg_h + 50
        
        draw.rounded_rectangle([bx, by, bx + box_w, by + box_h], radius=16, fill=(10, 12, 18, 240), outline=(255, 215, 0, 255), width=2)
        draw.text(((out_w - sw) // 2 + 2, by + 18 + 2), subtitle_text, font=font_sub, fill=(0, 0, 0, 255))
        draw.text(((out_w - sw) // 2, by + 18), subtitle_text, font=font_sub, fill=(255, 255, 255, 255))
        
    # Bottom Call to Action (Directs to full story in Related Video)
    if lang == "en":
        cta_text = "👇 TAP 'RELATED VIDEO' FOR FULL STORY"
    elif lang == "ml":
        cta_text = "👇 പൂർണ്ണ കഥ കാണാൻ താഴെ ക്ലിക്ക് ചെയ്യുക"
    else:
        cta_text = "👇 KLICKE 'RELATED VIDEO' FÜR DEN GANZEN FILM"
    bbox_c = font_cta.getbbox(cta_text)
    cw = bbox_c[2] - bbox_c[0]
    ch = bbox_c[3] - bbox_c[1]
    
    cta_box_w = min(out_w - 80, cw + 60)
    cta_box_h = ch + 34
    cx_box = (out_w - cta_box_w) // 2
    cy_box = out_h - 220
    
    draw.rounded_rectangle([cx_box, cy_box, cx_box + cta_box_w, cy_box + cta_box_h],
                           radius=9999, fill=(245, 158, 11, 245), outline=(255, 255, 255, 255), width=2)
    draw.text(((out_w - cw) // 2, cy_box + 14), cta_text, font=font_cta, fill=(0, 0, 0, 255))
    
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def generate_short(lang="en"):
    if lang == "en":
        scenes = EN_SHORT_SCENES
        voice = "en-US-ChristopherNeural"
    elif lang == "ml":
        scenes = ML_SHORT_SCENES
        voice = "ml-IN-MidhunNeural"
    else:
        scenes = DE_SHORT_SCENES
        voice = "de-DE-ConradNeural"
    prefix = f"{lang}_short"
    
    print(f"\n=== GENERATING 9:16 YOUTUBE SHORT ({lang.upper()}) ===")
    clip_paths = []
    fps = 30
    
    for i, s in enumerate(scenes):
        audio_path = os.path.join(SCRATCH_DIR, f"{prefix}_audio_{i}.mp3")
        print(f"Generating audio for Short scene {i+1}...")
        
        async def _synth():
            comm = edge_tts.Communicate(s["narration"], voice, rate="+3%")
            await comm.save(audio_path)
            
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.run_until_complete(_synth())
        except RuntimeError:
            asyncio.run(_synth())
            
        dur = get_audio_duration(audio_path)
        scene_dur = dur + 0.8
        num_frames = int(scene_dur * fps)
        
        raw_img = cv2.imread(s["image"])
        raw_vid = os.path.join(SCRATCH_DIR, f"{prefix}_vid_{i}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(raw_vid, fourcc, fps, (1080, 1920))
        
        print(f"Rendering {num_frames} vertical frames for scene {i+1}...")
        for f in range(num_frames):
            prog = f / float(num_frames)
            frame = build_vertical_frame(raw_img, prog, s["subtitle"], s["title"], lang=lang, out_w=1080, out_h=1920)
            out.write(frame)
        out.release()
        
        muxed_clip = os.path.join(SCRATCH_DIR, f"{prefix}_muxed_{i}.mp4")
        cmd = [
            FFMPEG_EXE, "-y",
            "-i", raw_vid,
            "-i", audio_path,
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            muxed_clip
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg mux error: {res.stderr}")
        clip_paths.append(muxed_clip)
        
    # Concatenate short scenes
    concat_file = os.path.join(SCRATCH_DIR, f"{prefix}_concat.txt")
    with open(concat_file, "w", encoding="utf-8") as f:
        for c in clip_paths:
            f.write(f"file '{c.replace(chr(92), '/')}'\n")
            
    final_short = os.path.join(OUTPUT_DIR, f"david_and_goliath_{lang}_short.mp4")
    static_dest = os.path.join(STATIC_DIR, f"david_and_goliath_{lang}_short.mp4")
    
    concat_cmd = [
        FFMPEG_EXE, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        final_short
    ]
    subprocess.run(concat_cmd, check=True)
    
    import shutil
    shutil.copy2(final_short, static_dest)
    
    final_dur = get_audio_duration(final_short)
    final_size = os.path.getsize(final_short) / (1024 * 1024)
    print(f"\nSUCCESS! {lang.upper()} Short created:")
    print(f"Path: {static_dest}")
    print(f"Duration: {final_dur:.2f}s | Size: {final_size:.2f}MB")
    return static_dest

def main():
    generate_short("en")
    generate_short("ml")
    generate_short("de")

if __name__ == "__main__":
    main()

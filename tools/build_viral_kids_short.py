"""
FableForge Viral Kids Short Builder - "Racing With Jesus"
Produces high-retention 9:16 YouTube Shorts & 16:9 Masters with:
- Pixar 3D Motion Video Clips (SVD GPU Diffusion)
- Upbeat 125 BPM Praise Song Vocals (en-US-AnaNeural)
- Foley Sound Effects (Engine revs, speed whooshes, cheering)
- Bouncy Highlighted Subtitles & Viral Hook Header
"""

import os
import sys
import asyncio
import subprocess
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

BASE_DIR = Path(r"c:\Users\NIBIN G VARGHESE\.gemini\antigravity-ide\scratch\text-to-video-pipeline")
KIDS_DIR = BASE_DIR / "storage" / "kids_race"
IMAGES_DIR = KIDS_DIR / "images"
VIDEO_DIR = KIDS_DIR / "video_clips"
AUDIO_DIR = KIDS_DIR / "audio"
SHORTS_DIR = KIDS_DIR / "shorts"

for d in [IMAGES_DIR, VIDEO_DIR, AUDIO_DIR, SHORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def get_ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"

FFMPEG = get_ffmpeg()

LANG_CONFIG = {
    "en": {
        "voice": "en-US-AnaNeural",
        "badge": "✨ BIBLE JOY KIDS ✨",
        "title": "RACING WITH JESUS!",
        "out_name": "racing_with_jesus_short_en_9x16.mp4",
        "scenes": [
            {
                "id": "scene_1",
                "duration": 7.0,
                "image": IMAGES_DIR / "scene_1_start.jpg",
                "video": VIDEO_DIR / "scene_1_motion.mp4",
                "lyrics": "Buckle up, turn the key! Jesus is right here with me!",
                "subs": [
                    ("Buckle up, turn the key!", 0.5, 3.8, "0xFFFFFF"),
                    ("Jesus is right here with me!", 3.8, 7.0, "0x00FFFF")
                ]
            },
            {
                "id": "scene_2",
                "duration": 7.5,
                "image": IMAGES_DIR / "scene_2_cruise.jpg",
                "video": VIDEO_DIR / "scene_2_motion.mp4",
                "lyrics": "Zooming fast, we have no fear! He is our Champion loud and clear!",
                "subs": [
                    ("Zooming fast, we have no fear!", 7.2, 10.8, "0xFFFFFF"),
                    ("He is our Champion loud and clear!", 10.8, 14.5, "0xFFDD00")
                ]
            },
            {
                "id": "scene_3",
                "duration": 7.5,
                "image": IMAGES_DIR / "scene_3_victory.jpg",
                "video": VIDEO_DIR / "scene_3_motion.mp4",
                "lyrics": "Through the race and down the track, Jesus' love will bring us back! YAY!",
                "subs": [
                    ("Through the race and down the track!", 14.8, 18.4, "0xFFFFFF"),
                    ("Jesus love will bring us back!", 18.4, 20.8, "0x00FF88"),
                    ("YAY!", 20.8, 22.0, "0xFFCC00")
                ]
            }
        ]
    },
    "de": {
        "voice": "de-DE-AmalaNeural",
        "badge": "✨ BIBEL FREUDE KIDS ✨",
        "title": "RENNEN MIT JESUS!",
        "out_name": "racing_with_jesus_short_de_9x16.mp4",
        "scenes": [
            {
                "id": "scene_1",
                "duration": 7.0,
                "image": IMAGES_DIR / "scene_1_start.jpg",
                "video": VIDEO_DIR / "scene_1_motion.mp4",
                "lyrics": "Anschnallen, Schlüssel drehn! Jesus wird zur Seite stehn!",
                "subs": [
                    ("Anschnallen, Schlüssel drehn!", 0.5, 3.8, "0xFFFFFF"),
                    ("Jesus wird zur Seite stehn!", 3.8, 7.0, "0x00FFFF")
                ]
            },
            {
                "id": "scene_2",
                "duration": 7.5,
                "image": IMAGES_DIR / "scene_2_cruise.jpg",
                "video": VIDEO_DIR / "scene_2_motion.mp4",
                "lyrics": "Schnell wie der Wind, kein' Angst mehr, Jesus ist Sieger und unser Herr!",
                "subs": [
                    ("Schnell wie der Wind, kein' Angst mehr!", 7.2, 10.8, "0xFFFFFF"),
                    ("Jesus ist Sieger und unser Herr!", 10.8, 14.5, "0xFFDD00")
                ]
            },
            {
                "id": "scene_3",
                "duration": 7.5,
                "image": IMAGES_DIR / "scene_3_victory.jpg",
                "video": VIDEO_DIR / "scene_3_motion.mp4",
                "lyrics": "Durch das Rennen, über die Bahn, Jesus' Liebe führt uns voran! JUHU!",
                "subs": [
                    ("Durch das Rennen, über die Bahn!", 14.8, 18.4, "0xFFFFFF"),
                    ("Jesus Liebe führt uns voran!", 18.4, 20.8, "0x00FF88"),
                    ("JUHU!", 20.8, 22.0, "0xFFCC00")
                ]
            }
        ]
    }
}

TOTAL_DURATION = 22.0

async def generate_vocals(lang="en"):
    """Synthesize enthusiastic child vocals using edge-tts."""
    import edge_tts
    cfg = LANG_CONFIG.get(lang, LANG_CONFIG["en"])
    print(f"[*] Generating energetic child vocal tracks ({lang.upper()}) using {cfg['voice']}...")
    
    for scene in cfg["scenes"]:
        out_vocal = AUDIO_DIR / f"{scene['id']}_vocal_{lang}.mp3"
        communicate = edge_tts.Communicate(
            text=scene["lyrics"],
            voice=cfg["voice"],
            rate="+16%",
            pitch="+14Hz"
        )
        await communicate.save(str(out_vocal))
        print(f" [+] Vocal generated: {out_vocal.name}")

def generate_upbeat_backing_track(total_sec=22.0, sr=44100):
    """Synthesize an upbeat 125 BPM cheerful acoustic/pop kids backing track with Foley SFX."""
    print("[*] Synthesizing upbeat 125 BPM rhythm & Foley sound effects...")
    t = np.linspace(0, total_sec, int(sr * total_sec), endpoint=False)
    bpm = 125.0
    beat_sec = 60.0 / bpm
    total_beats = int(total_sec / beat_sec)
    
    audio = np.zeros_like(t)
    
    # 1. Cheerful Chord Progression (C - G - Am - F) in Synth Marimba / Bells
    # C major (261.63, 329.63, 392.00), G (196.00, 246.94, 293.66), Am (220.00, 261.63, 329.63), F (174.61, 220.00, 261.63)
    chords = [
        [261.63, 329.63, 392.00, 523.25], # C
        [196.00, 246.94, 293.66, 392.00], # G
        [220.00, 261.63, 329.63, 440.00], # Am
        [174.61, 220.00, 261.63, 349.23]  # F
    ]
    
    # Arpeggiate chords on 8th notes (0.5 beat)
    for beat_idx in range(total_beats * 2):
        t_start = beat_idx * (beat_sec / 2)
        idx_start = int(t_start * sr)
        chord = chords[(beat_idx // 8) % len(chords)]
        freq = chord[beat_idx % len(chord)]
        
        note_len = int(0.22 * sr)
        if idx_start + note_len < len(audio):
            t_note = np.linspace(0, 0.22, note_len)
            env = np.exp(-t_note * 12)
            wave = 0.15 * np.sin(2 * np.pi * freq * t_note) + 0.08 * np.sin(4 * np.pi * freq * t_note)
            audio[idx_start:idx_start+note_len] += wave * env

    # 2. Four-on-the-floor Kick Drum + Handclaps on 2 and 4
    for b in range(total_beats):
        t_b = b * beat_sec
        idx = int(t_b * sr)
        
        # Kick (thump)
        kick_len = int(0.12 * sr)
        if idx + kick_len < len(audio):
            tk = np.linspace(0, 0.12, kick_len)
            kick_freq = 140 * np.exp(-tk * 35) + 45
            kick_wave = 0.35 * np.sin(2 * np.pi * kick_freq * tk) * np.exp(-tk * 20)
            audio[idx:idx+kick_len] += kick_wave
            
        # Handclap on beats 2 and 4 (b % 4 == 1 or 3)
        if b % 2 == 1:
            clap_len = int(0.15 * sr)
            if idx + clap_len < len(audio):
                noise = (np.random.rand(clap_len) - 0.5) * 0.22
                env_clap = np.exp(-np.linspace(0, 0.15, clap_len) * 25)
                audio[idx:idx+clap_len] += noise * env_clap

    # 3. Foley Effects (Engine Revs at start, turbo whoosh in mid, celebration shimmer at end)
    # Engine Rev at 0.0s to 3.5s
    rev_samples = int(3.5 * sr)
    t_rev = np.linspace(0, 3.5, rev_samples)
    rpm = 50 + 90 * (t_rev / 3.5)**2
    engine_rumble = 0.18 * (np.sin(2 * np.pi * rpm * t_rev) + 0.5 * np.sin(4 * np.pi * rpm * t_rev))
    engine_noise = 0.08 * (np.random.rand(rev_samples) - 0.5) * (t_rev / 3.5)
    audio[:rev_samples] += (engine_rumble + engine_noise) * np.linspace(0.8, 0.2, rev_samples)

    # Turbo whoosh at 7.0s to 9.5s
    whoosh_start = int(7.0 * sr)
    whoosh_len = int(2.5 * sr)
    if whoosh_start + whoosh_len < len(audio):
        t_w = np.linspace(0, 2.5, whoosh_len)
        w_noise = (np.random.rand(whoosh_len) - 0.5) * 0.18 * np.sin(np.pi * t_w / 2.5)
        audio[whoosh_start:whoosh_start+whoosh_len] += w_noise

    # Victory Shimmer / Chimes at 15.0s to 22.0s
    vic_start = int(15.0 * sr)
    if vic_start < len(audio):
        t_vic = np.linspace(0, total_sec - 15.0, len(audio) - vic_start)
        chimes = 0.12 * np.sin(2 * np.pi * 1046.50 * t_vic) * np.sin(2 * np.pi * 5 * t_vic)
        audio[vic_start:] += chimes

    # Master Limiter
    max_val = np.max(np.abs(audio))
    if max_val > 0.95:
        audio = audio / max_val * 0.95
        
    out_backing = AUDIO_DIR / "kids_race_backing.wav"
    import wave
    with wave.open(str(out_backing), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        int_data = (audio * 32767).astype(np.int16)
        wf.writeframes(int_data.tobytes())
        
    print(f"[+] Backing track saved: {out_backing}")
    return out_backing

def build_master_audio(lang="en"):
    """Mix vocals and backing track with scene timeline ducking."""
    out_master_audio = AUDIO_DIR / f"master_soundtrack_{lang}.mp3"
    
    # We will assemble an ffmpeg complex filter mixing backing + vocals at precise start times
    vocal_1 = AUDIO_DIR / f"scene_1_vocal_{lang}.mp3"
    vocal_2 = AUDIO_DIR / f"scene_2_vocal_{lang}.mp3"
    vocal_3 = AUDIO_DIR / f"scene_3_vocal_{lang}.mp3"
    backing = AUDIO_DIR / "kids_race_backing.wav"
    
    cmd = [
        FFMPEG, "-y",
        "-i", str(backing),
        "-i", str(vocal_1),
        "-i", str(vocal_2),
        "-i", str(vocal_3),
        "-filter_complex",
        "[1:a]adelay=500|500,volume=1.4[v1];"
        "[2:a]adelay=7200|7200,volume=1.4[v2];"
        "[3:a]adelay=14800|14800,volume=1.4[v3];"
        "[0:a]volume=0.85[bkg];"
        "[bkg][v1][v2][v3]amix=inputs=4:duration=first:dropout_transition=2[outa]",
        "-map", "[outa]",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        str(out_master_audio)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[+] Master soundtrack mixed ({lang}): {out_master_audio}")
    return out_master_audio

def build_scene_clip(scene, target_w=1080, target_h=1920):
    """
    Prepare a scene video segment formatted for 9:16 vertical Short.
    If motion video exists, use it with gentle looping/speed; otherwise, smooth Ken Burns zoom on keyframe.
    """
    out_segment = VIDEO_DIR / f"{scene['id']}_segment_9x16.mp4"
    duration = scene["duration"]
    
    if scene["video"].exists():
        input_args = ["-stream_loop", "-1", "-i", str(scene["video"])]
        vf = (
            f"[0:v]split[bg][fg];"
            f"[bg]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h},boxblur=25:5[bgblur];"
            f"[fg]scale={target_w}:-1[fgscaled];"
            f"[bgblur][fgscaled]overlay=(W-w)/2:(H-h)/2[base]"
        )
    else:
        input_args = ["-loop", "1", "-i", str(scene["image"])]
        vf = (
            f"[0:v]scale={target_w*2}:-1,"
            f"zoompan=z='min(zoom+0.0015,1.25)':d={int(duration*30)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={target_w}x{target_h}[base]"
        )
        
    cmd = [
        FFMPEG, "-y",
        *input_args,
        "-filter_complex", vf,
        "-map", "[base]",
        "-t", str(duration),
        "-r", "30",
        "-c:v", "libx264",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        str(out_segment)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[+] Scene segment ready: {out_segment.name}")
    return out_segment

def build_full_short(segments, master_audio, lang="en"):
    """Concatenate segments, overlay viral header and dynamic animated subtitles, and mux audio."""
    cfg = LANG_CONFIG.get(lang, LANG_CONFIG["en"])
    out_short = SHORTS_DIR / cfg["out_name"]
    concat_list = VIDEO_DIR / "concat_list.txt"
    with open(concat_list, "w") as f:
        for s in segments:
            f.write(f"file '{s.name}'\n")

    raw_concat = VIDEO_DIR / "raw_concat.mp4"
    subprocess.run([
        FFMPEG, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(raw_concat)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    drawtext_filters = [
        f"drawtext=text='{cfg['badge']}':x=(w-text_w)/2:y=180:fontsize=38:fontcolor=white:box=1:boxcolor=0x000000AA:boxborderw=14",
        f"drawtext=text='{cfg['title']}':x=(w-text_w)/2:y=260:fontsize=68:fontcolor=0xFFDD00:borderw=5:bordercolor=black"
    ]
    
    # Subtitles per scene
    for sc in cfg["scenes"]:
        for text, t_start, t_end, color in sc["subs"]:
            escaped = text.replace("'", "")
            drawtext_filters.append(
                f"drawtext=text='{escaped}':enable='between(t,{t_start},{t_end})':x=(w-text_w)/2:y=1550:fontsize=62:fontcolor={color}:borderw=6:bordercolor=black"
            )
            
    vf = ",".join(drawtext_filters)
    
    cmd = [
        FFMPEG, "-y",
        "-i", str(raw_concat),
        "-i", str(master_audio),
        "-filter_complex", f"[0:v]{vf}[outv]",
        "-map", "[outv]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "slow",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(out_short)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[SUCCESS] Viral YouTube Short ({lang.upper()}) Exported: {out_short}")
    return out_short

async def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", default="de", choices=["en", "de"], help="Language code (en or de)")
    args = parser.parse_args()
    
    lang = args.lang
    print("="*60)
    print(f"🎬 STARTING VIRAL KIDS SHORT PRODUCTION ({lang.upper()}): 'RACING WITH JESUS'")
    print("="*60)
    
    cfg = LANG_CONFIG.get(lang, LANG_CONFIG["en"])
    
    # 1. Generate vocals
    await generate_vocals(lang=lang)
    
    # 2. Synthesize backing track & SFX (if not already synthesized)
    backing_file = AUDIO_DIR / "kids_race_backing.wav"
    if not backing_file.exists():
        generate_upbeat_backing_track(total_sec=TOTAL_DURATION)
    
    # 3. Mix master soundtrack
    master_audio = build_master_audio(lang=lang)
    
    # 4. Build video segments
    print("[*] Assembling 9:16 vertical motion video segments...")
    segments = []
    for s in cfg["scenes"]:
        seg = build_scene_clip(s)
        segments.append(seg)
        
    # 5. Concatenate and add viral styling
    print(f"[*] Rendering final YouTube Short ({lang.upper()}) with bouncy karaoke subtitles...")
    final_short = build_full_short(segments, master_audio, lang=lang)
    
    print("="*60)
    print(f"🎉 MASTER SHORT ({lang.upper()}) READY AT: {final_short}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())

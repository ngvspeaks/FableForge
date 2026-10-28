# -*- coding: utf-8 -*-
"""
FableForge - 6-Language Viral YouTube Shorts / Reels Generator for Samson
Produces high-impact 9:16 vertical videos (720x1280, 24fps) featuring:
- Ambient blurred background + 16:9 gold-bordered cinematic center frame
- Fast dynamic zoom / motion
- Emotional voiceover with SFX (lion roar, shears, temple collapse)
- High-visibility top badge, center subtitle card, and bottom CTA
- Generates POSTING_MANIFEST.md with copy-paste titles, descriptions, and hashtags for all 6 languages
"""

import os
import sys
import subprocess
import asyncio
import wave
import cv2
import numpy as np
import edge_tts
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_DIR = os.path.join(BASE_DIR, "storage", "samson")
IMAGES_DIR = os.path.join(STORAGE_DIR, "images")
SHORTS_DIR = os.path.join(STORAGE_DIR, "shorts")
os.makedirs(SHORTS_DIR, exist_ok=True)

INDIC_FONT_PATH = r"C:\Windows\Fonts\Nirmala.ttc"
EURO_FONT_PATH = r"C:\Windows\Fonts\segoeui.ttf"

IMG_LION = os.path.join(IMAGES_DIR, "samson_lion_battle_1793120775287.jpg")
IMG_DELILAH = os.path.join(IMAGES_DIR, "delilah_betrayal_samson_1793120823545.jpg")
IMG_TEMPLE = os.path.join(IMAGES_DIR, "samson_temple_dagon_1793120884719.jpg")

SHORTS_CONFIG = {
    "en": {
        "name": "English",
        "voice": "en-US-ChristopherNeural",
        "font": EURO_FONT_PATH,
        "cta": "👇 WATCH FULL 4K STORY IN RELATED VIDEO",
        "title_post": "He fought a LION with his bare hands! 🦁 Samson's Epic Strength",
        "caption": "From wrestling lions to collapsing a massive temple with his bare hands! Witness the legend of Samson. Full cinematic movie on our channel! 🔥 #Samson #BibleStories #Shorts #Animation",
        "scenes": [
            {
                "id": 1,
                "badge": "🦁 SUPERHUMAN POWER",
                "image": IMG_LION,
                "narration": "He fought a roaring lion with his bare hands, tearing it apart with divine power!",
                "subtitle": "He fought a roaring lion with his bare hands!",
                "rate": "+5%", "pitch": "+1Hz"
            },
            {
                "id": 2,
                "badge": "✂️ THE DEADLY BETRAYAL",
                "image": IMG_DELILAH,
                "narration": "Until a deadly secret was whispered in the dark, and his sacred strength was stolen...",
                "subtitle": "Until his sacred strength was stolen...",
                "rate": "-12%", "pitch": "-2Hz"
            },
            {
                "id": 3,
                "badge": "💥 THE FINAL STAND",
                "image": IMG_TEMPLE,
                "narration": "Blinded and bound in chains, he called on God one last time and collapsed the colossal temple!",
                "subtitle": "He pushed the pillars and collapsed the temple!",
                "rate": "-2%", "pitch": "-1Hz"
            }
        ]
    },
    "ml": {
        "name": "Malayalam",
        "voice": "ml-IN-MidhunNeural",
        "font": INDIC_FONT_PATH,
        "cta": "👇 പൂർണ്ണ കഥ കാണാൻ താഴെ ക്ലിക്ക് ചെയ്യുക",
        "title_post": "വെറുംകൈകൊണ്ട് സിംഹത്തെ കീറിമുറിച്ച വീരൻ! 🦁 ശിംശോൻ",
        "caption": "വെറുംകൈകൊണ്ട് സിംഹത്തെ കീറിമുറിച്ച അജയ്യനായ ശിംശോന്റെയും, ദെലീലയുടെ വഞ്ചനയുടെയും ഇതിഹാസ കഥ! പൂർണ്ണ കഥ ചാനലിൽ കാണുക. #Samson #MalayalamStories #Shorts",
        "scenes": [
            {
                "id": 1,
                "badge": "🦁 അജയ്യനായ വീരൻ",
                "image": IMG_LION,
                "narration": "വെറുംകൈകളോടെ അലറിപ്പാഞ്ഞ സിംഹത്തെ കീറിമുറിച്ചവൻ; ദൈവത്തിന്റെ സ്വന്തം വീരൻ ശിംശോൻ!",
                "subtitle": "വെറുംകൈകളോടെ സിംഹത്തെ കീറിമുറിച്ച വീരൻ!",
                "rate": "+5%", "pitch": "+1Hz"
            },
            {
                "id": 2,
                "badge": "✂️ ദെലീലയുടെ വഞ്ചന",
                "image": IMG_DELILAH,
                "narration": "എന്നാൽ ഒരു രാത്രിയിൽ, പ്രണയം വഞ്ചനയായി മാറി; അവന്റെ ദിവ്യശക്തി അപഹരിക്കപ്പെട്ടു...",
                "subtitle": "പ്രണയം വഞ്ചനയായി, ശക്തി അപഹരിക്കപ്പെട്ടു...",
                "rate": "-12%", "pitch": "-2Hz"
            },
            {
                "id": 3,
                "badge": "💥 അന്തിമ വിജയം",
                "image": IMG_TEMPLE,
                "narration": "ബന്ധനസ്ഥനായ അവൻ ഉള്ളുരുകി പ്രാർത്ഥിച്ചു; തൂണുകൾ തകർത്ത് മഹാക്ഷേത്രം നിലംപൊത്തിച്ചു!",
                "subtitle": "തൂണുകൾ തകർത്ത് ക്ഷേത്രം നിലംപൊത്തിച്ചു!",
                "rate": "-2%", "pitch": "-1Hz"
            }
        ]
    },
    "hi": {
        "name": "Hindi",
        "voice": "hi-IN-MadhurNeural",
        "font": INDIC_FONT_PATH,
        "cta": "👇 पूरी कहानी देखने के लिए नीचे क्लिक करें",
        "title_post": "खाली हाथों से शेर को चीर डाला! 🦁 शिमशोन की असीम शक्ति",
        "caption": "खाली हाथों से शेर को परास्त करने वाले सबसे शक्तिशाली योद्धा शिमशोन की अमर गाथा! पूरी कहानी चैनल पर देखें। #Samson #HindiStories #Shorts",
        "scenes": [
            {
                "id": 1,
                "badge": "🦁 असीम ताकत",
                "image": IMG_LION,
                "narration": "उसने अपने खाली हाथों से एक खूंखार शेर को चीर डाला, ईश्वरीय शक्ति से भरा शिमशोन!",
                "subtitle": "खाली हाथों से शेर को चीर डाला!",
                "rate": "+5%", "pitch": "+1Hz"
            },
            {
                "id": 2,
                "badge": "✂️ दलीला का धोखा",
                "image": IMG_DELILAH,
                "narration": "लेकिन अंधेरी रात में प्रेम धोखे में बदल गया, और उसकी शक्ति छीन ली गई...",
                "subtitle": "प्रेम धोखे में बदला, शक्ति छीन ली गई...",
                "rate": "-12%", "pitch": "-2Hz"
            },
            {
                "id": 3,
                "badge": "💥 महाविनाश और विजय",
                "image": IMG_TEMPLE,
                "narration": "ज़ंजीरों में बंधे उसने ईश्वर को पुकारा, और खंभों को तोड़कर पूरे मंदिर को ध्वस्त कर दिया!",
                "subtitle": "खंभों को तोड़कर मंदिर ध्वस्त कर दिया!",
                "rate": "-2%", "pitch": "-1Hz"
            }
        ]
    },
    "de": {
        "name": "German",
        "voice": "de-DE-ConradNeural",
        "font": EURO_FONT_PATH,
        "cta": "👇 KLICKE UNTEN FÜR DEN GANZEN FILM",
        "title_post": "Er kämpfte mit bloßen Händen gegen einen LÖWEN! 🦁 Simson",
        "caption": "Vom Kampf gegen den Löwen bis zum Einsturz des Tempels! Erlebe Simsons epische Geschichte auf unserem Kanal! #Simson #BibelGeschichten #Shorts",
        "scenes": [
            {
                "id": 1,
                "badge": "🦁 ÜBERMENSCHLICHE KRAFT",
                "image": IMG_LION,
                "narration": "Mit bloßen Händen bezwang er einen brüllenden Löwen durch göttliche Macht!",
                "subtitle": "Mit bloßen Händen bezwang er den Löwen!",
                "rate": "+5%", "pitch": "+1Hz"
            },
            {
                "id": 2,
                "badge": "✂️ DER TÖDLICHE VERRAT",
                "image": IMG_DELILAH,
                "narration": "Bis Liebe zum Verrat wurde und sein heiliges Geheimnis gestohlen war...",
                "subtitle": "Bis seine heilige Kraft geraubt wurde...",
                "rate": "-12%", "pitch": "-2Hz"
            },
            {
                "id": 3,
                "badge": "💥 DER FINALE SIEG",
                "image": IMG_TEMPLE,
                "narration": "In Ketten rief er Gott an und brachte den gewaltigen Tempel zum Einsturz!",
                "subtitle": "Er brachte den gewaltigen Tempel zum Einsturz!",
                "rate": "-2%", "pitch": "-1Hz"
            }
        ]
    },
    "fr": {
        "name": "French",
        "voice": "fr-FR-HenriNeural",
        "font": EURO_FONT_PATH,
        "cta": "👇 REGARDEZ L'HISTOIRE COMPLÈTE CI-DESSOUS",
        "title_post": "Il a terrassé un LION à mains nues! 🦁 La Force de Samson",
        "caption": "D'un combat féroce contre un lion à l'effondrement d'un temple! Découvrez l'incroyable légende de Samson sur notre chaîne! #Samson #Shorts",
        "scenes": [
            {
                "id": 1,
                "badge": "🦁 PUISSANCE DIVINE",
                "image": IMG_LION,
                "narration": "Il terrassa un lion rugissant à mains nues par une force divine prodigieuse!",
                "subtitle": "Il terrassa un lion rugissant à mains nues!",
                "rate": "+5%", "pitch": "+1Hz"
            },
            {
                "id": 2,
                "badge": "✂️ LA TRAHISON",
                "image": IMG_DELILAH,
                "narration": "Jusqu'à ce que l'amour devienne trahison et que sa force céleste lui soit volée...",
                "subtitle": "Jusqu'à ce que sa force lui soit dérobée...",
                "rate": "-12%", "pitch": "-2Hz"
            },
            {
                "id": 3,
                "badge": "💥 LE TRIOMPHE FINAL",
                "image": IMG_TEMPLE,
                "narration": "Enchaîné, il implora Dieu une dernière fois et fit s'effondrer le temple colossal!",
                "subtitle": "Il fit s'effondrer le temple colossal!",
                "rate": "-2%", "pitch": "-1Hz"
            }
        ]
    },
    "es": {
        "name": "Spanish",
        "voice": "es-ES-AlvaroNeural",
        "font": EURO_FONT_PATH,
        "cta": "👇 TOCA ABAJO PARA VER LA PELÍCULA COMPLETA",
        "title_post": "¡Luchó contra un LEÓN con sus manos! 🦁 La Fuerza de Sansón",
        "caption": "¡De vencer a un león con sus manos a derrumbar un templo colosal! Conoce la historia épica de Sansón en nuestro canal. #Sanson #HistoriasBiblicas #Shorts",
        "scenes": [
            {
                "id": 1,
                "badge": "🦁 FUERZA SOBRENATURAL",
                "image": IMG_LION,
                "narration": "¡Luchó contra un león rugiente con sus propias manos y lo venció con poder celestial!",
                "subtitle": "¡Venció a un león rugiente con sus manos!",
                "rate": "+5%", "pitch": "+1Hz"
            },
            {
                "id": 2,
                "badge": "✂️ LA TRAICIÓN DE DALILA",
                "image": IMG_DELILAH,
                "narration": "Hasta que el amor se convirtió en traición, y su fuerza sagrada fue arrebatada...",
                "subtitle": "Hasta que su fuerza sagrada fue arrebatada...",
                "rate": "-12%", "pitch": "-2Hz"
            },
            {
                "id": 3,
                "badge": "💥 EL DERRUMBE DEL TEMPLO",
                "image": IMG_TEMPLE,
                "narration": "¡Encadenado, clamó a Dios por última vez y derrumbó el colosal templo sobre sus opresores!",
                "subtitle": "¡Derrumbó el templo sobre sus opresores!",
                "rate": "-2%", "pitch": "-1Hz"
            }
        ]
    }
}

def generate_short_sfx(scene_id, duration_sec, sample_rate=44100):
    num_samples = int(duration_sec * sample_rate)
    audio = np.zeros(num_samples, dtype=np.float32)
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)

    # Base cinematic low rumble
    audio += 0.08 * np.sin(2 * np.pi * 55.0 * t)

    if scene_id == 1:
        # Lion roar
        noise = np.random.normal(0, 0.18, num_samples)
        mod = (np.sin(2 * np.pi * 5.0 * t) ** 2) * np.clip((t - 1.0) / 1.5, 0, 1)
        audio += (noise * mod * 0.45).astype(np.float32)
    elif scene_id == 2:
        # Tense heartbeat
        audio += (0.22 * np.sin(2 * np.pi * 50.0 * t) * (np.sin(2 * np.pi * 1.5 * t) ** 8)).astype(np.float32)
    elif scene_id == 3:
        # Earthquake + temple crash
        crash_t = np.maximum(0.0, t - max(0.0, duration_sec - 4.5))
        crash = np.random.normal(0, 0.35, num_samples) * np.clip(crash_t / 1.5, 0, 1) * np.exp(-crash_t * 0.3)
        seismic = 0.3 * np.sin(2 * np.pi * 32.0 * t)
        audio += (crash + seismic).astype(np.float32)

    audio = np.clip(audio, -0.95, 0.95)
    return (audio * 32767).astype(np.int16)

def get_audio_duration(file_path):
    cmd = [FFMPEG_EXE, "-i", file_path, "-hide_banner"]
    p = subprocess.run(cmd, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
    import re
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", p.stderr)
    if match:
        h, m, s = match.groups()
        return int(h) * 3600 + int(m) * 60 + float(s)
    return 10.0

async def generate_speech(text, voice, out_mp3, rate="+0%", pitch="+0Hz"):
    comm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await comm.save(out_mp3)

def render_vertical_frame(raw_img, progress, badge_text, subtitle_text, cta_text, font_path, out_w=720, out_h=1280):
    """
    Renders high-converting vertical short layout:
    - Upper-third gold badge
    - Center 16:9 cinematic shot with slow zoom & gold frame
    - High-contrast subtitle card
    - Bottom pulsing CTA
    """
    h, w = raw_img.shape[:2]

    # 1. Background: Blurred, darkened ambient filler
    bg_resized = cv2.resize(raw_img, (out_w, out_h))
    bg_blurred = cv2.GaussianBlur(bg_resized, (75, 75), 0)
    bg_dark = (bg_blurred * 0.38).astype(np.uint8)

    # 2. Center 16:9 Frame with dynamic Ken Burns zoom
    scale = 1.0 + 0.10 * progress
    crop_w, crop_h = int(w / scale), int(h / scale)
    cx, cy = w // 2, h // 2
    x1, y1 = max(0, cx - crop_w // 2), max(0, cy - crop_h // 2)
    cropped = raw_img[y1:y1 + crop_h, x1:x1 + crop_w]

    fg_w = out_w - 40
    fg_h = int(fg_w * (9 / 16))
    fg_resized = cv2.resize(cropped, (fg_w, fg_h), interpolation=cv2.INTER_LINEAR)

    center_y = (out_h - fg_h) // 2 - 40
    center_x = (out_w - fg_w) // 2

    # Border around center frame
    cv2.rectangle(bg_dark, (center_x - 3, center_y - 3), (center_x + fg_w + 3, center_y + fg_h + 3), (245, 158, 11), 3)
    bg_dark[center_y:center_y + fg_h, center_x:center_x + fg_w] = fg_resized

    pil_img = Image.fromarray(cv2.cvtColor(bg_dark, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img, "RGBA")

    try:
        font_badge = ImageFont.truetype(font_path, 34)
        font_sub = ImageFont.truetype(font_path, 32)
        font_cta = ImageFont.truetype(font_path, 26)
    except:
        font_badge = font_sub = font_cta = ImageFont.load_default()

    # Top Badge
    b_box = font_badge.getbbox(badge_text)
    bw, bh = b_box[2] - b_box[0], b_box[3] - b_box[1]
    pill_w = bw + 50
    pill_h = bh + 24
    bx = (out_w - pill_w) // 2
    by = center_y - pill_h - 40
    draw.rounded_rectangle([bx, by, bx + pill_w, by + pill_h], radius=16, fill=(15, 18, 26, 235), outline=(245, 158, 11, 240), width=2)
    draw.text(((out_w - bw) // 2, by + 12), badge_text, font=font_badge, fill=(251, 191, 36))

    # Center Subtitle Card
    if subtitle_text:
        s_box = font_sub.getbbox(subtitle_text)
        sw, sh = s_box[2] - s_box[0], s_box[3] - s_box[1]
        card_w = min(out_w - 60, sw + 50)
        card_h = sh + 30
        cx_sub = (out_w - card_w) // 2
        cy_sub = center_y + fg_h + 40
        draw.rounded_rectangle([cx_sub, cy_sub, cx_sub + card_w, cy_sub + card_h], radius=14, fill=(10, 12, 16, 240), outline=(245, 158, 11, 220), width=2)
        draw.text(((out_w - sw) // 2 + 1, cy_sub + 15 + 1), subtitle_text, font=font_sub, fill=(0, 0, 0, 255))
        draw.text(((out_w - sw) // 2, cy_sub + 15), subtitle_text, font=font_sub, fill=(255, 255, 255, 255))

    # Bottom CTA
    c_box = font_cta.getbbox(cta_text)
    cw = c_box[2] - c_box[0]
    draw.text(((out_w - cw) // 2, out_h - 90), cta_text, font=font_cta, fill=(251, 191, 36, 230))

    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def build_single_short(lang_code, cfg):
    print(f"\n==========================================")
    print(f"📱 Rendering 9:16 Short: {cfg['name']}")
    print(f"==========================================")

    lang_dir = os.path.join(SHORTS_DIR, lang_code)
    os.makedirs(lang_dir, exist_ok=True)

    scene_mp4s = []

    for scene in cfg["scenes"]:
        s_id = scene["id"]
        tts_file = os.path.join(lang_dir, f"short_{s_id}_voice.mp3")
        asyncio.run(generate_speech(scene["narration"], cfg["voice"], tts_file, rate=scene["rate"], pitch=scene["pitch"]))
        duration = get_audio_duration(tts_file) + 0.8
        print(f"  ▶ Hook {s_id}: {duration:.1f}s via {cfg['voice']}")

        sfx_pcm = generate_short_sfx(s_id, duration)
        sfx_wav = os.path.join(lang_dir, f"short_{s_id}_sfx.wav")
        with wave.open(sfx_wav, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            wf.writeframes(sfx_pcm.tobytes())

        mixed_audio = os.path.join(lang_dir, f"short_{s_id}_audio.aac")
        subprocess.run([
            FFMPEG_EXE, "-y",
            "-i", tts_file, "-i", sfx_wav,
            "-filter_complex", "[0:a]volume=1.0[v];[1:a]volume=0.35[s];[v][s]amix=inputs=2:duration=longest[a]",
            "-map", "[a]", "-c:a", "aac", "-b:a", "192k",
            mixed_audio
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Render Vertical Frames
        raw_video = os.path.join(lang_dir, f"short_{s_id}_raw.mp4")
        fps = 24
        total_frames = int(duration * fps)
        raw_img = cv2.imread(scene["image"])

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(raw_video, fourcc, float(fps), (720, 1280))

        for f in range(total_frames):
            prog = f / float(total_frames)
            frame = render_vertical_frame(raw_img, prog, scene["badge"], scene["subtitle"], cfg["cta"], cfg["font"])
            out.write(frame)
        out.release()

        # Mux Scene
        final_mp4 = os.path.join(lang_dir, f"short_{s_id}_final.mp4")
        subprocess.run([
            FFMPEG_EXE, "-y",
            "-i", raw_video, "-i", mixed_audio,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19",
            "-c:a", "copy", "-shortest",
            final_mp4
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        scene_mp4s.append(final_mp4)

    # Concat into master Short
    concat_txt = os.path.join(lang_dir, "concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for p in scene_mp4s:
            f.write(f"file '{os.path.abspath(p)}'\n")

    master_short = os.path.join(SHORTS_DIR, f"samson_short_{lang_code}.mp4")
    subprocess.run([
        FFMPEG_EXE, "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_txt,
        "-c", "copy",
        master_short
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(f"🎉 MASTER 9:16 SHORT READY: {master_short} ({os.path.getsize(master_short) / 1024 / 1024:.2f} MB)")
    return master_short

def generate_posting_manifest():
    manifest_path = os.path.join(SHORTS_DIR, "POSTING_MANIFEST.md")
    content = "# 📱 FableForge Samson: 6-Language Posting Guide\n\n"
    content += "Ready-to-copy metadata for YouTube Shorts, Instagram Reels, and TikTok.\n\n---\n\n"

    for code, cfg in SHORTS_CONFIG.items():
        content += f"## {cfg['name']} ({code.upper()})\n\n"
        content += f"**🎥 Video File:** `storage/samson/shorts/samson_short_{code}.mp4`\n\n"
        content += f"### 📌 YouTube Shorts Title\n```\n{cfg['title_post']}\n```\n\n"
        content += f"### 📝 Description / Caption\n```\n{cfg['caption']}\n```\n\n"
        content += f"### 🏷️ Top Tags & Hashtags\n```\n#Samson #BibleStories #Shorts #Animation #Faith #Viral #Reels #TikTok\n```\n\n---\n\n"

    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"📋 Generated Posting Manifest: {manifest_path}")

if __name__ == "__main__":
    target_langs = sys.argv[1:] if len(sys.argv) > 1 else list(SHORTS_CONFIG.keys())
    for code in target_langs:
        if code in SHORTS_CONFIG:
            build_single_short(code, SHORTS_CONFIG[code])
    generate_posting_manifest()

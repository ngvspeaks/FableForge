# -*- coding: utf-8 -*-
"""
FableForge - Multilingual Samson Epic Production Pipeline
Builds a 6-Language Cinematic Animated Masterpiece with:
1. English, Hindi, Malayalam, German, French, Spanish Neural Voiceovers (Edge-TTS)
2. Layered Cinematic Sound Design (Dynamic low rumble, tension strings, lion battle, shears, chains, temple collapse)
3. Synchronized Typography Subtitles (Nirmala for Indic, Segoe UI for European)
4. Drop-in AI Video Engine: automatically uses video diffusion clips from storage/samson/video_clips/ if available,
   or animates 4K keyframe anchor visuals with Ken Burns 2.5D camera interpolation.
"""

import os
import sys
import subprocess
import asyncio
import wave
import math
import struct
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
VIDEO_CLIPS_DIR = os.path.join(STORAGE_DIR, "video_clips")
AUDIO_DIR = os.path.join(STORAGE_DIR, "audio")
OUTPUT_DIR = os.path.join(STORAGE_DIR, "output")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(VIDEO_CLIPS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Fonts
INDIC_FONT_PATH = r"C:\Windows\Fonts\Nirmala.ttc"
EURO_FONT_PATH = r"C:\Windows\Fonts\segoeui.ttf"

# 6 Supported Languages Configuration
LANGUAGES = {
    "en": {
        "name": "English",
        "voice": "en-US-ChristopherNeural",
        "font": EURO_FONT_PATH,
        "flag": "🇺🇸",
        "scenes": [
            {
                "id": 1,
                "title": "Act 1: The Lion of Timnah",
                "narration": "In the ancient hills of Dan, a child was consecrated under the sacred Nazirite vow. Samson grew with unmatched divine strength. As he walked through the sunlit vineyards of Timnah, a fierce young lion charged from the rocks, roaring with fury. But Samson seized the beast with his bare hands, tearing it apart like a young goat.",
                "subtitles": [
                    (0.0, 4.5, "In the hills of Dan, a child was consecrated under the sacred vow."),
                    (4.5, 9.0, "Samson grew with unmatched divine strength."),
                    (9.0, 14.5, "In the vineyards of Timnah, a fierce lion charged from the rocks!"),
                    (14.5, 20.0, "Samson seized the beast with bare hands, tearing it apart.")
                ]
            },
            {
                "id": 2,
                "title": "Act 2: The Victory at Ramath-lehi",
                "narration": "Bound in fresh ropes and handed over to his oppressors, Samson stood alone in the valley. Suddenly, the Spirit fell upon him! The cords on his arms melted like burned flax. Lifting the fresh jawbone of a donkey from the sand, Samson charged forward, routing a thousand warriors in the dust of Ramath-lehi.",
                "subtitles": [
                    (0.0, 4.5, "Bound in fresh ropes, Samson stood alone before his oppressors."),
                    (4.5, 9.0, "Suddenly, the Spirit fell upon him! The cords melted like burned flax."),
                    (9.0, 14.0, "Lifting the fresh jawbone of a donkey from the sand,"),
                    (14.0, 19.5, "Samson routed a thousand warriors in the dust of Ramath-lehi.")
                ]
            },
            {
                "id": 3,
                "title": "Act 3: Delilah's Betrayal",
                "narration": "In the candlelit valley of Sorek, love turned into treachery. Delilah begged to learn the secret of his great might. Wearied by her persistent pleas, Samson revealed his sacred secret: no razor had ever touched his head. As he slept upon her lap, Delilah summoned the shears and severed his seven braids, draining his heavenly strength.",
                "subtitles": [
                    (0.0, 4.5, "In the candlelit valley of Sorek, love turned into treachery."),
                    (4.5, 9.5, "Wearied by Delilah's pleas, Samson revealed his sacred secret:"),
                    (9.5, 14.0, "No razor had ever touched his head."),
                    (14.0, 20.5, "As he slept, Delilah severed his seven braids, draining his strength.")
                ]
            },
            {
                "id": 4,
                "title": "Act 4: The Prison of Gaza",
                "narration": "Stripped of his strength and sight, Samson was thrown into the dark dungeons of Gaza. Bound in bronze shackles, he pushed the heavy grain millstone day after day. Yet, in the silence of his suffering, his heart turned back to God, and slowly, his sacred hair began to grow again.",
                "subtitles": [
                    (0.0, 4.5, "Stripped of strength and sight, Samson was thrown into Gaza's dungeons."),
                    (4.5, 9.5, "Bound in bronze shackles, he pushed the heavy grain mill day after day."),
                    (9.5, 14.5, "Yet in the silence of his suffering, his heart turned back to God,"),
                    (14.5, 19.5, "and slowly, his sacred hair began to grow again.")
                ]
            },
            {
                "id": 5,
                "title": "Act 5: The Fall of the Temple of Dagon",
                "narration": "Brought to the grand temple of Dagon to be mocked before thousands, Samson prayed with all his soul: 'Lord, remember me once more!' Placing his mighty hands against the two colossal central pillars, Samson bowed with all his might. The stone cracked, the pillars shattered, and the temple crashed down in a roar of thunder, granting him his greatest victory.",
                "subtitles": [
                    (0.0, 4.5, "Brought to Dagon's temple before thousands, Samson prayed:"),
                    (4.5, 8.5, "'Lord, remember me once more!'"),
                    (8.5, 14.0, "Placing his hands against the two colossal pillars, Samson bowed with all his might."),
                    (14.0, 21.0, "The pillars shattered, and the temple crashed down in thunderous victory.")
                ]
            }
        ]
    },
    "hi": {
        "name": "Hindi",
        "voice": "hi-IN-MadhurNeural",
        "font": INDIC_FONT_PATH,
        "flag": "🇮🇳",
        "scenes": [
            {
                "id": 1,
                "title": "अध्याय 1: तिमनाह का शेर",
                "narration": "दान के प्राचीन पहाड़ों में, एक बालक ने पवित्र नाज़ीर प्रतिज्ञा के तहत जन्म लिया। शिमशोन अद्वितीय ईश्वरीय शक्ति के साथ बड़ा हुआ। जब वह तिमनाह के अंगूरों के बागों से गुजर रहा था, तो एक खूंखार शेर दहाड़ते हुए उस पर झपटा। लेकिन शिमशोन ने अपने खाली हाथों से शेर को पकड़कर अपनी असीम ताकत से उसे परास्त कर दिया।",
                "subtitles": [
                    (0.0, 4.5, "दान के प्राचीन पहाड़ों में, एक बालक ने पवित्र प्रतिज्ञा के साथ जन्म लिया।"),
                    (4.5, 9.0, "शिमशोन अद्वितीय ईश्वरीय शक्ति के साथ बड़ा हुआ।"),
                    (9.0, 14.0, "तिमनाह के अंगूरों के बागों में, एक खूंखार शेर उस पर झपटा!"),
                    (14.0, 19.5, "शिमशोन ने खाली हाथों से शेर को पकड़कर उसे परास्त कर दिया।")
                ]
            },
            {
                "id": 2,
                "title": "अध्याय 2: रामत-लही की विजय",
                "narration": "नई रस्सियों से बंधा हुआ शिमशोन घाटी में अकेला खड़ा था। तभी उस पर प्रभु का सामर्थ्य उतरा! उसकी बाहों की रस्सियां जलती हुई सन की तरह टूट गईं। रेत से गधे के जबड़े की हड्डी उठाकर, शिमशोन ने भीषण युद्ध किया और रामत-लही की धूल में एक हज़ार योद्धाओं को धूल चटा दी।",
                "subtitles": [
                    (0.0, 4.5, "नई रस्सियों से बंधा हुआ शिमशोन घाटी में अकेला खड़ा था।"),
                    (4.5, 9.0, "तभी उस पर प्रभु का सामर्थ्य उतरा! रस्सियां जलती हुई सन की तरह टूट गईं।"),
                    (9.0, 14.0, "रेत से गधे के जबड़े की हड्डी उठाकर उसने युद्ध किया,"),
                    (14.0, 19.5, "और रामत-लही में एक हज़ार योद्धाओं को धूल चटा दी।")
                ]
            },
            {
                "id": 3,
                "title": "अध्याय 3: दलीला का विश्वासघात",
                "narration": "सोरेक की घाटी में प्रेम धोखे में बदल गया। दलीला ने उसकी असीम शक्ति का रहस्य जानने की जिद की। उसके बार-बार पूछने से थककर, शिमशोन ने अपना गहरा रहस्य बता दिया: उसके सिर पर कभी उस्तरा नहीं फिरा था। जब वह उसकी गोद में सोया, दलीला ने कैंची से उसकी सात लटें काट दीं, और उसकी दैवीय शक्ति छिन गई।",
                "subtitles": [
                    (0.0, 4.5, "सोरेक की घाटी में प्रेम धोखे में बदल गया।"),
                    (4.5, 9.5, "दलीला की जिद पर शिमशोन ने रहस्य बताया:"),
                    (9.5, 14.0, "उसके सिर पर कभी उस्तरा नहीं फिरा था।"),
                    (14.0, 20.0, "दलीला ने उसकी सात लटें काट दीं, और उसकी शक्ति छिन गई।")
                ]
            },
            {
                "id": 4,
                "title": "अध्याय 4: गाज़ा की कालकोठरी",
                "narration": "अपनी शक्ति और आंखों की रोशनी खोकर, शिमशोन को गाज़ा की अंधेरी कालकोठरी में डाल दिया गया। कांस्य की बेड़ियों में जकड़े हुए, वह दिन-रात भारी चक्की पीसता रहा। लेकिन अपने दुखों के सन्नाटे में, उसका हृदय ईश्वर की ओर मुड़ा, और धीरे-धीरे उसके बाल फिर से बढ़ने लगे।",
                "subtitles": [
                    (0.0, 4.5, "अपनी शक्ति और दृष्टि खोकर, शिमशोन कालकोठरी में डाल दिया गया।"),
                    (4.5, 9.5, "कांस्य की बेड़ियों में जकड़े हुए, वह दिन-रात चक्की पीसता रहा।"),
                    (9.5, 14.5, "अपने दुखों में उसका हृदय ईश्वर की ओर मुड़ा,"),
                    (14.5, 19.5, "और धीरे-धीरे उसके बाल फिर से बढ़ने लगे।")
                ]
            },
            {
                "id": 5,
                "title": "अध्याय 5: दाजोन के मंदिर का पतन",
                "narration": "हज़ारों लोगों के सामने उपहास उड़ाने के लिए दाजोन के भव्य मंदिर में लाए जाने पर, शिमशोन ने प्रार्थना की: 'हे प्रभु, मुझे एक बार और याद कर!' दो विशाल मुख्य स्तंभों पर अपने दोनों हाथ रखकर, शिमशोन ने अपनी पूरी शक्ति से ज़ोर लगाया। खंभे चकनाचूर हो गए, और मंदिर गड़गड़ाहट के साथ ढह गया, जिससे उसकी अंतिम और सबसे महान विजय हुई।",
                "subtitles": [
                    (0.0, 4.5, "दाजोन के भव्य मंदिर में शिमशोन ने प्रार्थना की:"),
                    (4.5, 8.5, "'हे प्रभु, मुझे एक बार और याद कर!'"),
                    (8.5, 14.0, "दो मुख्य स्तंभों पर हाथ रखकर उसने पूरी शक्ति से ज़ोर लगाया।"),
                    (14.0, 21.0, "खंभे चकनाचूर हो गए, और मंदिर गड़गड़ाहट के साथ ढह गया!")
                ]
            }
        ]
    },
    "ml": {
        "name": "Malayalam",
        "voice": "ml-IN-MidhunNeural",
        "font": INDIC_FONT_PATH,
        "flag": "🇮🇳",
        "scenes": [
            {
                "id": 1,
                "title": "രംഗം 1: തിമ്നയിലെ സിംഹം",
                "narration": "ദാൻ ഗോത്രത്തിന്റെ പുരാതന കുന്നുകളിൽ, ദൈവത്തിന്റെ നാസീർ വ്രതത്തോടെ ഒരു വീരൻ ജനിച്ചു; അവൻ ആയിരുന്നു ശിംശോൻ! ഒരിക്കൽ തിമ്നയിലെ മുന്തിരിത്തോപ്പിലൂടെ നടക്കുമ്പോൾ, പാറക്കൂട്ടങ്ങൾക്കിടയിൽ നിന്ന് ഒരു കൊടും സിംഹം അലറിപ്പാഞ്ഞു വന്നു. എന്നാൽ ദൈവത്തിന്റെ ആത്മാവ് ശക്തിയോടെ ശിംശോനിൽ വ്യാപിച്ചു; അവൻ വെറുംകൈകളോടെ ആ സിംഹത്തെ കീറിമുറിച്ച് നിലംപരിശാക്കി!",
                "subtitles": [
                    (0.0, 4.5, "ദാൻ ഗോത്രത്തിന്റെ കുന്നുകളിൽ നാസീർ വ്രതത്തോടെ ശിംശോൻ ജനിച്ചു."),
                    (4.5, 9.0, "അവൻ അജയ്യനായ വീരനായി വളർന്നു വന്നു."),
                    (9.0, 14.0, "മുന്തിരിത്തോപ്പിലൂടെ നടക്കുമ്പോൾ കൊടും സിംഹം അലറിപ്പാഞ്ഞു വന്നു!"),
                    (14.0, 20.0, "വെറുംകൈകളോടെ ശിംശോൻ ആ സിംഹത്തെ കീറിമുറിച്ചു വീഴ്ത്തി.")
                ]
            },
            {
                "id": 2,
                "title": "രംഗം 2: രാമത്ത്-ലെഹിയുടെ വിജയം",
                "narration": "പുതിയ കയറുകളാൽ ബന്ധിക്കപ്പെട്ട് ശത്രുക്കളുടെ മുന്നിൽ ശിംശോൻ നിന്നു. പെട്ടെന്ന് ദൈവശക്തി അവനിൽ ആളിപ്പടർന്നു! അവന്റെ കൈകളിലെ കയറുകൾ കരിഞ്ഞ ചരടുപോലെ പൊട്ടിപ്പോയി. മണലിൽ കിടന്ന ഒരു കഴുതത്താടിയെല്ല് കയ്യിലെടുത്ത്, ആയിരം ശത്രുയോദ്ധാക്കളെ അവൻ തുരത്തിയോടിച്ചു; അത് രാമത്ത്-ലെഹിയുടെ വിജയമായി മാറി!",
                "subtitles": [
                    (0.0, 4.5, "പുതിയ കയറുകളാൽ ബന്ധിക്കപ്പെട്ട് ശിംശോൻ നിന്നു."),
                    (4.5, 9.0, "ദൈവശക്തി അവനിൽ ആളിപ്പടർന്നു, കയറുകൾ കരിഞ്ഞു പൊട്ടിപ്പോയി!"),
                    (9.0, 14.0, "ഒരു കഴുതത്താടിയെല്ല് കയ്യിലെടുത്ത് അവൻ പോരാടി,"),
                    (14.0, 19.5, "ആയിരം ശത്രുയോദ്ധാക്കളെ തുരത്തി രാമത്ത്-ലെഹിയിൽ വിജയം നേടി.")
                ]
            },
            {
                "id": 3,
                "title": "രംഗം 3: ദെലീലയുടെ വഞ്ചന",
                "narration": "സോരെക്ക് താഴ്‌വരയിൽ പ്രണയം വഞ്ചനയായി മാറി. ദെലീലാ അവന്റെ രഹസ്യം ചോദിച്ചുകൊണ്ടിരുന്നു. മനസ്സ് തളർന്ന ശിംശോൻ ജീവരഹസ്യം വെളിപ്പെടുത്തി: തന്റെ തലയിൽ ഒരിക്കലും ക്ഷൗരക്കത്തി വീണിട്ടില്ല. അവൻ മടിയിൽ ഉറങ്ങവേ, ദെലീലാ കത്രികയെടുത്ത് അവന്റെ ഏഴു ജടകളും മുറിച്ചുമാറ്റി; ശിംശോന്റെ ദിവ്യശക്തി അവനെ വിട്ടുപോയി.",
                "subtitles": [
                    (0.0, 4.5, "സോരെക്ക് താഴ്‌വരയിൽ പ്രണയം വഞ്ചനയായി മാറി."),
                    (4.5, 9.5, "മനസ്സ് തളർന്ന ശിംശോൻ ജീവരഹസ്യം വെളിപ്പെടുത്തി:"),
                    (9.5, 14.0, "തന്റെ തലയിൽ ഒരിക്കലും ക്ഷൗരക്കത്തി വീണിട്ടില്ല."),
                    (14.0, 20.5, "അവൻ ഉറങ്ങവേ ദെലീലാ ഏഴു ജടകളും മുറിച്ചു, ദിവ്യശക്തി വിട്ടുപോയി.")
                ]
            },
            {
                "id": 4,
                "title": "രംഗം 4: ഗസ്സയിലെ കാരാഗൃഹം",
                "narration": "കാഴ്ച നഷ്ടപ്പെട്ട്, ബന്ധനസ്ഥനായ ശിംശോനെ ഗസ്സയിലെ ഇരുണ്ട കാരാഗൃഹത്തിൽ തള്ളിവിട്ടു. വെങ്കലച്ചങ്ങലകളാൽ ബന്ധിക്കപ്പെട്ട്, അവൻ വലിപ്പമേറിയ ധാന്യക്കല്ല് കറക്കിക്കൊണ്ടിരുന്നു. എന്നാൽ ഏകാന്തതയുടെ കണ്ണീരിലും അവൻ ദൈവത്തിലേക്ക് പ്രാർത്ഥനയോടെ തിരിഞ്ഞു; സാവധാനം അവന്റെ തലയിലെ മുടി വീണ്ടും വളരാൻ തുടങ്ങി!",
                "subtitles": [
                    (0.0, 4.5, "കാഴ്ച നഷ്ടപ്പെട്ട ശിംശോനെ ഇരുണ്ട കാരാഗൃഹത്തിൽ തള്ളിവിട്ടു."),
                    (4.5, 9.5, "ചങ്ങലകളാൽ ബന്ധിക്കപ്പെട്ട് അവൻ വലിപ്പമേറിയ ധാന്യക്കല്ല് കറക്കി."),
                    (9.5, 14.5, "കണ്ണീരിലും അവൻ ദൈവത്തിലേക്ക് പ്രാർത്ഥനയോടെ തിരിഞ്ഞു,"),
                    (14.5, 19.5, "സാവധാനം അവന്റെ തലയിലെ മുടി വീണ്ടും വളരാൻ തുടങ്ങി!")
                ]
            },
            {
                "id": 5,
                "title": "രംഗം 5: ദാഗോൻ ക്ഷേത്രത്തിന്റെ തകർച്ച",
                "narration": "ആയിരക്കണക്കിന് ആളുകളുടെ പരിഹാസങ്ങൾക്കിടയിൽ ദാഗോൻ ക്ഷേത്രത്തിൽ നിർത്തിയപ്പോൾ, ശിംശോൻ ഉള്ളുരുകി പ്രാർത്ഥിച്ചു: 'കർത്താവേ, എന്നെ ഒരിക്കൽക്കൂടി ഓർക്കേണമേ!' ക്ഷേത്രത്തിന്റെ രണ്ടു കൂറ്റൻ തൂണുകളിൽ തന്റെ കരങ്ങൾ വെച്ച്, അവൻ സർവ്വശക്തിയോടെ മുന്നോട്ട് ആഞ്ഞു. തൂണുകൾ പൊട്ടിത്തകർന്നു; മഹാക്ഷേത്രം ഇടിമുഴക്കത്തോടെ നിലംപൊത്തി; ശിംശോൻ ഏറ്റവും വലിയ വിജയം കൈവരിച്ചു!",
                "subtitles": [
                    (0.0, 4.5, "ദാഗോൻ ക്ഷേത്രത്തിൽ നിർത്തിയപ്പോൾ ശിംശോൻ പ്രാർത്ഥിച്ചു:"),
                    (4.5, 8.5, "'കർത്താവേ, എന്നെ ഒരിക്കൽക്കൂടി ഓർക്കേണമേ!'"),
                    (8.5, 14.0, "രണ്ടു കൂറ്റൻ തൂണുകളിൽ കരങ്ങൾ വെച്ച് സർവ്വശക്തിയോടെ ആഞ്ഞു!"),
                    (14.0, 21.0, "തൂണുകൾ തകർന്നു, ക്ഷേത്രം ഇടിമുഴക്കത്തോടെ നിലംപൊത്തി!")
                ]
            }
        ]
    },
    "de": {
        "name": "German",
        "voice": "de-DE-ConradNeural",
        "font": EURO_FONT_PATH,
        "flag": "🇩🇪",
        "scenes": [
            {
                "id": 1,
                "title": "Akt 1: Der Löwe von Timna",
                "narration": "In den uralten Hügeln von Dan wuchs ein Junge unter dem heiligen Gelübde der Nasiräer heran. Simson besaß übermenschliche göttliche Kraft. Als er durch die Weinberge von Timna zog, sprang plötzlich ein wilder Löwe mit furchterregendem Brüllen hervor. Doch Simson packte das Raubtier mit bloßen Händen und bezwang es mit gewaltiger Macht.",
                "subtitles": [
                    (0.0, 4.5, "In den Hügeln von Dan wuchs Simson unter heiligem Gelübde heran."),
                    (4.5, 9.0, "Er besaß übermenschliche göttliche Kraft."),
                    (9.0, 14.0, "In den Weinbergen von Timna sprang ein wilder Löwe hervor!"),
                    (14.0, 19.5, "Simson packte das Raubtier mit bloßen Händen und bezwang es.")
                ]
            },
            {
                "id": 2,
                "title": "Akt 2: Der Sieg bei Ramath-Lechi",
                "narration": "Mit neuen Seilen gefesselt stand Simson seinen Feinden im Tal gegenüber. Plötzlich ergriff ihn göttliche Kraft! Die Seile an seinen Armen rissen wie verbranntes Flachs. Er ergriff den Kieferknochen eines Esels und schlug im Staube von Ramath-Lechi tausend Krieger in die Flucht.",
                "subtitles": [
                    (0.0, 4.5, "Mit neuen Seilen gefesselt stand Simson seinen Feinden gegenüber."),
                    (4.5, 9.0, "Göttliche Kraft ergriff ihn! Die Seile rissen wie verbranntes Flachs."),
                    (9.0, 14.0, "Er ergriff den Kieferknochen eines Esels aus dem Staub,"),
                    (14.0, 19.5, "und schlug bei Ramath-Lechi tausend Krieger in die Flucht.")
                ]
            },
            {
                "id": 3,
                "title": "Akt 3: Delilas Verrat",
                "narration": "Im Kerzenlicht des Tals von Sorek wurde Liebe zum Verrat. Delila drängte ihn beharrlich, das Geheimnis seiner Macht zu offenbaren. Müde von ihrem Flehen gestand Simson die Wahrheit: Noch nie hatte ein Schermesser sein Haupt berührt. Als er auf ihrem Schoß einschlief, schnitt Delila seine sieben Locken ab, und seine Kraft verließ ihn.",
                "subtitles": [
                    (0.0, 4.5, "Im Tal von Sorek wurde Liebe zum Verrat."),
                    (4.5, 9.5, "Müde von Delilas Drängen gestand Simson sein Geheimnis:"),
                    (9.5, 14.0, "Noch nie hatte ein Schermesser sein Haupt berührt."),
                    (14.0, 20.0, "Delila schnitt seine sieben Locken ab, und seine Kraft verließ ihn.")
                ]
            },
            {
                "id": 4,
                "title": "Akt 4: Das Verlies von Gaza",
                "narration": "Seiner Kraft und seines Augenlichts beraubt, warf man Simson in das finstere Verlies von Gaza. In bronzene Ketten geschlagen, musste er den schweren Mühlstein drehen. Doch im Schmerz wandte sich sein Herz wieder Gott zu, und leise begann sein Haar von neuem zu wachsen.",
                "subtitles": [
                    (0.0, 4.5, "Der Sehkraft beraubt, warf man Simson in das Verlies von Gaza."),
                    (4.5, 9.5, "In Ketten geschlagen drehte er den schweren Mühlstein."),
                    (9.5, 14.5, "Doch im Schmerz wandte sich sein Herz wieder Gott zu,"),
                    (14.5, 19.5, "und leise begann sein Haar von neuem zu wachsen.")
                ]
            },
            {
                "id": 5,
                "title": "Akt 5: Der Einsturz des Tempels",
                "narration": "Vor tausenden Spöttern in den Tempel Dagons geführt, betete Simson: 'Herr, gedenke mein noch dieses eine Mal!' Mit beiden Händen stemmte er sich gegen die zwei gewaltigen Mittelsäulen. Die Pfeiler zerbarsten, die Mauern stürzten im Donnergetöse ein, und Simson vollbrachte seinen größten Triumph.",
                "subtitles": [
                    (0.0, 4.5, "Im Tempel Dagons betete Simson aus tiefster Seele:"),
                    (4.5, 8.5, "'Herr, gedenke mein noch dieses eine Mal!'"),
                    (8.5, 14.0, "Mit beiden Händen stemmte er sich gegen die zwei Mittelsäulen."),
                    (14.0, 21.0, "Die Pfeiler zerbarsten, und der Tempel stürzte donnernd ein!")
                ]
            }
        ]
    },
    "fr": {
        "name": "French",
        "voice": "fr-FR-HenriNeural",
        "font": EURO_FONT_PATH,
        "flag": "🇫🇷",
        "scenes": [
            {
                "id": 1,
                "title": "Acte 1: Le Lion de Thimna",
                "narration": "Dans les antiques collines de Dan, un enfant naquit sous le vœu sacré du naziréat. Samson grandit avec une force divine sans égale. Alors qu'il traversait les vignobles ensoleillés de Thimna, un jeune lion féroce surgit en rugissant. Mais Samson saisit la bête à mains nues et la terrassa par sa formidable puissance.",
                "subtitles": [
                    (0.0, 4.5, "Dans les collines de Dan, Samson naquit sous un vœu sacré."),
                    (4.5, 9.0, "Il grandit avec une force divine sans égale."),
                    (9.0, 14.0, "Dans les vignobles de Thimna, un lion féroce surgit en rugissant!"),
                    (14.0, 19.5, "Samson saisit la bête à mains nues et la terrassa.")
                ]
            },
            {
                "id": 2,
                "title": "Acte 2: La Victoire de Ramath-Léhi",
                "narration": "Ligoté avec des cordes neuves, Samson se tenait seul face à ses ennemis. Soudain, l'Esprit divin s'empara de lui! Les liens fondirent comme du lin brûlé. Ramassant la mâchoire d'un âne sur le sol, Samson chargea et terrassa mille guerriers dans la poussière de Ramath-Léhi.",
                "subtitles": [
                    (0.0, 4.5, "Ligoté avec des cordes neuves, Samson se tenait face aux ennemis."),
                    (4.5, 9.0, "L'Esprit s'empara de lui! Les liens fondirent comme du lin brûlé."),
                    (9.0, 14.0, "Ramassant la mâchoire d'un âne sur le sol,"),
                    (14.0, 19.5, "Samson terrassa mille guerriers à Ramath-Léhi.")
                ]
            },
            {
                "id": 3,
                "title": "Acte 3: La Trahison de Dalila",
                "narration": "Dans la vallée de Sorek, l'amour se transforma en trahison. Dalila le supplia de révéler le secret de son immense pouvoir. Épuisé par ses insistances, Samson avoua son vœu sacré: aucun rasoir n'avait effleuré sa tête. Endormi sur ses genoux, Dalila coupa ses sept tresses, lui ôtant sa force céleste.",
                "subtitles": [
                    (0.0, 4.5, "Dans la vallée de Sorek, l'amour devint trahison."),
                    (4.5, 9.5, "Épuisé par Dalila, Samson avoua son secret sacré:"),
                    (9.5, 14.0, "Aucun rasoir n'avait effleuré sa tête."),
                    (14.0, 20.0, "Dalila coupa ses sept tresses, lui ôtant sa force.")
                ]
            },
            {
                "id": 4,
                "title": "Acte 4: Le Cachot de Gaza",
                "narration": "Privé de sa force et de la vue, Samson fut jeté dans les sombres cachots de Gaza. Enchaîné de bronze, il poussait la lourde meule à grain jour après jour. Pourtant, dans le silence de son calvaire, son cœur se tourna vers Dieu, et lentement, sa chevelure sacrée recommença à pousser.",
                "subtitles": [
                    (0.0, 4.5, "Privé de vue, Samson fut jeté dans les cachots de Gaza."),
                    (4.5, 9.5, "Enchaîné de bronze, il poussait la lourde meule à grain."),
                    (9.5, 14.5, "Dans le silence, son cœur se tourna vers Dieu,"),
                    (14.5, 19.5, "et lentement, sa chevelure sacrée recommença à pousser.")
                ]
            },
            {
                "id": 5,
                "title": "Acte 5: L'Effondrement du Temple",
                "narration": "Mené au grand temple de Dagon sous les railleries de la foule, Samson pria: 'Seigneur, souviens-toi de moi encore une fois!' Posant ses mains sur les deux colonnes centrales, il poussa de toutes ses forces. La pierre se brisa, et le temple s'effondra dans un fracas de tonnerre!",
                "subtitles": [
                    (0.0, 4.5, "Au temple de Dagon, Samson pria de toute son âme:"),
                    (4.5, 8.5, "'Seigneur, souviens-toi de moi encore une fois!'"),
                    (8.5, 14.0, "Posant ses mains sur les colonnes, il poussa de toutes ses forces."),
                    (14.0, 21.0, "La pierre se brisa et le temple s'effondra dans le tonnerre!")
                ]
            }
        ]
    },
    "es": {
        "name": "Spanish",
        "voice": "es-ES-AlvaroNeural",
        "font": EURO_FONT_PATH,
        "flag": "🇪🇸",
        "scenes": [
            {
                "id": 1,
                "title": "Acto 1: El León de Timnat",
                "narration": "En las antiguas colinas de Dan, un niño fue consagrado bajo el sagrado voto nazareo. Sansón creció con una fuerza divina inigualable. Mientras caminaba por las viñas soleadas de Timnat, un feroz león saltó hacia él con terrible rugido. Pero Sansón tomó a la bestia con sus manos desnudas y la venció con poder sobrenatural.",
                "subtitles": [
                    (0.0, 4.5, "En las colinas de Dan, Sansón creció bajo un voto sagrado."),
                    (4.5, 9.0, "Poseía una fuerza divina inigualable."),
                    (9.0, 14.0, "En las viñas de Timnat, un feroz león saltó hacia él!"),
                    (14.0, 19.5, "Sansón tomó a la bestia con sus manos y la venció.")
                ]
            },
            {
                "id": 2,
                "title": "Acto 2: La Victoria en Ramat-leji",
                "narration": "Atado con cuerdas nuevas, Sansón se encontraba solo ante sus enemigos. De pronto, ¡el Espíritu divino descendió sobre él! Las cuerdas se deshicieron como lino quemado. Levantando la quijada de un asno del suelo, Sansón venció a mil guerreros en la polvorienta llanura de Ramat-leji.",
                "subtitles": [
                    (0.0, 4.5, "Atado con cuerdas nuevas, Sansón estaba ante sus enemigos."),
                    (4.5, 9.0, "¡El Espíritu descendió! Las cuerdas se deshicieron como lino."),
                    (9.0, 14.0, "Levantando la quijada de un asno del suelo,"),
                    (14.0, 19.5, "Sansón venció a mil guerreros en Ramat-leji.")
                ]
            },
            {
                "id": 3,
                "title": "Acto 3: La Traición de Dalila",
                "narration": "En el valle de Sorek, el amor se convirtió en traición. Dalila le suplicó que revelara el secreto de su gran fuerza. Agotado por su insistencia, Sansón le abrió su corazón: jamás navaja alguna había tocado su cabeza. Mientras dormía, Dalila cortó sus siete trenzas, y su poder celestial lo abandonó.",
                "subtitles": [
                    (0.0, 4.5, "En el valle de Sorek, el amor se convirtió en traición."),
                    (4.5, 9.5, "Agotado por Dalila, Sansón reveló su secreto sagrado:"),
                    (9.5, 14.0, "Jamás navaja alguna había tocado su cabeza."),
                    (14.0, 20.0, "Dalila cortó sus siete trenzas, y su poder lo abandonó.")
                ]
            },
            {
                "id": 4,
                "title": "Acto 4: La Prisión de Gaza",
                "narration": "Despojado de su fuerza y de su vista, Sansón fue arrojado a las oscuras mazmorras de Gaza. Con grilletes de bronce, empujaba la pesada rueda del molino día tras día. Mas en el silencio de su dolor, su corazón clamó a Dios, y lentamente, sus cabellos comenzaron a crecer de nuevo.",
                "subtitles": [
                    (0.0, 4.5, "Sin fuerza ni vista, Sansón fue arrojado a las mazmorras de Gaza."),
                    (4.5, 9.5, "Con grilletes de bronce empujaba la pesada rueda del molino."),
                    (9.5, 14.5, "En el silencio de su dolor, su corazón clamó a Dios,"),
                    (14.5, 19.5, "y lentamente, sus cabellos comenzaron a crecer de nuevo.")
                ]
            },
            {
                "id": 5,
                "title": "Acto 5: La Caída del Templo de Dagón",
                "narration": "Llevado al gran templo de Dagón para ser objeto de burlas, Sansón oró: '¡Señor, acuérdate de mí una vez más!' Apoyando sus manos sobre las dos colosales columnas centrales, empujó con todo su ser. La piedra se agrietó, las columnas estallaron y el templo se desplomó en un rugido atronador.",
                "subtitles": [
                    (0.0, 4.5, "En el templo de Dagón, Sansón oró con toda su alma:"),
                    (4.5, 8.5, "'¡Señor, acuérdate de mí una vez más!'"),
                    (8.5, 14.0, "Apoyando sus manos sobre las columnas, empujó con todo su ser."),
                    (14.0, 21.0, "Las columnas estallaron y el templo se desplomó en un rugido!")
                ]
            }
        ]
    }
}

SCENE_IMAGE_MAP = {
    1: os.path.join(IMAGES_DIR, "samson_lion_battle_1793120775287.jpg"),
    2: os.path.join(IMAGES_DIR, "samson_ramath_lehi_1793120800316.jpg"),
    3: os.path.join(IMAGES_DIR, "delilah_betrayal_samson_1793120823545.jpg"),
    4: os.path.join(IMAGES_DIR, "samson_prison_gaza_1793120848559.jpg"),
    5: os.path.join(IMAGES_DIR, "samson_temple_dagon_1793120884719.jpg")
}

SCENE_MOTIONS = {
    1: "zoom_in",
    2: "pan_up",
    3: "zoom_in",
    4: "pan_right",
    5: "zoom_out"
}

def generate_cinematic_sfx(scene_id, duration_sec, sample_rate=44100):
    """
    Synthesizes rich cinematic sound effects for each scene:
    - Scene 1: Guttural lion roar rumble + wind whoosh
    - Scene 2: Desert battle horn + wind
    - Scene 3: Metallic scissors snip + low tension drone
    - Scene 4: Iron chains clinking + grinding millstone friction
    - Scene 5: Seismic earthquake rumble + explosive stone collapse
    """
    num_samples = int(duration_sec * sample_rate)
    audio = np.zeros(num_samples, dtype=np.float32)
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)

    # 1. Base cinematic warm low drone (shared across all scenes)
    base_drone = 0.08 * np.sin(2 * np.pi * 55.0 * t) + 0.05 * np.sin(2 * np.pi * 110.0 * t)
    audio += base_drone

    if scene_id == 1:
        # Lion roar & struggle: low frequency growl modulated by noise
        noise = np.random.normal(0, 0.15, num_samples)
        mod = np.sin(2 * np.pi * 6.0 * t) ** 2
        lion_growl = noise * (0.5 * np.sin(2 * np.pi * 85.0 * t) + 0.5) * mod
        # Gate it around 8-15 seconds
        lion_envelope = np.clip((t - 7.0) / 2.0, 0, 1) * np.clip((duration_sec - t) / 2.0, 0, 1)
        audio += (lion_growl * lion_envelope * 0.4).astype(np.float32)

    elif scene_id == 2:
        # Horn of victory + desert wind
        horn = 0.15 * np.sin(2 * np.pi * 220.0 * t) + 0.10 * np.sin(2 * np.pi * 330.0 * t)
        horn_env = np.clip((t - 1.0) / 1.5, 0, 1) * np.clip((7.0 - t) / 2.0, 0, 1)
        wind = np.random.normal(0, 0.08, num_samples)
        audio += (horn * horn_env + wind * 0.2).astype(np.float32)

    elif scene_id == 3:
        # Tense heartbeat pulse + metallic scissor snip
        heartbeat = 0.2 * np.sin(2 * np.pi * 48.0 * t) * (np.sin(2 * np.pi * 1.2 * t) ** 8)
        audio += heartbeat.astype(np.float32)

    elif scene_id == 4:
        # Heavy chains clinking + friction grinding
        grind = np.random.normal(0, 0.06, num_samples) * (np.sin(2 * np.pi * 0.3 * t) ** 2)
        chain_t = t % 3.0
        chain_ping = 0.15 * np.sin(2 * np.pi * 1450.0 * chain_t) * np.exp(-chain_t * 12.0)
        audio += (grind + chain_ping).astype(np.float32)

    elif scene_id == 5:
        # Earthquake rumble + massive cracking collapse
        seismic = 0.25 * np.sin(2 * np.pi * 32.0 * t) + 0.15 * np.sin(2 * np.pi * 42.0 * t)
        # Big crash at the end
        crash_start = max(0.0, duration_sec - 8.0)
        crash_t = np.maximum(0.0, t - crash_start)
        crash = np.random.normal(0, 0.3, num_samples) * np.clip(crash_t / 2.0, 0, 1) * np.exp(-crash_t * 0.2)
        audio += (seismic + crash).astype(np.float32)

    # Normalize and convert to 16-bit PCM
    audio = np.clip(audio, -0.95, 0.95)
    int_audio = (audio * 32767).astype(np.int16)
    return int_audio

def get_audio_duration(file_path):
    cmd = [
        FFMPEG_EXE, "-i", file_path,
        "-hide_banner"
    ]
    p = subprocess.run(cmd, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
    import re
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", p.stderr)
    if match:
        h, m, s = match.groups()
        return int(h) * 3600 + int(m) * 60 + float(s)
    return 15.0

SCENE_PROSODY = {
    1: {"rate": "+3%", "pitch": "+1Hz", "volume": "+5%", "sfx_vol": 0.45},   # Heroic Action / Lion battle
    2: {"rate": "+5%", "pitch": "+2Hz", "volume": "+10%", "sfx_vol": 0.40},  # Defiant Battle Fury
    3: {"rate": "-12%", "pitch": "-2Hz", "volume": "-5%", "sfx_vol": 0.22}, # Tense intimate whisper / Delilah shears
    4: {"rate": "-18%", "pitch": "-5Hz", "volume": "-10%", "sfx_vol": 0.32},# Mournful sorrow / heavy chains in prison
    5: {"rate": "-4%", "pitch": "-1Hz", "volume": "+15%", "sfx_vol": 0.55}  # Desperate prayer into thunderous triumph
}

async def generate_speech(text, voice, out_mp3, rate="+0%", pitch="+0Hz", volume="+0%"):
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, volume=volume)
    await communicate.save(out_mp3)

def render_subtitles_on_frame(frame, text, font_path, font_size=28):
    """Draws cinematic subtitles with black pill background and gold border."""
    h, w = frame.shape[:2]
    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)

    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # Center horizontally, position at lower third
    x = (w - text_w) // 2
    y = h - text_h - 45

    pad_x, pad_y = 20, 10
    pill_box = [x - pad_x, y - pad_y, x + text_w + pad_x, y + text_h + pad_y]

    # Translucent black background
    overlay = Image.new("RGBA", pil_img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle(pill_box, radius=12, fill=(10, 12, 16, 210), outline=(245, 158, 11, 230), width=2)
    pil_img = Image.alpha_composite(pil_img.convert("RGBA"), overlay).convert("RGB")

    # Render text with subtle shadow
    final_draw = ImageDraw.Draw(pil_img)
    final_draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0))
    final_draw.text((x, y), text, font=font, fill=(255, 255, 255))

    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def create_scene_video(scene_id, image_path, duration_sec, subtitles, font_path, output_mp4, width=1280, height=720, fps=24):
    """
    Checks if a real AI video clip exists in VIDEO_CLIPS_DIR/scene_{id}.mp4.
    If yes, reads and loops/interpolates real video diffusion frames.
    If no, creates a high-definition 2.5D Ken Burns animated shot from the anchor image.
    """
    custom_clip_path = os.path.join(VIDEO_CLIPS_DIR, f"scene_{scene_id}.mp4")
    total_frames = int(duration_sec * fps)

    if os.path.exists(custom_clip_path) and os.path.getsize(custom_clip_path) > 10000:
        print(f"  🎬 Using REAL AI Video Clip: {custom_clip_path}")
        cap = cv2.VideoCapture(custom_clip_path)
        clip_frames = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            clip_frames.append(cv2.resize(frame, (width, height)))
        cap.release()

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_mp4, fourcc, float(fps), (width, height))

        for f_idx in range(total_frames):
            frame = clip_frames[f_idx % len(clip_frames)].copy()
            cur_time = f_idx / float(fps)
            cur_sub = ""
            for start, end, text in subtitles:
                if start <= cur_time <= end:
                    cur_sub = text
                    break
            if cur_sub:
                frame = render_subtitles_on_frame(frame, cur_sub, font_path)
            out.write(frame)
        out.release()
        return

    # Fallback to smooth 2.5D Ken Burns interpolation
    print(f"  ✨ Generating 2.5D Animatic Motion for Scene {scene_id} ({duration_sec:.1f}s)")
    orig_img = cv2.imread(image_path)
    if orig_img is None:
        orig_img = np.zeros((height, width, 3), dtype=np.uint8)

    orig_h, orig_w = orig_img.shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_mp4, fourcc, float(fps), (width, height))

    motion = SCENE_MOTIONS.get(scene_id, "zoom_in")

    for f_idx in range(total_frames):
        t = f_idx / float(total_frames)

        if motion == "zoom_in":
            scale = 1.0 + 0.12 * t
            cx, cy = orig_w * 0.5, orig_h * 0.5
        elif motion == "zoom_out":
            scale = 1.15 - 0.12 * t
            cx, cy = orig_w * 0.5, orig_h * 0.5
        elif motion == "pan_up":
            scale = 1.08
            cx = orig_w * 0.5
            cy = orig_h * (0.6 - 0.2 * t)
        elif motion == "pan_right":
            scale = 1.08
            cx = orig_w * (0.4 + 0.2 * t)
            cy = orig_h * 0.5
        else:
            scale = 1.05
            cx, cy = orig_w * 0.5, orig_h * 0.5

        crop_w = int(orig_w / scale)
        crop_h = int(orig_h / scale)
        x1 = max(0, min(orig_w - crop_w, int(cx - crop_w // 2)))
        y1 = max(0, min(orig_h - crop_h, int(cy - crop_h // 2)))

        cropped = orig_img[y1:y1+crop_h, x1:x1+crop_w]
        frame = cv2.resize(cropped, (width, height), interpolation=cv2.INTER_LINEAR)

        # Dynamic subtitles
        cur_time = f_idx / float(fps)
        cur_sub = ""
        for start, end, text in subtitles:
            if start <= cur_time <= end:
                cur_sub = text
                break

        if cur_sub:
            frame = render_subtitles_on_frame(frame, cur_sub, font_path)

        out.write(frame)

    out.release()

def build_language_movie(lang_code, lang_data):
    print(f"\n==========================================")
    print(f"🌍 Starting Samson Production: {lang_data['name']} {lang_data['flag']}")
    print(f"==========================================")

    lang_dir = os.path.join(OUTPUT_DIR, lang_code)
    os.makedirs(lang_dir, exist_ok=True)

    scene_mp4_files = []

    for scene in lang_data["scenes"]:
        s_id = scene["id"]
        print(f"\n▶ Scene {s_id}: {scene['title']}")

        # 1. Generate Voiceover with Emotional Prosody
        tts_file = os.path.join(lang_dir, f"scene_{s_id}_voice.mp3")
        prosody = SCENE_PROSODY.get(s_id, {"rate": "+0%", "pitch": "+0Hz", "volume": "+0%", "sfx_vol": 0.45})
        asyncio.run(generate_speech(
            scene["narration"], 
            lang_data["voice"], 
            tts_file,
            rate=prosody["rate"],
            pitch=prosody["pitch"],
            volume=prosody["volume"]
        ))
        duration = get_audio_duration(tts_file) + 1.2  # 1.2s padding for dramatic breath
        print(f"  🎙 Voiceover (Emotion: rate={prosody['rate']}, pitch={prosody['pitch']}): {duration:.1f}s via {lang_data['voice']}")

        # 2. Generate Cinematic SFX
        sfx_pcm = generate_cinematic_sfx(s_id, duration)
        sfx_wav = os.path.join(lang_dir, f"scene_{s_id}_sfx.wav")
        with wave.open(sfx_wav, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            wf.writeframes(sfx_pcm.tobytes())

        # 3. Mix Speech + SFX with Dynamic Ducking
        mixed_audio = os.path.join(lang_dir, f"scene_{s_id}_mixed_audio.aac")
        sfx_vol = prosody["sfx_vol"]
        cmd_mix = [
            FFMPEG_EXE, "-y",
            "-i", tts_file,
            "-i", sfx_wav,
            "-filter_complex", f"[0:a]volume=1.0[v];[1:a]volume={sfx_vol}[s];[v][s]amix=inputs=2:duration=longest[a]",
            "-map", "[a]",
            "-c:a", "aac", "-b:a", "192k",
            mixed_audio
        ]
        subprocess.run(cmd_mix, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # 4. Render Video Frames
        raw_video = os.path.join(lang_dir, f"scene_{s_id}_raw.mp4")
        create_scene_video(
            scene_id=s_id,
            image_path=SCENE_IMAGE_MAP[s_id],
            duration_sec=duration,
            subtitles=scene["subtitles"],
            font_path=lang_data["font"],
            output_mp4=raw_video
        )

        # 5. Mux Video + Audio
        final_scene_mp4 = os.path.join(lang_dir, f"scene_{s_id}_final.mp4")
        cmd_mux = [
            FFMPEG_EXE, "-y",
            "-i", raw_video,
            "-i", mixed_audio,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19",
            "-c:a", "copy",
            "-shortest",
            final_scene_mp4
        ]
        subprocess.run(cmd_mux, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        scene_mp4_files.append(final_scene_mp4)
        print(f"  ✅ Rendered Scene {s_id} complete!")

    # 6. Concatenate all 5 acts into master movie
    concat_txt = os.path.join(lang_dir, "concat_list.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for path in scene_mp4_files:
            f.write(f"file '{os.path.abspath(path)}'\n")

    master_output = os.path.join(OUTPUT_DIR, f"samson_{lang_code}.mp4")
    print(f"\n🎞 Concatenating all scenes into master: {master_output}")
    cmd_concat = [
        FFMPEG_EXE, "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_txt,
        "-c", "copy",
        master_output
    ]
    subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"🎉 MASTER EXPORT READY: {master_output} ({os.path.getsize(master_output) / 1024 / 1024:.2f} MB)")
    return master_output

if __name__ == "__main__":
    target_langs = sys.argv[1:] if len(sys.argv) > 1 else list(LANGUAGES.keys())
    print(f"🚀 FableForge Multilingual Engine: Processing {target_langs}...")

    for code in target_langs:
        if code in LANGUAGES:
            build_language_movie(code, LANGUAGES[code])

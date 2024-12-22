#!python3

# alloy, echo, fable, onyx, nova, and shimmer

import os
import io
import re

# from icecream import ic

from dotenv import load_dotenv
load_dotenv('config.env')

from openai import OpenAI

from pydub import AudioSegment
from pydub.playback import play
from pydub import effects

import librosa
import soundfile as sf

import numpy as np

def make_safe_fname(text):
    safe_text = re.sub(r'[\\/:*?"<>|]', '_', text + voice)
    safe_text = safe_text.replace('\n', '_').replace('\r', '_')
    return "cache/" + f"{safe_text}.mp3"

def make_safe_slow_fname(text):
    safe_text = re.sub(r'[\\/:*?"<>|]', '_', text + voice)
    safe_text = safe_text.replace('\n', '_').replace('\r', '_')
    return "cache/" + f"{safe_text}" + "_slow.mp3"

def openai_tts(text,voice):
    fname = make_safe_fname(text)

    client = OpenAI(api_key=os.getenv('OPENAI_KEY'))

    if os.path.exists(fname):
        return AudioSegment.from_file(fname, format="mp3")
    else:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        audio_buffer = io.BytesIO(response.content)
        audio = AudioSegment.from_file(audio_buffer, format="mp3")
        audio.export(fname, format="mp3")
        return audio

def slow(text):
    fname = make_safe_fname(text)
    slow_fname = make_safe_slow_fname(text)

    audio, sr = librosa.load(fname)
    slower_audio = librosa.effects.time_stretch(audio, rate=0.8)
    sf.write("output_slow.wav", slower_audio, sr)

file_path = "scenario.md"
voice = "alloy" # alloy, echo, fable, onyx, nova, and shimmer
# all = AudioSegment.silent(duration=500)
all =  AudioSegment.from_file("material/決定ボタンを押す3.mp3", format="mp3")

try:
    with open(file_path, 'r', encoding='utf-8') as file:
        for i, line in enumerate(file, start=1):

            if line.startswith(" "):
                pass

            elif line.startswith("#") or line.startswith("pause:"):
                audio = AudioSegment.silent(duration=3000)

            elif line.startswith("voice:"):
                voice = line.split(":", 1)[1].strip()

            elif len(line.strip()) > 1:
                audio = openai_tts(line,voice)
                alen = len(audio)
                silence = AudioSegment.silent(
                    duration=1000 * (alen/1000) - alen + 1000) # 1秒ごとに次の音が始まる
                all = all + audio + silence

                all = all + audio + silence

    all.export("scenario/audio.mp3", format="mp3")
    play(all)

except Exception as e:
    print(f"エラーが発生しました: {e}")

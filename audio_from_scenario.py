#!python3

import os
import io
import re

import fire
from icecream import ic

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
    safe_text = re.sub(r'[\\/:*?"<>|]', '_', text)
    safe_text = safe_text.replace('\n', '_').replace('\r', '_')
    return "cache/" + f"{safe_text}.mp3"

def make_safe_slow_fname(text):
    safe_text = re.sub(r'[\\/:*?"<>|]', '_', text)
    safe_text = safe_text.replace('\n', '_').replace('\r', '_')
    return "cache/" + f"{safe_text}" + "_slow.mp3"

def is_korean(text):
    for char in text:
        # Check if the character is in the Hangul unicode range
        if '\uAC00' <= char <= '\uD7A3':
            return True
    return False

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

def command(fire=False):

    voice = "alloy" # alloy, echo, fable, onyx, nova, and shimmer
    file_path = "scenario.md"
    # all = AudioSegment.silent(duration=500)
    audio =  AudioSegment.from_file("material/決定ボタンを押す3.mp3", format="mp3")
    alen = len(audio)
    duration = 1875 - alen
    silence = AudioSegment.silent(duration=duration)            
    all = audio + silence

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for i, line in enumerate(file, start=1):
                  
                if line.startswith(" "):
                    pass

                elif is_korean(line) is False:
                    pass

                #elif line.startswith("#") or line.startswith("pause:"):
                #    #audio = AudioSegment.silent(duration=3000)
                #    pass

                elif line.startswith("voice:"):
                    voice = line.split(":", 1)[1].strip()
                    ic(voice)

                elif len(line.strip()) > 0:
                    audio = openai_tts(line,voice)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
                    alen = len(audio)

                    if alen * 2 < 1875:
                        duration = 1875 - (alen * 2) + alen
                    else:
                        #duration = alen
                        duration = 1875

                    silence = AudioSegment.silent(duration = duration)
                    all = all + audio + silence

                    all = all + audio + silence # 同じ音声を2回再生する

        all.export("scenario/audio.mp3", format="mp3")

        if fire:
            play(all)

    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":

    fire.Fire(command)
#!/usr/bin/env python3

import io
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import fire
from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment


PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / "config.env")


def make_safe_fname(text, cache_dir=PROJECT_DIR / "cache"):
	safe_text = re.sub(r'[\\/:*?"<>|]', "_", text)
	safe_text = safe_text.replace("\n", "_").replace("\r", "_")
	safe_text = safe_text.replace("# ", "")
	return Path(cache_dir) / f"{safe_text}.mp3"


def openai_tts(text, voice="alloy", cache_dir=PROJECT_DIR / "cache"):
	cache_dir.mkdir(parents=True, exist_ok=True)
	cache_path = make_safe_fname(text, cache_dir)
	if cache_path.exists():
		return AudioSegment.from_file(cache_path, format="mp3")

	api_key = os.getenv("OPENAI_KEY")
	if not api_key:
		raise RuntimeError(
			f"音声キャッシュがありません。config.envにOPENAI_KEYを設定してください: {cache_path}"
		)

	client = OpenAI(api_key=api_key)
	response = client.audio.speech.create(
		model="tts-1", 
		voice=voice, 
		input=text,
		speed=1.0)
	audio = AudioSegment.from_file(io.BytesIO(response.content), format="mp3")
	audio.export(cache_path, format="mp3")
	return audio


def parse_titles(scenario_path):
	titles = []
	voice = "alloy"
	with open(scenario_path, encoding="utf-8") as scenario_file:
		for line_number, line in enumerate(scenario_file, start=1):
			stripped = line.strip()
			if stripped == "# exit":
				break
			elif stripped.startswith("voice:"):
				voice = stripped.split(":", 1)[1].strip()
			elif re.match(r"^#\s+", line) and stripped != "#":
				title = re.sub(r"^#\s+", "", stripped)
				titles.append({"text": title, "voice": voice, "line": line_number})
	return titles


def natural_sort_key(path):
	return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", path.name)]


def find_images(image_dir):
	image_paths = [*Path(image_dir).glob("*.png"), *Path(image_dir).glob("*.jpg"), *Path(image_dir).glob("*.jpeg")]
	return sorted(set(image_paths), key=natural_sort_key)


def speech_with_pause(audio, repeats=2):
	if repeats < 1:
		raise ValueError("repeatsは1以上で指定してください")
	pause = AudioSegment.silent(duration=1000)
	return sum((audio + pause for _ in range(repeats)), AudioSegment.empty())


def make_slide_audio(title, index, cache_dir, intro_path):
	audio = openai_tts(title["text"], title["voice"], cache_dir)
	segment = speech_with_pause(audio)

	if index == 0 and intro_path.exists():
		intro = AudioSegment.from_file(intro_path, format="mp3")
		segment = intro + AudioSegment.silent(duration=1000) + segment
	return segment


def run_ffmpeg(images, audio_paths, output_path, fps=30):
	ffmpeg = shutil.which("ffmpeg")
	if not ffmpeg:
		raise RuntimeError("ffmpegが見つかりません。FFmpegをインストールしてください。")

	with tempfile.TemporaryDirectory(prefix="make_mp4_") as temp_dir:
		concat_path = Path(temp_dir) / "images.txt"
		lines = []
		for image_path, audio_path in zip(images, audio_paths):
			duration = probe_duration(audio_path)
			lines.extend([
				f"file '{image_path.resolve()}'",
				f"duration {duration:.6f}",
			])
		lines.append(f"file '{images[-1].resolve()}'")
		concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

		combined_audio = Path(temp_dir) / "audio.wav"
		combined_segment = AudioSegment.empty()
		for audio_path in audio_paths:
			combined_segment += AudioSegment.from_file(audio_path, format="wav")
		combined_segment.export(combined_audio, format="wav")
		output_path.parent.mkdir(parents=True, exist_ok=True)
		subprocess.run(
			[
				ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_path),
				"-i", str(combined_audio), "-map", "0:v:0", "-map", "1:a:0",
				"-fps_mode", "vfr", "-c:v", "libx264", "-pix_fmt", "yuv420p",
				"-c:a", "aac", "-shortest", str(output_path),
			],
			check=True,
			stdout=subprocess.DEVNULL,
			stderr=subprocess.PIPE,
		)


def probe_duration(audio_path):
	ffprobe = shutil.which("ffprobe")
	if not ffprobe:
		raise RuntimeError("ffprobeが見つかりません。FFmpegをインストールしてください。")
	result = subprocess.run(
		[ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)],
		check=True,
		capture_output=True,
		text=True,
	)
	return float(result.stdout.strip())


def command(
	scenario="scenario.md",
	image_dir="scenario",
	output="scenario/scenario.mp4",
	cache_dir="cache",
):
	scenario_path = Path(scenario)
	titles = parse_titles(scenario_path)
	images = find_images(image_dir)
	if not titles:
		raise RuntimeError(f"# 見出しが見つかりません: {scenario_path}")
	if len(images) > len(titles):
		images = images[:len(titles)]
	if len(titles) != len(images):
		raise RuntimeError(f"タイトル数({len(titles)})と画像数({len(images)})が一致しません: {image_dir}")

	cache_path = Path(cache_dir)
	intro_path = PROJECT_DIR / "material" / "決定ボタンを押す3.mp3"
	with tempfile.TemporaryDirectory(prefix="make_mp4_audio_") as temp_dir:
		audio_paths = []
		for index, title in enumerate(titles):
			audio_path = Path(temp_dir) / f"slide_{index + 1:03d}.wav"
			make_slide_audio(title, index, cache_path, intro_path).export(audio_path, format="wav")
			audio_paths.append(audio_path)
		run_ffmpeg(images, audio_paths, Path(output))
	print(f"動画を生成しました: {output}")


if __name__ == "__main__":
	fire.Fire(command)

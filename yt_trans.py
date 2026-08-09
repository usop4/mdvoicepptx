#!/Users/user/Documents/hangul/venv/bin/python3
import os
import sys
import argparse
import subprocess
import yt_dlp
from faster_whisper import WhisperModel

# YouTube-to-Transcription Script
# 1. Downloads audio from YouTube (mp3)
# 2. Trims first 30 seconds
# 3. Transcribes using faster-whisper (Korean)
#
# Usage:
#   python3 yt_trans.py <youtube_url> [--output_dir DIR] [--trim_seconds SEC]

def download_audio(url, output_dir):
    """
    Download audio from YouTube using yt-dlp.
    Returns the path to the downloaded mp3 file.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'quiet': False,
        'noplaylist': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        # yt-dlp replaces extension with mp3
        filename = ydl.prepare_filename(info_dict)
        base, _ = os.path.splitext(filename)
        mp3_path = base + ".mp3"
        return mp3_path

def trim_audio(input_path, duration=60):
    """
    Trim the first N seconds of the audio file using ffmpeg.
    Returns the path to the trimmed file.
    """
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_top{duration}s{ext}"
    
    # Check if file already exists to avoid overwriting or redundant processing
    if os.path.exists(output_path):
        print(f"Trimmed file already exists: {output_path}")
        return output_path

    cmd = [
        'ffmpeg', '-y', '-i', input_path,
        '-t', str(duration),
        '-c', 'copy',
        output_path
    ]
    
    print(f"Trimming first {duration} seconds...")
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(f"Error trimming audio: {e}")
        return None
        
    return output_path

def transcribe_audio(audio_path, language='ko', model_size='medium'):
    """
    Transcribe audio file using faster-whisper.
    Saves transcription to a .txt file with the same base name.
    """
    output_txt_path = os.path.splitext(audio_path)[0] + '.txt'
    
    print(f"Loading Whisper model ({model_size})...")
    # Using 'int8' for CPU efficiency as per previous context
    model = WhisperModel(model_size, device='cpu', compute_type='int8')
    
    print(f"Transcribing: {audio_path}...")
    segments, info = model.transcribe(audio_path, beam_size=5, language=language)
    
    print(f"Detected language: {info.language} with probability {info.language_probability:.2f}")
    
    with open(output_txt_path, 'w', encoding='utf-8') as f:
        for segment in segments:
            line = f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text.strip()}"
            print(line)
            f.write(line + '\n')
            
    print(f"Transcription saved to: {output_txt_path}")
    return output_txt_path

def main():
    parser = argparse.ArgumentParser(description="Download YouTube audio, trim, and transcribe (Korean).")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--output_dir", default="/Users/user/Documents/hangul/youtube", help="Directory to save files")
    parser.add_argument("--trim_seconds", type=int, default=None, help="Seconds to trim from start (default: None - no trimming)")
    parser.add_argument("--model", default="medium", help="Whisper model size (default: medium)")
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    print(f"Processing URL: {args.url}")
    
    # 1. Download
    try:
        mp3_path = download_audio(args.url, args.output_dir)
        print(f"Downloaded: {mp3_path}")
    except Exception as e:
        print(f"Download failed: {e}")
        return

    # 2. Trim (if specified)
    audio_to_transcribe = mp3_path
    if args.trim_seconds is not None:
        trimmed_path = trim_audio(mp3_path, duration=args.trim_seconds)
        if not trimmed_path:
            print("Trimming failed.")
            return
        print(f"Trimmed file: {trimmed_path}")
        audio_to_transcribe = trimmed_path
    else:
        print("Trimming skipped (--trim_seconds not specified)")

    # 3. Transcribe
    try:
        transcribe_audio(audio_to_transcribe, language='ko', model_size=args.model)
    except Exception as e:
        print(f"Transcription failed: {e}")

if __name__ == "__main__":
    main()

from flask import Flask, request, jsonify
import os
import subprocess
from vosk import Model, KaldiRecognizer
import wave
import json
import boto3
import time
import hashlib
from transformers import pipeline
import ffmpeg
import threading

# ========== Flask Setup ==========
app = Flask(__name__)

# ========== Processing Status Tracking ==========
processing_status = {}

# ========== AWS S3 Upload ==========
def upload_to_s3(file_path, bucket_name, s3_key):
    s3 = boto3.client('s3')
    try:
        s3.upload_file(file_path, bucket_name, s3_key)
        print(f"[+] Uploaded {file_path} to s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print("[-] Upload failed:", e)

# ========== Step 1: Download YouTube Video ==========
def download_youtube_video(url, output_path='video.mp4'):
    print("[*] Downloading video...")
    subprocess.run([
    'yt-dlp',
    '--cookies', 'cookies.txt',
    '-f', 'best',
    '--no-playlist',
    '--quiet',
    '--no-warnings',
    '--restrict-filenames',
    '--no-call-home',
    '-o', output_path,
    url
    ], check=True)
    print("[*] Video downloaded.")

# ========== Step 2: Extract Audio ==========
def extract_audio(video_path='video.mp4', audio_path='audio.wav'):
    print("[*] Extracting audio...")
    subprocess.run([
        'ffmpeg', '-y', '-i', video_path, '-vn',
        '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', audio_path
    ], check=True)
    print("[*] Audio extracted.")

# ========== Step 3: Transcribe with Vosk ==========
def transcribe_audio(audio_path='audio.wav'):
    print("[*] Transcribing audio with Vosk...")

    if not os.path.exists("model"):
        return "[Error: Vosk model not found]"

    wf = wave.open(audio_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
        return "[Error: Audio must be WAV with 16kHz mono PCM]"

    model = Model("model")
    rec = KaldiRecognizer(model, wf.getframerate())

    results = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            results.append(json.loads(rec.Result()))
    results.append(json.loads(rec.FinalResult()))

    transcript = " ".join([res.get("text", "") for res in results])
    print("[*] Transcription complete.")
    return transcript

# ========== Step 4: QA with DistilBERT ==========
def ask_question(transcript, question):
    print("[*] Answering question...")
    qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
    result = qa_pipeline(question=question, context=transcript)
    return result['answer']

# ========== Cleanup ==========
def remove_local_file(path):
    try:
        os.remove(path)
        print(f"[−] Deleted local file: {path}")
    except FileNotFoundError:
        print(f"[!] File not found for deletion: {path}")

# ========== Full Pipeline ==========
def run_pipeline_for_url(youtube_url, bucket_name='eira1-general-dataset'):
    print(f"\n[+] Starting pipeline for: {youtube_url}")

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    unique_id = hashlib.md5(youtube_url.encode()).hexdigest()[:6] + "-" + timestamp

    video_file = 'video.mp4'
    audio_file = 'audio.wav'
    transcript_file = 'transcript.txt'
    pairs_dir = f'fps3_filter_media_extraction_{unique_id}'

    # Step 1
    print("[*] Step 1: Downloading video...")
    download_youtube_video(youtube_url, video_file)
    print("[✓] Video downloaded")

    # Step 2
    print("[*] Step 2: Extracting audio...")
    extract_audio(video_file, audio_file)
    print("[✓] Audio extracted")

    # Step 3
    print("[*] Step 3: Uploading video to S3...")
    upload_to_s3(video_file, bucket_name, f'videos/{unique_id}/{video_file}')
    print("[✓] Video uploaded")

    print("[*] Step 3: Uploading audio to S3...")
    upload_to_s3(audio_file, bucket_name, f'audio/{unique_id}/{audio_file}')
    print("[✓] Audio uploaded")

    # Step 4: Extract frames and audio pairs
    print("[*] Step 4: Extracting frames and audio pairs...")
    pairs = extract_fps_frames_and_audio_chunks(video_file, pairs_dir, fps=3)
    print(f"[✓] Extracted {len(pairs)} frame & audio pairs.")

    # Step 5: Upload pairs to S3
    print("[*] Step 5: Uploading frame/audio pairs to S3...")
    for frame_path, audio_path in pairs:
        frame_key = f'pairs/{unique_id}/{os.path.basename(frame_path)}'
        audio_key = f'pairs/{unique_id}/{os.path.basename(audio_path)}'
        upload_to_s3(frame_path, bucket_name, frame_key)
        upload_to_s3(audio_path, bucket_name, audio_key)
    print("[✓] Frame/audio pairs uploaded.")

    # Cleanup pairs dir
    for frame_path, audio_path in pairs:
        remove_local_file(frame_path)
        remove_local_file(audio_path)
    if os.path.exists(pairs_dir):
        try:
            os.rmdir(pairs_dir)
        except Exception:
            pass

    remove_local_file(video_file)

    # Step 6
    print("[*] Step 6: Transcribing audio...")
    transcript = transcribe_audio(audio_file)
    print("[✓] Transcript obtained")

    # Step 7
    with open(transcript_file, 'w') as f:
        f.write(transcript)
    upload_to_s3(transcript_file, bucket_name, f'transcripts/{unique_id}/{transcript_file}')
    remove_local_file(audio_file)
    remove_local_file(transcript_file)

    print("\nTRANSCRIPT PREVIEW:\n", transcript[:500], "...\n")
    print(f"[✓] Finished processing {youtube_url}")
# ========== FPS Frame/Audio Extraction ========== 
def extract_fps_frames_and_audio_chunks(video_path, output_dir, fps=3):
    os.makedirs(output_dir, exist_ok=True)
    frame_pattern = os.path.join(output_dir, "frame_%010.3f.jpg")
    raw_frames_pattern = os.path.join(output_dir, "frame_%03d.jpg")
    subprocess.run([
        "ffmpeg", "-i", video_path,
        "-vf", f"fps={fps},showinfo",
        "-vsync", "vfr",
        raw_frames_pattern,
        "-hide_banner", "-loglevel", "info"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    timestamps = []
    log_output = subprocess.run([
        "ffmpeg", "-i", video_path,
        "-vf", f"fps={fps},showinfo",
        "-f", "null", "-"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    for line in log_output.stderr.splitlines():
        if "showinfo" in line and "pts_time:" in line:
            import re
            m = re.search(r"pts_time:([0-9.]+)", line)
            if m:
                timestamps.append(float(m.group(1)))

    frame_files = sorted([f for f in os.listdir(output_dir) if f.startswith("frame_") and f.endswith(".jpg")])
    new_frame_files = []
    for fname, ts in zip(frame_files, timestamps):
        old_path = os.path.join(output_dir, fname)
        new_name = f"frame_{ts:010.3f}.jpg"
        new_path = os.path.join(output_dir, new_name)
        os.rename(old_path, new_path)
        new_frame_files.append((ts, new_path))

    pairs = []
    for ts, frame_path in new_frame_files:
        audio_path = os.path.join(output_dir, f"frame_{ts:010.3f}.wav")
        subprocess.run([
            "ffmpeg", "-i", video_path,
            "-ss", str(ts), "-t", "0.5",
            "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            "-vn", audio_path,
            "-hide_banner", "-loglevel", "error"
        ], check=True)
        pairs.append((frame_path, audio_path))
    return pairs


# ========== Batch Processing from TXT File ==========
def process_links_from_file(txt_file, bucket_name='eira1-general-dataset'):
    with open(txt_file, 'r') as f:
        links = [line.strip() for line in f if line.strip()]
    print(f"Found {len(links)} links in {txt_file}. Starting batch processing...")
    for idx, link in enumerate(links):
        print(f"\nProcessing link {idx+1}/{len(links)}: {link}")
        try:
            run_pipeline_for_url(link, bucket_name)
        except Exception as e:
            print(f"[!] Error processing {link}: {e}")


if __name__ == "__main__":
    # Commented out Flask endpoints for batch mode
    # app.run(host='0.0.0.0', port=5000)
    txt_file = input("Enter path to TXT file with YouTube links: ").strip()
    process_links_from_file(txt_file)
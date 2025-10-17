import os
import subprocess
import ffmpeg

def extract_fps_frames_and_audio_chunks(video_path, output_dir, fps=2):
    """
    Extracts frames at a constant FPS and their corresponding audio chunks.
    Returns a list of (frame_path, audio_chunk_path) tuples.
    """
    os.makedirs(output_dir, exist_ok=True)

    # 1. Extract frames at given fps
    frame_pattern = os.path.join(output_dir, "frame_%010.3f.jpg")
    raw_frames_pattern = os.path.join(output_dir, "frame_%03d.jpg")
    subprocess.run([
        "ffmpeg", "-i", video_path,
        "-vf", f"fps={fps},showinfo",
        "-vsync", "vfr",
        raw_frames_pattern,
        "-hide_banner", "-loglevel", "info"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # 2. Parse showinfo output from log (embedded in stderr)
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

    # 3. Rename frame images to match their exact timestamp
    frame_files = sorted([f for f in os.listdir(output_dir) if f.startswith("frame_") and f.endswith(".jpg")])
    new_frame_files = []
    for fname, ts in zip(frame_files, timestamps):
        old_path = os.path.join(output_dir, fname)
        new_name = f"frame_{ts:010.3f}.jpg"
        new_path = os.path.join(output_dir, new_name)
        os.rename(old_path, new_path)
        new_frame_files.append((ts, new_path))

    # 4. Extract corresponding 0.5 sec audio for each timestamp
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


if __name__ == "__main__":
    video_path = "video.mp4"  # Your video file
    output_dir = "fps3_filter_media_extraction"
    fps = 3

    pairs = extract_fps_frames_and_audio_chunks(video_path, output_dir, fps)
    print(f"Extracted {len(pairs)} frame & audio pairs at {fps} FPS.")
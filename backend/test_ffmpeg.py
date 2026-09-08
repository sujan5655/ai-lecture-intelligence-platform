from pathlib import Path

from lectures.services.ffmpeg_service import extract_video

BASE_DIR = Path(__file__).resolve().parent

video_path = BASE_DIR / "test_video.mp4"
audio_path = BASE_DIR / "media" / "test_audio.wav"


result = extract_video(
    video_path=str(video_path),
    output_path=str(audio_path),
)

print("Audio extraction successful.")
print(f"Audio file: {result}")

if Path(result).exists():
    print("Output file exists.")
else:
    print("ERROR: Output file was not created.")
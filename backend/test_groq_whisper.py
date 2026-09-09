import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv(
    "GROQ_WHISPER_MODEL",
    "whisper-large-v3-turbo",
)

if not api_key:
    raise RuntimeError(
        "GROQ_API_KEY is not configured in .env"
    )


client = Groq(api_key=api_key)


BASE_DIR = Path(__file__).resolve().parent

audio_path = (
    BASE_DIR
    / "media"
    / "test_segments"
    / "does_not_exist.wav"
)


if not audio_path.exists():
    raise FileNotFoundError(
        f"Audio segment not found: {audio_path}"
    )


print("Sending audio to Groq Whisper...")
print(f"Audio: {audio_path}")
print(f"Model: {model}")


with open(audio_path, "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        file=audio_file,
        model=model,
        response_format="verbose_json",
        timestamp_granularities=["segment"],
    )


print("\nTRANSCRIPTION")
print("=" * 60)

print(f"Full text:\n{transcription.text}")

print("\nSEGMENTS")
print("=" * 60)


for segment in transcription.segments:
    print(
        f"[{segment['start']:.2f}s - "
        f"{segment['end']:.2f}s] "
        f"{segment['text']}"
    )


print("\nGroq Whisper test completed successfully.")
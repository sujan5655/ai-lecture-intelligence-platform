from pathlib import Path

from lectures.services.groq_service import transcribe_audio


BASE_DIR = Path(__file__).resolve().parent

audio_path = (
    BASE_DIR
    / "media"
    / "test_segments"
    / "segment_0000.wav"
)


result = transcribe_audio(
    audio_path=str(audio_path),
)


print("\nTRANSCRIPTION SERVICE TEST")
print("=" * 60)

print(f"Full text:\n{result['text']}")

print("\nTimestamped segments:")
print("-" * 60)

for segment in result["segments"]:
    print(
        f"[{segment['start']:.2f}s - "
        f"{segment['end']:.2f}s] "
        f"{segment['text']}"
    )

print("-" * 60)

print(
    f"Total Whisper segments: "
    f"{len(result['segments'])}"
)

print("\nGroq service test completed successfully.")
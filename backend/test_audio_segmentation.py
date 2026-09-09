from pathlib import Path

from lectures.services.audio_service import split_audio


BASE_DIR = Path(__file__).resolve().parent

audio_path = BASE_DIR / "media" / "test_audio.wav"

output_directory = (
    BASE_DIR
    / "media"
    / "test_segments"
)


segments = split_audio(
    audio_path=str(audio_path),
    output_directory=str(output_directory),
    segment_duration=15,
)


print("\nAUDIO SEGMENTS")
print("=" * 60)

for segment in segments:
    print(
        f"Sequence: {segment['sequence']}"
    )

    print(
        f"Start: {segment['start_time']:.2f}s"
    )

    print(
        f"End: {segment['end_time']:.2f}s"
    )

    print(
        f"File: {segment['path']}"
    )

    print("-" * 60)


print(
    f"\nTotal segments: {len(segments)}"
)
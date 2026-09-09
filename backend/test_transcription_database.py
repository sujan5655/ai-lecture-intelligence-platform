import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from lectures.models import Lecture, AudioSegment

from pathlib import Path

from django.core.files import File

from lectures.models import Lecture, AudioSegment
from lectures.services.transcription_service import (
    transcribe_audio_segment,
)


BASE_DIR = Path(__file__).resolve().parent

audio_path = (
    BASE_DIR
    / "media"
    / "test_segments"
    / "segment_0000.wav"
)


if not audio_path.exists():
    raise FileNotFoundError(
        f"Audio file not found: {audio_path}"
    )


# --------------------------------------------------
# 1. Create test lecture
# --------------------------------------------------

lecture = Lecture.objects.create(
    title="Transcription Test Lecture"
)


# --------------------------------------------------
# 2. Create AudioSegment
# --------------------------------------------------

audio_segment = AudioSegment(
    lecture=lecture,
    sequence=1,
    start_time=0,
    end_time=15,
)


with open(audio_path, "rb") as audio_file:
    audio_segment.audio_file.save(
        audio_path.name,
        File(audio_file),
        save=True,
    )


print("\nAudio segment created.")
print(f"Lecture ID: {lecture.id}")
print(f"Audio Segment ID: {audio_segment.id}")
print(f"Stored file: {audio_segment.audio_file.name}")


# --------------------------------------------------
# 3. Transcribe
# --------------------------------------------------

print("\nSending audio to Groq Whisper...")

transcript_segments = (
    transcribe_audio_segment(
        audio_segment
    )
)


# --------------------------------------------------
# 4. Display results
# --------------------------------------------------

print("\nDATABASE TRANSCRIPTION TEST")
print("=" * 60)

print(f"Lecture ID: {lecture.id}")
print(f"Audio Segment ID: {audio_segment.id}")

print("\nTranscript segments:")
print("-" * 60)

for segment in transcript_segments:
    print(
        f"[{segment.start_time:.2f}s - "
        f"{segment.end_time:.2f}s] "
        f"{segment.text}"
    )

print("-" * 60)

print(
    f"Total transcript segments: "
    f"{len(transcript_segments)}"
)

print("\nDatabase transcription test completed successfully.")
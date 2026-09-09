from lectures.models import AudioSegment, TranscriptSegment
from lectures.services.groq_service import transcribe_audio


def transcribe_audio_segment(audio_segment: AudioSegment):
    """
    Transcribe one AudioSegment and save its
    timestamped transcript to PostgreSQL.
    """

    result = transcribe_audio(
        audio_path=audio_segment.audio_file.path
    )

    transcript_segments = []

    for segment in result["segments"]:
        relative_start = segment["start"]
        relative_end = segment["end"]

        absolute_start = (
            audio_segment.start_time
            + relative_start
        )

        absolute_end = (
            audio_segment.start_time
            + relative_end
        )

        transcript_segment = TranscriptSegment.objects.create(
            audio_segment=audio_segment,
            start_time=absolute_start,
            end_time=absolute_end,
            text=segment["text"],
        )

        transcript_segments.append(
            transcript_segment
        )

    return transcript_segments
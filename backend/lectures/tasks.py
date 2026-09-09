from celery import shared_task

@shared_task
def task_celery_task():
  print("Celery task is running ")
  return {
    "status":"Success",
    "message":"Celery is working correctly"
  }

from django.db import transaction
from lectures.models import AudioSegment,TranscriptSegment
from lectures.services.groq_service import transcribe_audio

MAX_RETRIES=3
@shared_task(
    bind=True,
    max_retries=MAX_RETRIES,
)
def transcribe_audio_segment_task(
    self,
    audio_segment_id,
):
    try:
        audio_segment = AudioSegment.objects.get(
            id=audio_segment_id
        )

    except AudioSegment.DoesNotExist:
        return {
            "status": "failed",
            "message": (
                f"AudioSegment "
                f"{audio_segment_id} does not exist"
            ),
        }

    try:
        # Mark segment as processing
        audio_segment.status = "processing"
        audio_segment.last_error = None

        audio_segment.save(
            update_fields=[
                "status",
                "last_error",
                "updated_at",
            ]
        )

        # Transcribe audio using Groq
        result = transcribe_audio(
            audio_path=audio_segment.audio_file.path
        )

        with transaction.atomic():

            # Remove old transcript records if this task
            # is being retried.
            TranscriptSegment.objects.filter(
                audio_segment=audio_segment
            ).delete()

            transcript_objects = []

            # Build all TranscriptSegment objects
            for segment in result["segments"]:

                absolute_start = (
                    audio_segment.start_time
                    + float(segment["start"])
                )

                absolute_end = (
                    audio_segment.start_time
                    + float(segment["end"])
                )

                transcript_objects.append(
                    TranscriptSegment(
                        audio_segment=audio_segment,
                        start_time=absolute_start,
                        end_time=absolute_end,
                        text=segment["text"],
                    )
                )

            # IMPORTANT:
            # bulk_create is OUTSIDE the for loop.
            TranscriptSegment.objects.bulk_create(
                transcript_objects
            )

            # Mark as completed
            audio_segment.status = "completed"
            audio_segment.last_error = None

            audio_segment.save(
                update_fields=[
                    "status",
                    "last_error",
                    "updated_at",
                ]
            )

        return {
            "status": "completed",
            "audio_segment_id": audio_segment.id,
            "transcript_segments": len(
                transcript_objects
            ),
        }

    except Exception as exc:

        retry_count = self.request.retries + 1

        audio_segment.status = (
            "retrying"
            if retry_count <= MAX_RETRIES
            else "failed"
        )

        audio_segment.retry_count = retry_count
        audio_segment.last_error = str(exc)

        audio_segment.save(
            update_fields=[
                "status",
                "retry_count",
                "last_error",
                "updated_at",
            ]
        )

        if retry_count <= MAX_RETRIES:
            raise self.retry(
                exc=exc,
                countdown=10 * retry_count,
            )

        raise


@shared_task
def transcribe_lecture_task(lecture_id):
    """
    Queue transcription tasks for all audio segments
    belonging to a lecture.
    """

    from lectures.models import Lecture

    try:
        lecture = Lecture.objects.get(
            id=lecture_id
        )
    except Lecture.DoesNotExist:
        return {
            "status": "failed",
            "message": (
                f"Lecture {lecture_id} does not exist."
            ),
        }

    audio_segments = (
        lecture.audio_segments
        .order_by("sequence")
    )

    if not audio_segments.exists():
        return {
            "status": "failed",
            "message": (
                "No audio segments found "
                "for this lecture."
            ),
        }

    lecture.status = "transcribing"
    lecture.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    queued_tasks = []

    for audio_segment in audio_segments:

        # Already completed segments don't need
        # to be submitted again.
        if audio_segment.status == "completed":
            continue

        task = transcribe_audio_segment_task.delay(
            audio_segment.id
        )

        queued_tasks.append(
            {
                "audio_segment_id": audio_segment.id,
                "task_id": task.id,
            }
        )

    return {
        "status": "queued",
        "lecture_id": lecture.id,
        "total_segments": audio_segments.count(),
        "queued_segments": len(queued_tasks),
        "tasks": queued_tasks,
    }


@shared_task
def check_lecture_transcription_status(
    lecture_id,
):
    """
    Check whether all audio segments belonging
    to a lecture have been successfully transcribed.
    """

    from lectures.models import Lecture

    try:
        lecture = Lecture.objects.get(
            id=lecture_id
        )
    except Lecture.DoesNotExist:
        return {
            "status": "failed",
            "message": (
                f"Lecture {lecture_id} does not exist."
            ),
        }

    audio_segments = lecture.audio_segments.all()

    total = audio_segments.count()

    if total == 0:
        lecture.status = "failed"
        lecture.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return {
            "status": "failed",
            "message": "No audio segments found.",
        }

    completed = audio_segments.filter(
        status="completed"
    ).count()

    retrying = audio_segments.filter(
        status="retrying"
    ).count()

    processing = audio_segments.filter(
        status="processing"
    ).count()

    pending = audio_segments.filter(
        status="pending"
    ).count()

    failed = audio_segments.filter(
        status="failed"
    ).count()

    if failed > 0:

        lecture.status = "failed"

        lecture.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return {
            "status": "failed",
            "lecture_id": lecture.id,
            "total": total,
            "completed": completed,
            "retrying": retrying,
            "processing": processing,
            "pending": pending,
            "failed": failed,
        }

    if completed == total:

        lecture.status = "completed"

        lecture.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return {
            "status": "completed",
            "lecture_id": lecture.id,
            "total": total,
            "completed": completed,
        }

    return {
        "status": "processing",
        "lecture_id": lecture.id,
        "total": total,
        "completed": completed,
        "retrying": retrying,
        "processing": processing,
        "pending": pending,
        "failed": failed,
    }


@shared_task(
    bind=True,
    max_retries=3,
)
def process_lecture_slides_task(self, lecture_id):
    from lectures.models import Lecture
    from lectures.services.slide_service import (
        process_lecture_slides,
    )

    try:
        lecture = Lecture.objects.get(id=lecture_id)
    except Lecture.DoesNotExist:
        return {
            "status": "failed",
            "message": f"Lecture {lecture_id} does not exist.",
        }

    try:
        lecture.status = "processing_slides"
        lecture.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        slides = process_lecture_slides(
            lecture
        )

        lecture.status = "completed"
        lecture.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return {
            "status": "completed",
            "lecture_id": lecture.id,
            "slides_created": len(slides),
        }

    except Exception as exc:
        lecture.status = "failed"
        lecture.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        if self.request.retries < self.max_retries:
            raise self.retry(
                exc=exc,
                countdown=10 * (
                    self.request.retries + 1
                ),
            )

        raise
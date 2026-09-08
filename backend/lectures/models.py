from django.db import models

# Create your models here.
class Lecture(models.Model):
  STATUS_CHOICES=[
    ("uploaded","Uploaded"),
    ("processing","Processing"),
    ("transcribing","Transcribing"),
    ("processing_slides","Processing Slides"),
    ("generating_notes","Generating Notes"),
    ("generating_quiz","Generating Quiz"),
    ("completed","Completed"),
    ("failed","Failed")
  ]
  title=models.CharField(max_length=255)
  video=models.FileField(
    upload_to="lectures/videos",
    blank=True,
    null=True,
    max_length=2000
  )
  slides_source=models.FileField(
    upload_to="lectures/slide_sources/",
    blank=True,
    null=True,
    max_length=3000
  )
  status=models.CharField(
    max_length=30,
    choices=STATUS_CHOICES,
    default="uploaded"
  )
  created_at=models.DateTimeField(auto_now_add=True)
  updated_at=models.DateTimeField(auto_now=True)
  def __str__(self):
    return self.title




class AudioSegment(models.Model):
  STATUS_CHOICES=[
    ("pending","Pending"),
    ("processing","Processing"),
    ("completed","Completed"),
    ("retrying","Retrying"),
    ("failed","Failed")
  ]
  lecture=models.ForeignKey(
    Lecture,
    on_delete=models.CASCADE,
    related_name="audio_segments"
  )
  sequence=models.PositiveBigIntegerField()
  audio_file=models.FileField(
    upload_to="lectures/audio_segments/"
  )
  start_time=models.FloatField()
  end_time=models.FloatField()
  status=models.CharField(
    max_length=20,
    choices=STATUS_CHOICES,
    default="pending"
  )
  retry_count=models.PositiveIntegerField(default=0)
  last_error=models.TextField(blank=True,null=True)
  created_at=models.DateTimeField(auto_now=True)
  updated_at=models.DateTimeField(auto_now=True)
  class Meta:
    ordering=["sequence"]
    constraints=[
      models.UniqueConstraint(
        fields=["lecture","sequence"],
        name="unique_lecture_audio_sequence"
      )
    ]
    def __str__(self):
      return (
        f"{self.lecture.title }--"
        f"Segment {self.sequence}"
      )
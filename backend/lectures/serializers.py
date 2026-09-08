from rest_framework import serializers
from .models import Lecture

class LectureSerializer(serializers.ModelSerializer):
  class Meta:
    model=Lecture
    fields=[
      "id",
      "title",
      "video",
      "slides_source",
      "status",
      "created_at",
      "updated_at"
    ]
    read_only_fields=[
      "id",
      "status",
      "created_at",
      "updated_at"
    ]
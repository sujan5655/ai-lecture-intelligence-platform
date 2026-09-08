from django.contrib import admin

# Register your models here.
from .models import Lecture

@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
  list_display=(
    "id",
    "title",
    "status",
    "created_at",
    "updated_at"
  )
  list_filter=["status"]
  search_fields=["title"]
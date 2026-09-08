from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view,parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser
from .serializers import LectureSerializer
from rest_framework import status
from .models import Lecture
@api_view(['GET'])
def health_check(request):
  return Response(
    {
      "status":"ok",
      "service":"lecture ai-backend"
    }
  )

@api_view(["POST"])
@parser_classes([MultiPartParser,FormParser])
def upload_lecture(request):
  serializer=LectureSerializer(data=request.data)
  if serializer.is_valid():
    lecture=serializer.save()
    return Response(
      {
        "message":"Lecture uploaded successfully",
        "lecture":serializer.data
      }
    )
  return Response({
    "message":"Lecture upload failed",
    "errors":serializer.errors
  },
status=status.HTTP_400_BAD_REQUEST
  )



@api_view(["POST"])
@parser_classes([MultiPartParser,FormParser])
def upload_slides(request,lecture_id):
  try:
    lecture=Lecture.objects.get(id=lecture_id)
  except Lecture.DoesNotExist:
    return Response(
      {
        "message":"Lecture not found"
      },
      status=status.HTTP_404_NOT_FOUND
    )
  slides_file=request.FILES.get("slides_source")
  if not slides_file:
    return Response(
      {
        "message":"No slide was provided"
      },
      status=status.HTTP_400_BAD_REQUEST
    )
  allowed_extensions=[".pdf",".pptx"]
  filename=slides_file.name.lower()
  if not filename.endswith((".pdf",".pptx")):
    return Response(
      {"message":"Only PDF and pptx files are allowed"},
      status=status.HTTP_400_BAD_REQUEST
    )
  lecture.slides_source=slides_file
  lecture.save(update_fields=['slides_source','updated_at'])
  return Response(
    {
      "message":"Slides are uploaded successfully",
      "lecture":LectureSerializer(lecture).data
    },
    status=status.HTTP_200_OK
  )


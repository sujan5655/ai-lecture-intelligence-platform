import subprocess
from pathlib import Path

def extract_video(video_path:str,output_path:str)->str:
  """
  Extract audio from a video using FFmpeg.
  Args:
    video_path:Absolute path to the input video.
    output_path:Absolute path where the audio will be created.
  Returns:
    The output audio path.
  Raises:
    FileNotFoundError:
      If the input video doesn't exist.
    RuntimeError: 
       If FFmpeg fails.
  """
  video =Path(video_path)
  output=Path(output_path)
  if not video.exists():
    raise FileNotFoundError(
      f"Video file not found:{video}"
    )
  output.parent.mkdir(
    parents=True,
    exist_ok=True
  )
  command=[
    "ffmpeg",
    "-y",
    "-i",
    str(video),
    "-vn",
    "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        str(output),
  ]
  result=subprocess.run(
    command,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
  )
  if result.returncode!=0:
    raise RuntimeError(
      f"FFmpeg audio extraction failed ;\n"
      f"{result.stderr}"
    )
  return str(output)



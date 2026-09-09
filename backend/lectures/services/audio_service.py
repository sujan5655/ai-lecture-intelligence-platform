import subprocess
from pathlib import Path
DEFAULT_SEGMENT_DURATION=15


def split_audio(audio_path:str,output_directory:str,segment_duration:int=DEFAULT_SEGMENT_DURATION):
  """
  Split an audio file into fixed-duration WAV segments.
  Returns a list of dictionaries containing:
    sequence
    path
    start_time
    end_time
  """
  audio=Path(audio_path)
  output_dir=Path(output_directory)
  if not audio.exists:
    raise FileNotFoundError(
      f"Audio file not found: {audio}"
    )
  if segment_duration<=0:
    raise ValueError(
      "Segment duration must be greater than zero"
    )
  output_dir.mkdir(
    parents=True,
    exist_ok=True
  )
  output_pattern=output_dir/"segment_%04d.wav"
  command=[
    "ffmpeg",
    "-y",
    "-i",
    str(audio),
    "-f",
    "segment",
    "-segment_time",
    str(segment_duration),
    "-reset_timestamps",
    "1",
    "-acodec",
    "pcm_s16le",
    "-ar","16000",
    "-ac",
    "1",
    str(output_pattern)
  ]
  result=subprocess.run(
    command,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
  )
  if result.returncode!=0:
    raise RuntimeError(
      "FFmpeg audio segmentation failed \n"
      f"{result.stderr}"
    )
  segment_files = sorted(
        output_dir.glob("segment_*.wav")
    )
  if not segment_files:
        raise RuntimeError(
            "FFmpeg completed but no audio segments were created."
        )

  segments = []

  for index, segment_file in enumerate(segment_files):
        start_time = index * segment_duration

        duration = get_audio_duration(
            str(segment_file)
        )

        end_time = start_time + duration

        segments.append(
            {
                "sequence": index + 1,
                "path": str(segment_file),
                "start_time": start_time,
                "end_time": end_time,
            }
        )

  return segments


def get_audio_duration(audio_path: str) -> float:
    """
    Get audio duration using ffprobe.
    """

    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        audio_path,
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Unable to determine audio duration:\n"
            f"{result.stderr}"
        )

    return float(result.stdout.strip())
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
  output_pattern=output_dir/"segment_%"
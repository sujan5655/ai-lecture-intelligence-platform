import os 
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
GROQ_WHISPER_MODEL=os.getenv("GROQ_WHISPER_MODEL","whisper-large-v3-turbo")
if not GROQ_API_KEY:
  raise RuntimeError(
    "GROQ_API_KEY is not configured"
  )
client=Groq(api_key=GROQ_API_KEY)

def transcribe_audio(
    audio_path: str,
):
    """
    Transcribe one audio file using Groq Whisper.

    Returns:
        {
            "text": "...",
            "segments": [...]
        }
    """

    audio = Path(audio_path)

    if not audio.exists():
        raise FileNotFoundError(
            f"Audio file not found: {audio}"
        )

    with open(audio, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model=GROQ_WHISPER_MODEL,
            response_format="verbose_json",
            timestamp_granularities=["segment"],
        )

    segments = []

    for segment in transcription.segments:
        segments.append(
            {
                "start": float(segment["start"]),
                "end": float(segment["end"]),
                "text": segment["text"].strip(),
            }
        )

    return {
        "text": transcription.text.strip(),
        "segments": segments,
    }

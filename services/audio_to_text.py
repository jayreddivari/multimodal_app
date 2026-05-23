"""Speech-to-text using OpenAI Whisper (local, free)."""

from __future__ import annotations

from pathlib import Path

from config import WHISPER_MODEL_SIZE


def transcribe(audio_path: Path, language: str | None = "en") -> str:
    import whisper

    model = whisper.load_model(WHISPER_MODEL_SIZE)
    options: dict = {}
    if language:
        options["language"] = language
    result = model.transcribe(str(audio_path), **options)
    return result.get("text", "").strip()

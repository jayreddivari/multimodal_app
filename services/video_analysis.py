"""Video understanding: frame captions + optional audio transcription."""

from __future__ import annotations

from pathlib import Path

from config import VIDEO_FRAME_SAMPLE_COUNT
from . import audio_to_text, image_to_text, text_to_text
from utils.media import sample_video_frames


def describe_video(
    video_path: Path,
    user_prompt: str = "Summarize what happens in this video.",
    frame_provider: str = "blip",
    max_frames: int | None = None,
) -> dict[str, str | list[str]]:
    """Return frame captions and an overall summary."""
    max_frames = max_frames or VIDEO_FRAME_SAMPLE_COUNT
    frames = sample_video_frames(video_path, max_frames=max_frames)

    captions: list[str] = []
    for i, frame in enumerate(frames, start=1):
        caption = image_to_text.describe(
            frame,
            prompt="Describe this video frame briefly.",
            provider=frame_provider,
        )
        captions.append(f"Frame {i}: {caption}")

    # Use text-to-text for summarization (auto-detects HuggingFace or Ollama)
    try:
        joined = "\n".join(captions)
        summary_prompt = f"{user_prompt}\n\nFrame captions:\n{joined}"
        summary = text_to_text.generate(summary_prompt)
    except Exception:
        summary = "\n".join(captions)

    return {"captions": captions, "summary": summary}


def transcribe_video_audio(video_path: Path) -> str:
    """Transcribe audio track from a video file (requires ffmpeg)."""
    return audio_to_text.transcribe(video_path)

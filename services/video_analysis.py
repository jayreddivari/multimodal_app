"""Video understanding: frame captions + optional audio transcription."""

from __future__ import annotations

from pathlib import Path

from multimodal_app.config import VIDEO_FRAME_SAMPLE_COUNT
from multimodal_app.services import audio_to_text, image_to_text, ollama_client
from multimodal_app.utils.media import sample_video_frames


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

    try:
        summary = ollama_client.summarize_texts(
            captions,
            instruction=user_prompt,
        )
    except Exception:
        summary = "\n".join(captions)

    return {"captions": captions, "summary": summary}


def transcribe_video_audio(video_path: Path) -> str:
    """Transcribe audio track from a video file (requires ffmpeg)."""
    return audio_to_text.transcribe(video_path)

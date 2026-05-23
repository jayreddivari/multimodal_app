"""Text-to-speech using edge-tts (free, no API key)."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from config import EDGE_TTS_VOICE


async def _synthesize_async(text: str, voice: str, output_path: Path) -> None:
    import edge_tts

    communicate = edge_tts.Communicate(text, voice=voice)
    await communicate.save(str(output_path))


def generate(text: str, voice: str | None = None) -> Path:
    """Return path to a generated MP3 file."""
    voice = voice or EDGE_TTS_VOICE
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        output = Path(tmp.name)
    asyncio.run(_synthesize_async(text, voice, output))
    return output

"""Configuration for the multimodal Streamlit app."""

from __future__ import annotations

import os
from pathlib import Path

_PACKAGE_DIR = Path(__file__).resolve().parent
_PARENT_DIR = _PACKAGE_DIR.parent

try:
    from dotenv import load_dotenv

    load_dotenv(_PARENT_DIR / ".env")
    load_dotenv(_PACKAGE_DIR / ".env", override=True)
except ImportError:
    # Streamlit Cloud secrets are env vars; dotenv is optional at runtime.
    pass


def _get_config_value(*keys: str, default: str | None = None) -> str | None:
    """Read from os.environ, then Streamlit secrets (Cloud does not ship .env)."""
    for key in keys:
        value = os.getenv(key)
        if value:
            return value
    try:
        import streamlit as st

        for key in keys:
            if key in st.secrets:
                return str(st.secrets[key])
    except Exception:
        pass
    return default


# Ollama (local, free)
OLLAMA_BASE_URL = _get_config_value("OLLAMA_BASE_URL", default="http://localhost:11434")
OLLAMA_CHAT_MODEL = _get_config_value("OLLAMA_CHAT_MODEL", default="llama3.1:8b")
OLLAMA_VISION_MODEL = _get_config_value("OLLAMA_VISION_MODEL", default="llava")

# Hugging Face (optional — Inference API free tier with token)
HUGGINGFACE_API_KEY = _get_config_value("HUGGINGFACE_API_KEY", "HF_TOKEN")

# Hugging Face model IDs (must support Inference Providers — see HF model page)
HF_TEXT_TO_IMAGE_MODEL = _get_config_value(
    "HF_TEXT_TO_IMAGE_MODEL", default="black-forest-labs/FLUX.1-schnell"
)
HF_TEXT_TO_TEXT_MODEL = _get_config_value(
    "HF_TEXT_TO_TEXT_MODEL", default="meta-llama/Llama-3.1-8B-Instruct"
)
# Optional: fal-ai, replicate, hf-inference, etc. Leave unset for "auto".
HF_INFERENCE_PROVIDER = _get_config_value("HF_INFERENCE_PROVIDER") or None
HF_IMAGE_TO_TEXT_MODEL = _get_config_value(
    "HF_IMAGE_TO_TEXT_MODEL", default="Salesforce/blip-image-captioning-base"
)

# Local model sizes (CPU-friendly defaults)
WHISPER_MODEL_SIZE = _get_config_value("WHISPER_MODEL_SIZE", default="base")
BLIP_MODEL_ID = HF_IMAGE_TO_TEXT_MODEL

# edge-tts voice
EDGE_TTS_VOICE = _get_config_value("EDGE_TTS_VOICE", default="en-US-AriaNeural")

# Video frame sampling
VIDEO_FRAME_SAMPLE_COUNT = int(
    _get_config_value("VIDEO_FRAME_SAMPLE_COUNT", default="6") or "6"
)

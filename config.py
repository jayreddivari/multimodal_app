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

# Ollama (local, free)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "llama3.1:8b")
OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava")

# Hugging Face (optional — Inference API free tier with token)
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN")

# Hugging Face model IDs (must support Inference Providers — see HF model page)
HF_TEXT_TO_IMAGE_MODEL = os.getenv(
    "HF_TEXT_TO_IMAGE_MODEL", "black-forest-labs/FLUX.1-schnell"
)
# Optional: fal-ai, replicate, hf-inference, etc. Leave unset for "auto".
HF_INFERENCE_PROVIDER = os.getenv("HF_INFERENCE_PROVIDER") or None
HF_IMAGE_TO_TEXT_MODEL = os.getenv(
    "HF_IMAGE_TO_TEXT_MODEL", "Salesforce/blip-image-captioning-base"
)

# Local model sizes (CPU-friendly defaults)
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
BLIP_MODEL_ID = HF_IMAGE_TO_TEXT_MODEL

# edge-tts voice
EDGE_TTS_VOICE = os.getenv("EDGE_TTS_VOICE", "en-US-AriaNeural")

# Video frame sampling
VIDEO_FRAME_SAMPLE_COUNT = int(os.getenv("VIDEO_FRAME_SAMPLE_COUNT", "6"))

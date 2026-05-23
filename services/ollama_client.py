"""Ollama API helpers for chat and vision."""

from __future__ import annotations

import ollama
from PIL import Image

from config import OLLAMA_BASE_URL, OLLAMA_CHAT_MODEL, OLLAMA_VISION_MODEL
from utils.media import image_to_bytes


def _client() -> ollama.Client:
    return ollama.Client(host=OLLAMA_BASE_URL)


def check_ollama_available() -> tuple[bool, str]:
    try:
        models = _client().list()
        names = [m.model for m in models.models]
        return True, ", ".join(names[:8]) + ("..." if len(names) > 8 else "")
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def text_to_text(prompt: str, system: str | None = None, model: str | None = None) -> str:
    model = model or OLLAMA_CHAT_MODEL
    messages: list[dict] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        response = _client().chat(model=model, messages=messages)
        return response.message.content
    except Exception as exc:
        raise RuntimeError(
            f"Ollama is not available at {OLLAMA_BASE_URL}. "
            "On Streamlit Cloud, use the Hugging Face provider and set "
            "HUGGINGFACE_API_KEY (or HF_TOKEN) in App Settings → Secrets. "
            "Locally, add the same key to .env."
        ) from exc


def image_to_text(
    image: Image.Image,
    prompt: str = "Describe this image in detail.",
    model: str | None = None,
) -> str:
    model = model or OLLAMA_VISION_MODEL
    image_bytes = image_to_bytes(image, fmt="JPEG")

    try:
        response = _client().chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_bytes],
                }
            ],
        )
        return response.message.content
    except Exception as exc:
        raise RuntimeError(
            f"Ollama is not available at {OLLAMA_BASE_URL}. "
            "Install BLIP locally or use Ollama with text_to_text generation."
        ) from exc


def summarize_texts(texts: list[str], instruction: str, model: str | None = None) -> str:
    joined = "\n".join(f"- {t}" for t in texts)
    prompt = f"{instruction}\n\nCaptions / notes:\n{joined}"
    return text_to_text(prompt, model=model or OLLAMA_CHAT_MODEL)

"""Image-to-text (captioning / VQA) via Ollama vision or local BLIP."""

from __future__ import annotations

from PIL import Image

from config import BLIP_MODEL_ID
from . import ollama_client


def _parse_pipeline_result(result) -> str:
    if isinstance(result, list) and result:
        item = result[0]
        if isinstance(item, dict):
            return item.get("generated_text") or item.get("text") or str(item)
        return str(item)
    if isinstance(result, dict):
        return result.get("generated_text") or result.get("text") or str(result)
    return str(result)


def _caption_with_blip_model(
    image: Image.Image, model_id: str, prompt: str | None = None
) -> str:
    """BLIP via processor/model (stable across transformers versions)."""
    import torch
    from transformers import BlipForConditionalGeneration, BlipProcessor

    processor = BlipProcessor.from_pretrained(model_id)
    model = BlipForConditionalGeneration.from_pretrained(model_id)
    model.eval()

    if prompt and prompt.strip():
        inputs = processor(image, text=prompt, return_tensors="pt")
    else:
        inputs = processor(image, return_tensors="pt")

    with torch.no_grad():
        output_ids = model.generate(**inputs, max_new_tokens=50)
    return processor.decode(output_ids[0], skip_special_tokens=True)


def _caption_with_pipeline(
    image: Image.Image, model_id: str, prompt: str | None = None
) -> str:
    """Fallback for non-BLIP captioning models."""
    from transformers import pipeline

    try:
        captioner = pipeline(model=model_id)
    except ValueError:
        captioner = pipeline("image-text-to-text", model=model_id)

    if prompt and prompt.strip():
        result = captioner(image, text=prompt)
    else:
        result = captioner(image)
    return _parse_pipeline_result(result)


def _caption_with_blip(
    image: Image.Image,
    model_id: str | None = None,
    prompt: str | None = None,
) -> str:
    model_id = model_id or BLIP_MODEL_ID

    if "blip" in model_id.lower():
        return _caption_with_blip_model(image, model_id, prompt=prompt)

    return _caption_with_pipeline(image, model_id, prompt=prompt)


def describe(
    image: Image.Image,
    prompt: str = "Describe this image in detail.",
    provider: str = "blip",
) -> str:
    if provider == "ollama":
        try:
            return ollama_client.image_to_text(image, prompt=prompt)
        except Exception:
            return _caption_with_blip(image, prompt=prompt)

    if provider == "blip":
        return _caption_with_blip(image, prompt=prompt)

    raise ValueError(f"Unknown provider: {provider}")

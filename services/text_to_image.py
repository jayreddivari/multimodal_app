"""Text-to-image generation via Hugging Face Inference Providers."""

from __future__ import annotations

import io

from PIL import Image

from config import (
    HF_INFERENCE_PROVIDER,
    HF_TEXT_TO_IMAGE_MODEL,
    HUGGINGFACE_API_KEY,
)

# Models known to work with HF Inference Providers (not legacy Serverless API)
RECOMMENDED_T2I_MODELS = (
    "black-forest-labs/FLUX.1-schnell",
    "black-forest-labs/FLUX.1-dev",
    "stabilityai/stable-diffusion-xl-base-1.0",
)


def _inference_client():
    from huggingface_hub import InferenceClient

    kwargs: dict = {"token": HUGGINGFACE_API_KEY}
    if HF_INFERENCE_PROVIDER:
        kwargs["provider"] = HF_INFERENCE_PROVIDER
    return InferenceClient(**kwargs)


def generate(prompt: str, model_id: str | None = None) -> Image.Image:
    model_id = model_id or HF_TEXT_TO_IMAGE_MODEL

    if not HUGGINGFACE_API_KEY:
        raise ValueError(
            "HUGGINGFACE_API_KEY is required for text-to-image. "
            "Get a free token at https://huggingface.co/settings/tokens "
            "(enable 'Inference Providers') and add it to .env"
        )

    if model_id == "stabilityai/stable-diffusion-2-1":
        raise ValueError(
            "stabilityai/stable-diffusion-2-1 is no longer available on Hugging Face "
            "Inference Providers. Remove it from .env or the Model ID field and use e.g. "
            f"{RECOMMENDED_T2I_MODELS[0]}"
        )

    client = _inference_client()
    try:
        image = client.text_to_image(prompt, model=model_id)
    except Exception as exc:
        msg = str(exc)
        if "404" in msg or "Not Found" in msg or "inferenceProviderMapping" in msg:
            raise ValueError(
                f"Model '{model_id}' is not available via Hugging Face Inference Providers. "
                f"Try one of: {', '.join(RECOMMENDED_T2I_MODELS)}. "
                "Ensure your token has 'Inference Providers' permission at "
                "https://huggingface.co/settings/tokens"
            ) from exc
        raise

    if isinstance(image, Image.Image):
        return image.convert("RGB")

    if isinstance(image, bytes):
        return Image.open(io.BytesIO(image)).convert("RGB")

    raise TypeError(f"Unexpected response type from Inference API: {type(image)}")

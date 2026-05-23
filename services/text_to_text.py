"""Text-to-text generation."""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from config import (
    HF_INFERENCE_PROVIDER,
    HF_TEXT_TO_TEXT_MODEL,
    HUGGINGFACE_API_KEY,
    OLLAMA_BASE_URL,
    OLLAMA_CHAT_MODEL,
)
from . import ollama_client

# Models that work with Hugging Face Inference Providers (not legacy Serverless API)
RECOMMENDED_T2T_MODELS = (
    "meta-llama/Llama-3.1-8B-Instruct",
    "google/gemma-2-2b-it",
    "Qwen/Qwen2.5-7B-Instruct-1M",
    "mistralai/Mistral-7B-Instruct-v0.3",
)


def _inference_client():
    from huggingface_hub import InferenceClient

    kwargs: dict = {"token": HUGGINGFACE_API_KEY}
    if HF_INFERENCE_PROVIDER:
        kwargs["provider"] = HF_INFERENCE_PROVIDER
    return InferenceClient(**kwargs)


def generate(
    prompt: str,
    system: str | None = None,
    provider: str | None = None,
    hf_model: str | None = None,
) -> str:
    if provider is None:
        provider = "huggingface" if HUGGINGFACE_API_KEY else "ollama"

    if provider == "ollama":
        return ollama_client.text_to_text(prompt, system=system)

    if provider == "huggingface":
        if not HUGGINGFACE_API_KEY:
            raise ValueError(
                "HUGGINGFACE_API_KEY is not set. Locally, add it to .env. "
                "On Streamlit Cloud, set it under App Settings → Secrets."
            )

        model_id = hf_model or HF_TEXT_TO_TEXT_MODEL
        if model_id == "HuggingFaceH4/zephyr-7b-beta":
            model_id = HF_TEXT_TO_TEXT_MODEL

        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        client = _inference_client()
        try:
            response = client.chat_completion(
                messages=messages,
                model=model_id,
                max_tokens=512,
            )
        except Exception as exc:
            msg = str(exc)
            if (
                "model_not_supported" in msg
                or "not supported by any provider" in msg
                or "404" in msg
            ):
                raise ValueError(
                    f"Model '{model_id}' is not available on your Hugging Face "
                    "Inference Providers. Try one of: "
                    f"{', '.join(RECOMMENDED_T2T_MODELS)}. "
                    "Browse models at https://huggingface.co/inference/models "
                    "and enable providers at https://huggingface.co/settings/inference-providers"
                ) from exc
            raise

        return response.choices[0].message.content

    if provider == "langchain_ollama":
        llm = ChatOllama(
            model=OLLAMA_CHAT_MODEL,
            base_url=OLLAMA_BASE_URL,
        )
        messages = []
        if system:
            messages.append(SystemMessage(content=system))
        messages.append(HumanMessage(content=prompt))
        return llm.invoke(messages).content

    raise ValueError(f"Unknown provider: {provider}")

"""Text-to-text generation."""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from multimodal_app.config import HUGGINGFACE_API_KEY, OLLAMA_BASE_URL, OLLAMA_CHAT_MODEL
from multimodal_app.services import ollama_client


def generate(
    prompt: str,
    system: str | None = None,
    provider: str = "ollama",
    hf_model: str = "HuggingFaceH4/zephyr-7b-beta",
) -> str:
    if provider == "ollama":
        return ollama_client.text_to_text(prompt, system=system)

    if provider == "huggingface":
        if not HUGGINGFACE_API_KEY:
            raise ValueError(
                "HUGGINGFACE_API_KEY is not set. Add it to .env or use Ollama."
            )
        from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

        endpoint = HuggingFaceEndpoint(
            repo_id=hf_model,
            huggingfacehub_api_token=HUGGINGFACE_API_KEY,
            max_new_tokens=512,
        )
        llm = ChatHuggingFace(llm=endpoint)
        messages = []
        if system:
            messages.append(SystemMessage(content=system))
        messages.append(HumanMessage(content=prompt))
        return llm.invoke(messages).content

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

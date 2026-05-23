"""
Multimodal AI Studio — Streamlit web app.

Run from repo root:
    streamlit run multimodal_app/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow imports when Streamlit sets cwd to this folder
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import streamlit as st
from PIL import Image

from config import (
    EDGE_TTS_VOICE,
    HF_TEXT_TO_IMAGE_MODEL,
    HUGGINGFACE_API_KEY,
    OLLAMA_BASE_URL,
    OLLAMA_CHAT_MODEL,
    OLLAMA_VISION_MODEL,
    WHISPER_MODEL_SIZE,
)
from services import (
    audio_to_text,
    image_to_text,
    ollama_client,
    text_to_audio,
    text_to_image,
    text_to_text,
    video_analysis,
)
from utils.media import pil_from_upload, save_upload_to_temp

st.set_page_config(
    page_title="Multimodal AI Studio",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

TASKS = {
    "Text → Text": "text_to_text",
    "Text → Image": "text_to_image",
    "Image → Text": "image_to_text",
    "Text → Audio": "text_to_audio",
    "Audio → Text": "audio_to_text",
    "Video → Summary": "video_summary",
    "Video → Transcription": "video_transcribe",
}


def _sidebar() -> dict:
    st.sidebar.title("Settings")
    task_label = st.sidebar.selectbox("Task", list(TASKS.keys()))
    task = TASKS[task_label]

    st.sidebar.markdown("### Providers")
    ollama_ok, ollama_models = ollama_client.check_ollama_available()
    if ollama_ok:
        st.sidebar.success("Ollama connected")
        st.sidebar.caption(f"Models: {ollama_models}")
    else:
        st.sidebar.warning("Ollama not reachable")
        st.sidebar.caption(ollama_models)

    st.sidebar.text_input("Ollama URL", value=OLLAMA_BASE_URL, disabled=True)
    chat_model = st.sidebar.text_input("Chat model", value=OLLAMA_CHAT_MODEL)
    vision_model = st.sidebar.text_input("Vision model", value=OLLAMA_VISION_MODEL)

    hf_status = "set" if HUGGINGFACE_API_KEY else "not set"
    st.sidebar.caption(f"Hugging Face token: {hf_status}")

    whisper_size = st.sidebar.selectbox(
        "Whisper size (audio→text)",
        ["tiny", "base", "small", "medium"],
        index=["tiny", "base", "small", "medium"].index(WHISPER_MODEL_SIZE)
        if WHISPER_MODEL_SIZE in ("tiny", "base", "small", "medium")
        else 1,
    )

    tts_voice = st.sidebar.text_input("edge-tts voice", value=EDGE_TTS_VOICE)

    return {
        "task": task,
        "task_label": task_label,
        "chat_model": chat_model,
        "vision_model": vision_model,
        "whisper_size": whisper_size,
        "tts_voice": tts_voice,
        "ollama_ok": ollama_ok,
    }


def _render_text_to_text(settings: dict) -> None:
    st.subheader("Text → Text")
    st.caption("Chat with a local LLM via Ollama (free). Optional: Hugging Face endpoint.")

    col1, col2 = st.columns([2, 1])
    with col2:
        provider = st.selectbox("Provider", ["ollama", "langchain_ollama", "huggingface"])
    with col1:
        system = st.text_area("System prompt (optional)", height=68)
        prompt = st.text_area("Your message", height=140, placeholder="Ask anything...")

    if st.button("Generate response", type="primary"):
        if not prompt.strip():
            st.warning("Enter a message first.")
            return
        with st.spinner("Thinking..."):
            try:
                out = text_to_text.generate(
                    prompt.strip(),
                    system=system.strip() or None,
                    provider=provider,
                )
                st.markdown("### Response")
                st.write(out)
            except Exception as exc:  # noqa: BLE001
                st.error(str(exc))


def _render_text_to_image(settings: dict) -> None:
    st.subheader("Text → Image")
    st.caption(
        "Generate images via Hugging Face Inference Providers (token needs "
        "'Inference Providers' permission)."
    )

    prompt = st.text_input("Image prompt", placeholder="A serene lake at sunset, digital art")
    model_id = st.text_input(
        "Model ID",
        value=HF_TEXT_TO_IMAGE_MODEL,
        help="Default: black-forest-labs/FLUX.1-schnell. "
        "Do not use stabilityai/stable-diffusion-2-1 (removed from HF inference).",
    )

    if st.button("Generate image", type="primary"):
        if not prompt.strip():
            st.warning("Enter a prompt first.")
            return
        with st.spinner("Generating image (may take 30–60s on free tier)..."):
            try:
                image = text_to_image.generate(prompt.strip(), model_id=model_id.strip())
                st.image(image, caption=prompt, use_container_width=True)
                st.download_button(
                    "Download PNG",
                    data=_image_png_bytes(image),
                    file_name="generated.png",
                    mime="image/png",
                )
            except Exception as exc:  # noqa: BLE001
                st.error(str(exc))


def _image_png_bytes(image: Image.Image) -> bytes:
    import io

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def _render_image_to_text(settings: dict) -> None:
    st.subheader("Image → Text")
    st.caption("Describe images with Ollama vision (llava) or local BLIP fallback.")

    uploaded = st.file_uploader("Upload image", type=["png", "jpg", "jpeg", "webp"])
    prompt = st.text_input("Question / instruction", value="Describe this image in detail.")
    provider = st.selectbox(
        "Provider",
        ["ollama", "blip"],
        help="ollama uses llava; falls back to BLIP if vision model is missing",
    )

    if uploaded and st.button("Analyze image", type="primary"):
        image = pil_from_upload(uploaded)
        st.image(image, caption="Input", width=320)
        with st.spinner("Analyzing..."):
            try:
                out = image_to_text.describe(image, prompt=prompt, provider=provider)
                st.markdown("### Description")
                st.write(out)
            except Exception as exc:  # noqa: BLE001
                st.error(str(exc))


def _render_text_to_audio(settings: dict) -> None:
    st.subheader("Text → Audio")
    st.caption("Convert text to speech with edge-tts (free, no API key).")

    text = st.text_area("Text to speak", height=120, placeholder="Hello! Welcome to multimodal AI.")
    voice = settings["tts_voice"]

    if st.button("Generate audio", type="primary"):
        if not text.strip():
            st.warning("Enter text first.")
            return
        with st.spinner("Synthesizing speech..."):
            try:
                path = text_to_audio.generate(text.strip(), voice=voice)
                st.audio(path.read_bytes(), format="audio/mp3")
                st.download_button(
                    "Download MP3",
                    data=path.read_bytes(),
                    file_name="speech.mp3",
                    mime="audio/mp3",
                )
            except Exception as exc:  # noqa: BLE001
                st.error(str(exc))


def _render_audio_to_text(settings: dict) -> None:
    st.subheader("Audio → Text")
    st.caption("Transcribe speech with OpenAI Whisper (runs locally, free).")

    st.info("Requires **ffmpeg** installed for some formats. MP3/WAV work best.")

    source = st.radio("Audio source", ["Upload file", "Record microphone"], horizontal=True)
    language = st.selectbox("Language", ["en", "auto"], format_func=lambda x: "English" if x == "en" else "Auto-detect")

    audio_file = None
    if source == "Upload file":
        audio_file = st.file_uploader("Audio file", type=["mp3", "wav", "m4a", "ogg", "webm"])
    else:
        audio_file = st.audio_input("Record audio")

    if audio_file and st.button("Transcribe", type="primary"):
        suffix = Path(audio_file.name or "audio.wav").suffix or ".wav"
        temp_path = save_upload_to_temp(audio_file, suffix=suffix)
        with st.spinner(f"Transcribing with Whisper ({settings['whisper_size']})..."):
            try:
                # Patch model size at runtime via env is awkward; pass through config
                import config as cfg

                cfg.WHISPER_MODEL_SIZE = settings["whisper_size"]
                lang = None if language == "auto" else language
                out = audio_to_text.transcribe(temp_path, language=lang)
                st.markdown("### Transcription")
                st.write(out)
            except Exception as exc:  # noqa: BLE001
                st.error(str(exc))


def _render_video_summary(settings: dict) -> None:
    st.subheader("Video → Summary / Description")
    st.caption("Sample frames, caption each, then summarize with Ollama.")

    video = st.file_uploader("Upload video", type=["mp4", "mov", "avi", "webm", "mkv"])
    user_prompt = st.text_input(
        "Summary instruction",
        value="Summarize what happens in this video in 2–3 paragraphs.",
    )
    frame_provider = st.selectbox("Frame caption provider", ["blip", "ollama"])
    max_frames = st.slider("Frames to sample", 3, 12, 6)

    if video and st.button("Analyze video", type="primary"):
        path = save_upload_to_temp(video, suffix=Path(video.name).suffix)
        with st.spinner("Extracting frames and building summary..."):
            try:
                result = video_analysis.describe_video(
                    path,
                    user_prompt=user_prompt,
                    frame_provider=frame_provider,
                    max_frames=max_frames,
                )
                st.markdown("### Summary")
                st.write(result["summary"])
                with st.expander("Per-frame captions"):
                    for line in result["captions"]:
                        st.write(line)
            except Exception as exc:  # noqa: BLE001
                st.error(str(exc))


def _render_video_transcribe(settings: dict) -> None:
    st.subheader("Video → Transcription")
    st.caption("Extract and transcribe the audio track with Whisper (needs ffmpeg).")

    video = st.file_uploader("Upload video", type=["mp4", "mov", "avi", "webm", "mkv"], key="vtx")

    if video and st.button("Transcribe video audio", type="primary"):
        path = save_upload_to_temp(video, suffix=Path(video.name).suffix)
        with st.spinner("Transcribing audio track..."):
            try:
                import config as cfg

                cfg.WHISPER_MODEL_SIZE = settings["whisper_size"]
                out = video_analysis.transcribe_video_audio(path)
                st.markdown("### Transcription")
                st.write(out)
            except Exception as exc:  # noqa: BLE001
                st.error(str(exc))


RENDERERS = {
    "text_to_text": _render_text_to_text,
    "text_to_image": _render_text_to_image,
    "image_to_text": _render_image_to_text,
    "text_to_audio": _render_text_to_audio,
    "audio_to_text": _render_audio_to_text,
    "video_summary": _render_video_summary,
    "video_transcribe": _render_video_transcribe,
}


def main() -> None:
    st.title("Multimodal AI Studio")
    st.markdown(
        "A free multimodal playground using **Ollama**, **Hugging Face**, **Whisper**, **BLIP**, and **edge-tts**."
    )

    settings = _sidebar()
    st.divider()
    renderer = RENDERERS[settings["task"]]
    renderer(settings)

    with st.expander("Setup checklist"):
        st.markdown(
            """
            1. **Ollama** — `ollama serve` then `ollama pull llama3.1:8b` and `ollama pull llava`
            2. **Hugging Face** — free token in `.env` as `HUGGINGFACE_API_KEY` (for text→image)
            3. **ffmpeg** — `brew install ffmpeg` (for video/audio formats)
            4. **First run** — Whisper & BLIP download weights on first use (one-time)
            """
        )


if __name__ == "__main__":
    main()

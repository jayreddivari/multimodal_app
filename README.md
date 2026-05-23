# Multimodal AI Studio

## This app is hosted on streamlit and can be accessed here:
https://multimodalapp-jayreddiv.streamlit.app/

A **Streamlit** web app for experimenting with multimodal AI tasks using mostly **free, local, or open** tools: [Ollama](https://ollama.com), [Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers/index), [OpenAI Whisper](https://github.com/openai/whisper), [BLIP](https://huggingface.co/Salesforce/blip-image-captioning-base), and [edge-tts](https://github.com/rany2/edge-tts).

## Features

| Task | Description | Primary backend |
|------|-------------|-----------------|
| **Text → Text** | Chat / completion | Ollama, LangChain + Ollama, or Hugging Face Inference Providers |
| **Text → Image** | Image generation from a prompt | Hugging Face Inference Providers |
| **Image → Text** | Caption or answer questions about an image | Ollama vision (`llava`) or local BLIP |
| **Text → Audio** | Text-to-speech | edge-tts (no API key) |
| **Audio → Text** | Speech transcription | Whisper (local) |
| **Video → Summary** | Sample frames, caption, summarize | BLIP / Ollama frames + configured Text → Text backend |
| **Video → Transcription** | Transcribe the video’s audio track | Whisper + ffmpeg |

## Prerequisites

- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** — Python package and environment manager
- **Python** 3.12+
- **Git**
- **Ollama** — for local text chat and vision features ([install](https://ollama.com/download))
- **ffmpeg** — for video/audio processing ([install](https://ffmpeg.org/download.html))
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt install ffmpeg`
- **Hugging Face account** (free) — required for **Text → Image** and Hugging Face chat fallback
- Enough disk space for model weights (Whisper and BLIP download on first use; Ollama models are pulled separately)

## Project layout

```text
multimodal_app/              # this repository (clone root)
├── .env                     # secrets and config (create this file)
├── app.py                   # Streamlit entry point
├── config.py
├── packages.txt             # Streamlit Cloud system packages (ffmpeg)
├── requirements.txt         # pip-compatible dependency list
├── pyproject.toml           # uv / Streamlit Cloud Python dependencies
├── uv.lock                  # locked dependency graph
├── services/
└── utils/
```

The Streamlit entry point is `app.py`. Service modules import from the app root (`config`, `services`, `utils`), so run commands from this directory unless you use `uv --directory`.

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url> multimodal_app
cd multimodal_app
```

### 2. Create a virtual environment with uv

```bash
uv venv
```

This creates `.venv` in the project directory (respecting `.python-version` if present).

### 3. Install dependencies

```bash
uv sync
```

> **Note:** `torch`, `transformers`, and `openai-whisper` are large downloads. The first install can take several minutes.
>
> If you change dependencies, update `pyproject.toml` and run `uv lock`. Streamlit Cloud installs from `uv.lock` when it is present.

**Alternative (activate the venv first):**

```bash
source .venv/bin/activate          # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### 4. Install and start Ollama

```bash
# Install from https://ollama.com/download, then:
ollama serve
```

In another terminal, pull the models used by default:

```bash
ollama pull llama3.1:8b
ollama pull llava
```

You can change model names in `.env` (see below).

### 5. Configure environment variables

Create `.env` in the **project root** (`multimodal_app/.env`):

```env
# Ollama (local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=llama3.1:8b
OLLAMA_VISION_MODEL=llava

# Hugging Face (required for Text → Image and HF chat provider)
HUGGINGFACE_API_KEY=hf_your_token_here

# Optional overrides
HF_TEXT_TO_IMAGE_MODEL=black-forest-labs/FLUX.1-schnell
HF_TEXT_TO_TEXT_MODEL=meta-llama/Llama-3.1-8B-Instruct
# HF_INFERENCE_PROVIDER=fal-ai
HF_IMAGE_TO_TEXT_MODEL=Salesforce/blip-image-captioning-base
WHISPER_MODEL_SIZE=base
EDGE_TTS_VOICE=en-US-AriaNeural
VIDEO_FRAME_SAMPLE_COUNT=6
```

Get a free Hugging Face token at: https://huggingface.co/settings/tokens  
Enable **Inference Providers** on the token for Text → Image and Hugging Face chat.

## How to run

From the project directory, use **`uv run`** (uses `.venv` automatically):

```bash
cd multimodal_app
uv run streamlit run app.py
```

The app opens in your browser (default: http://localhost:8501).

**With an activated venv:**

```bash
cd multimodal_app
source .venv/bin/activate
streamlit run app.py
```

### Monorepo layout (optional)

If this repo lives inside a parent folder (e.g. `projects_genai/multimodal_app/`):

```bash
cd projects_genai
uv run --directory multimodal_app streamlit run app.py
```

## Using the app

1. Open the sidebar and pick a **Task**.
2. Adjust **Settings** (Ollama models, Whisper size, edge-tts voice) as needed.
3. Use the main panel for inputs (text, file uploads, or microphone).
4. Click the primary action button for that task (**Generate**, **Transcribe**, **Analyze**, etc.).

### Per-task notes

- **Text → Text** — Choose provider: `ollama`, or `huggingface`. If Ollama is not reachable, the app prefers Hugging Face when `HUGGINGFACE_API_KEY` is set.
- **Text → Image** — Requires `HUGGINGFACE_API_KEY` with Inference Providers permission. Generation can take 30–60 seconds.
- **Image → Text** — Upload PNG/JPG/WebP. `ollama` uses the vision model and falls back to BLIP if vision is unavailable. When Ollama is offline, **blip** is shown first.
- **Text → Audio** — Uses Microsoft edge voices; no API key. Output is MP3.
- **Audio → Text** — Upload or record audio. Whisper downloads weights on first run. **ffmpeg** improves format support.
- **Video → Summary** — Upload MP4/MOV/WebM/etc. Samples frames, captions them, then summarizes with the configured Text → Text backend. If summarization fails, it returns the frame captions.
- **Video → Transcription** — Extracts and transcribes audio with Whisper (**ffmpeg** required).

## Setup checklist

Use the in-app **Setup checklist** expander, or verify locally:

1. `ollama serve` is running and models are pulled (`llama3.1:8b`, `llava`).
2. `.env` contains `HUGGINGFACE_API_KEY` if you use Text → Image or Hugging Face chat.
3. `ffmpeg` is installed (`ffmpeg -version`).
4. First run of Whisper/BLIP may download large files; wait for completion.

## Streamlit Cloud

This app can run on Streamlit Cloud with the Hugging Face-backed features. Local-only Ollama features are not reachable from Cloud unless you expose your own Ollama endpoint.

1. Commit `pyproject.toml`, `uv.lock`, and `packages.txt`.
2. Set the app entry point to `app.py`.
3. Add secrets under **Manage app → Settings → Secrets**:

```toml
HUGGINGFACE_API_KEY = "hf_your_token_here"
HF_TEXT_TO_IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell"
HF_TEXT_TO_TEXT_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
```

`packages.txt` installs `ffmpeg` for audio and video handling. `.env` is for local development only and is not deployed to Streamlit Cloud.

## Troubleshooting

| Issue | What to try |
|-------|-------------|
| `ModuleNotFoundError: config` or `services` | Run `uv run streamlit run app.py` from the project folder, or use `uv run --directory multimodal_app streamlit run app.py` from the parent folder. |
| `uv: command not found` | Install uv: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Ollama not reachable | Start `ollama serve`; check `OLLAMA_BASE_URL` in `.env`. |
| Text → Image 404 / repo not found | Use `black-forest-labs/FLUX.1-schnell` (not `stabilityai/stable-diffusion-2-1`). Enable **Inference Providers** on your HF token. |
| `Unknown task image-to-text` | Restart Streamlit after updating `services/image_to_text.py`; use **blip** provider or pull Ollama `llava`. |
| Video/audio errors | Install **ffmpeg**; try MP4/WAV first. |
| Vision / llava errors | Run `ollama pull llava` or switch Image → Text provider to **blip**. |
| Slow or high memory use | Use a smaller Whisper model (`tiny` / `base`) in the sidebar; reduce video frame count. |
| `.env` not picked up | Put `.env` in the project root (`multimodal_app/.env`) and restart Streamlit. |
| `ModuleNotFoundError: dotenv` on Streamlit Cloud | Cloud uses **`uv.lock`** (not `requirements.txt`). Keep `pyproject.toml` dependencies in sync and run `uv lock` after changes. |
| Streamlit Cloud secrets | Use **Manage app → Settings → Secrets** (TOML), not `.env`. Example: `HUGGINGFACE_API_KEY = "hf_..."` |
| `model_not_supported` (text→text) | Default is `meta-llama/Llama-3.1-8B-Instruct`. Enable Inference Providers on your token and pick a model from [huggingface.co/inference/models](https://huggingface.co/inference/models). |

## Development

```bash
cd multimodal_app
uv run streamlit run app.py
```

Add a dependency:

```bash
uv add <package>
uv lock
```

`main.py` is a minimal placeholder; the Streamlit entry point is **`app.py`**.

## Using pip instead of uv

If you prefer pip:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
streamlit run app.py
```

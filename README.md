# Multimodal AI Studio

A **Streamlit** web app for experimenting with multimodal AI tasks using mostly **free, local, or open** tools: [Ollama](https://ollama.com), [Hugging Face Inference API](https://huggingface.co/docs/api-inference/index), [OpenAI Whisper](https://github.com/openai/whisper), [BLIP](https://huggingface.co/Salesforce/blip-image-captioning-base), and [edge-tts](https://github.com/rany2/edge-tts).

## Features

| Task | Description | Primary backend |
|------|-------------|-----------------|
| **Text → Text** | Chat / completion | Ollama (optional: LangChain + Ollama or Hugging Face) |
| **Text → Image** | Image generation from a prompt | Hugging Face Inference Providers |
| **Image → Text** | Caption or answer questions about an image | Ollama vision (`llava`) or local BLIP |
| **Text → Audio** | Text-to-speech | edge-tts (no API key) |
| **Audio → Text** | Speech transcription | Whisper (local) |
| **Video → Summary** | Sample frames, caption, summarize | BLIP / Ollama + Ollama chat |
| **Video → Transcription** | Transcribe the video’s audio track | Whisper + ffmpeg |

## Prerequisites

- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** — Python package and environment manager
- **Python** 3.12+ (see `.python-version`; 3.13 is the project default)
- **Git**
- **Ollama** — for text chat, vision, and video summaries ([install](https://ollama.com/download))
- **ffmpeg** — for video/audio processing ([install](https://ffmpeg.org/download.html))
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt install ffmpeg`
- **Hugging Face account** (free) — required for **Text → Image**; optional for Hugging Face chat
- Enough disk space for model weights (Whisper and BLIP download on first use; Ollama models are pulled separately)

## Project layout

```text
multimodal_app/              # this repository (clone root)
├── .env                     # secrets and config (create this file)
├── app.py                   # Streamlit entry point
├── config.py
├── requirements.txt         # dependencies (installed via uv)
├── pyproject.toml
├── uv.lock
├── services/
└── utils/
```

The Python package name is `multimodal_app`. When you run `app.py`, it adds the parent folder to `sys.path` so imports resolve correctly.

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
uv pip install -r requirements.txt
```

> **Note:** `torch`, `transformers`, and `openai-whisper` are large downloads. The first install can take several minutes.

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

# Hugging Face (required for Text → Image; optional for HF chat provider)
HUGGINGFACE_API_KEY=hf_your_token_here

# Optional overrides
HF_TEXT_TO_IMAGE_MODEL=black-forest-labs/FLUX.1-schnell
# HF_INFERENCE_PROVIDER=fal-ai
HF_IMAGE_TO_TEXT_MODEL=Salesforce/blip-image-captioning-base
WHISPER_MODEL_SIZE=base
EDGE_TTS_VOICE=en-US-AriaNeural
VIDEO_FRAME_SAMPLE_COUNT=6
```

Get a free Hugging Face token at: https://huggingface.co/settings/tokens  
Enable **Inference Providers** on the token for Text → Image.

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

Or set `PYTHONPATH` and run from anywhere:

```bash
export PYTHONPATH="/path/to/projects_genai"
cd multimodal_app
uv run streamlit run app.py
```

## Using the app

1. Open the sidebar and pick a **Task**.
2. Adjust **Settings** (Ollama models, Whisper size, edge-tts voice) as needed.
3. Use the main panel for inputs (text, file uploads, or microphone).
4. Click the primary action button for that task (**Generate**, **Transcribe**, **Analyze**, etc.).

### Per-task notes

- **Text → Text** — Choose provider: `ollama` (default), `langchain_ollama`, or `huggingface`. Ollama must be running.
- **Text → Image** — Requires `HUGGINGFACE_API_KEY` with Inference Providers permission. Generation can take 30–60 seconds.
- **Image → Text** — Upload PNG/JPG/WebP. `ollama` uses the vision model; falls back to BLIP if vision is unavailable. Use **blip** to skip Ollama.
- **Text → Audio** — Uses Microsoft edge voices; no API key. Output is MP3.
- **Audio → Text** — Upload or record audio. Whisper downloads weights on first run. **ffmpeg** improves format support.
- **Video → Summary** — Upload MP4/MOV/WebM/etc. Samples frames, captions them, then summarizes with Ollama.
- **Video → Transcription** — Extracts and transcribes audio with Whisper (**ffmpeg** required).

## Setup checklist

Use the in-app **Setup checklist** expander, or verify locally:

1. `ollama serve` is running and models are pulled (`llama3.1:8b`, `llava`).
2. `.env` contains `HUGGINGFACE_API_KEY` if you use Text → Image.
3. `ffmpeg` is installed (`ffmpeg -version`).
4. First run of Whisper/BLIP may download large files; wait for completion.

## Troubleshooting

| Issue | What to try |
|-------|-------------|
| `ModuleNotFoundError: multimodal_app` | Run `uv run streamlit run app.py` from the project folder, or set `PYTHONPATH` to the parent of `multimodal_app/`. |
| `uv: command not found` | Install uv: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Ollama not reachable | Start `ollama serve`; check `OLLAMA_BASE_URL` in `.env`. |
| Text → Image 404 / repo not found | Use `black-forest-labs/FLUX.1-schnell` (not `stabilityai/stable-diffusion-2-1`). Enable **Inference Providers** on your HF token. |
| `Unknown task image-to-text` | Restart Streamlit after updating `services/image_to_text.py`; use **blip** provider or pull Ollama `llava`. |
| Video/audio errors | Install **ffmpeg**; try MP4/WAV first. |
| Vision / llava errors | Run `ollama pull llava` or switch Image → Text provider to **blip**. |
| Slow or high memory use | Use a smaller Whisper model (`tiny` / `base`) in the sidebar; reduce video frame count. |
| `.env` not picked up | Put `.env` in the project root (`multimodal_app/.env`) and restart Streamlit. |

## Development

```bash
cd multimodal_app
uv run streamlit run app.py
```

Add a dependency:

```bash
uv pip install <package>
uv pip freeze > requirements.txt   # optional: update lockfile list
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

## License

Add your license here if you publish the project.

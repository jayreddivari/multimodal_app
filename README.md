# Multimodal AI Studio

A **Streamlit** web app for experimenting with multimodal AI tasks using mostly **free, local, or open** tools: [Ollama](https://ollama.com), [Hugging Face Inference API](https://huggingface.co/docs/api-inference/index), [OpenAI Whisper](https://github.com/openai/whisper), [BLIP](https://huggingface.co/Salesforce/blip-image-captioning-base), and [edge-tts](https://github.com/rany2/edge-tts).

## Features

| Task | Description | Primary backend |
|------|-------------|-----------------|
| **Text → Text** | Chat / completion | Ollama (optional: LangChain + Ollama or Hugging Face) |
| **Text → Image** | Image generation from a prompt | Hugging Face Inference API |
| **Image → Text** | Caption or answer questions about an image | Ollama vision (`llava`) or local BLIP |
| **Text → Audio** | Text-to-speech | edge-tts (no API key) |
| **Audio → Text** | Speech transcription | Whisper (local) |
| **Video → Summary** | Sample frames, caption, summarize | BLIP / Ollama + Ollama chat |
| **Video → Transcription** | Transcribe the video’s audio track | Whisper + ffmpeg |

## Prerequisites

- **Python** 3.12+ (project targets 3.13; 3.12 works with the current stack)
- **Git**
- **Ollama** — for text chat, vision, and video summaries ([install](https://ollama.com/download))
- **ffmpeg** — for video/audio processing ([install](https://ffmpeg.org/download.html))
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt install ffmpeg`
- **Hugging Face account** (free) — only required for **Text → Image** and optional Hugging Face chat
- Enough disk space for model weights (Whisper and BLIP download on first use; Ollama models are pulled separately)

## Project layout

The app is a Python package named `multimodal_app`. Imports expect this layout:

```text
projects_genai/              # parent folder (on PYTHONPATH)
├── .env                       # environment variables (recommended location)
└── multimodal_app/            # this repository
    ├── app.py                 # Streamlit entry point
    ├── config.py
    ├── requirements.txt
    ├── services/
    └── utils/
```

If you clone the repo as `multimodal_app/`, keep a **parent directory** (for example `projects_genai/`) and run Streamlit from that parent so imports resolve correctly.

## Installation

### 1. Clone and enter the parent directory

```bash
mkdir -p ~/projects_genai
cd ~/projects_genai
git clone <your-repo-url> multimodal_app
cd ~/projects_genai
```

### 2. Create a virtual environment

Using **uv** (recommended if you use the repo’s `pyproject.toml`):

```bash
cd multimodal_app
uv venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

Or with **venv**:

```bash
cd multimodal_app
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -U pip
pip install -r requirements.txt
```

> **Note:** `torch`, `transformers`, and `openai-whisper` are large downloads. First install can take several minutes.

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

Create a `.env` file in the **parent** of the `multimodal_app` folder (same level as the package), for example `~/projects_genai/.env`:

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

`config.py` loads `.env` from the parent directory of the `multimodal_app` package (`projects_genai/.env` in the layout above).

## How to run

Always run Streamlit from the **parent** of the `multimodal_app` package, with the virtual environment activated:

```bash
cd ~/projects_genai
source multimodal_app/.venv/bin/activate
streamlit run multimodal_app/app.py
```

The app opens in your browser (default: http://localhost:8501).

### Alternative: set `PYTHONPATH` manually

If your working directory is different, point Python at the parent folder:

```bash
export PYTHONPATH="/path/to/projects_genai"
streamlit run /path/to/projects_genai/multimodal_app/app.py
```

## Using the app

1. Open the sidebar and pick a **Task**.
2. Adjust **Settings** (Ollama models, Whisper size, edge-tts voice) as needed.
3. Use the main panel for inputs (text, file uploads, or microphone).
4. Click the primary action button for that task (**Generate**, **Transcribe**, **Analyze**, etc.).

### Per-task notes

- **Text → Text** — Choose provider: `ollama` (default), `langchain_ollama`, or `huggingface`. Ollama must be running.
- **Text → Image** — Requires `HUGGINGFACE_API_KEY`. Free-tier inference can take 30–60 seconds.
- **Image → Text** — Upload PNG/JPG/WebP. `ollama` uses the vision model; falls back to BLIP if vision is unavailable.
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
| `ModuleNotFoundError: multimodal_app` | Run from the **parent** directory or set `PYTHONPATH` to that parent. |
| Ollama not reachable | Start `ollama serve`; check `OLLAMA_BASE_URL` in `.env`. |
| Text → Image 404 / repo not found | Use `black-forest-labs/FLUX.1-schnell` (not `stabilityai/stable-diffusion-2-1`). Enable **Inference Providers** on your HF token. |
| Video/audio errors | Install **ffmpeg**; try MP4/WAV first. |
| Vision / llava errors | Run `ollama pull llava` or switch Image → Text provider to **blip**. |
| Slow or high memory use | Use a smaller Whisper model (`tiny` / `base`) in the sidebar; reduce video frame count. |
| `.env` not picked up | Place `.env` in the **parent** of `multimodal_app/`, not only inside the repo (unless you symlink). |

## Development

```bash
# From repo root (multimodal_app/), after activating venv:
cd ~/projects_genai
streamlit run multimodal_app/app.py
```

`main.py` is a minimal placeholder; the Streamlit app entry point is **`app.py`**.

## License

Add your license here if you publish the project.

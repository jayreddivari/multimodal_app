"""Media encoding and video frame extraction."""

from __future__ import annotations

import base64
import io
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image


def pil_from_upload(uploaded_file) -> Image.Image:
    """Load a Streamlit uploaded file as RGB PIL Image."""
    return Image.open(uploaded_file).convert("RGB")


def image_to_bytes(image: Image.Image, fmt: str = "PNG") -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format=fmt)
    return buffer.getvalue()


def bytes_to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def save_upload_to_temp(uploaded_file, suffix: str) -> Path:
    """Persist an upload to a temporary file and return its path."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        return Path(tmp.name)


def sample_video_frames(video_path: Path, max_frames: int = 6) -> list[Image.Image]:
    """Uniformly sample frames from a video using OpenCV."""
    import cv2

    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    frames: list[Image.Image] = []

    if total <= 0:
        # Fallback: read until EOF
        while len(frames) < max_frames:
            ok, frame = capture.read()
            if not ok:
                break
            frames.append(_bgr_to_pil(frame))
    else:
        indices = np.linspace(0, max(total - 1, 0), num=min(max_frames, total), dtype=int)
        for idx in indices:
            capture.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
            ok, frame = capture.read()
            if ok:
                frames.append(_bgr_to_pil(frame))

    capture.release()
    if not frames:
        raise ValueError("No frames could be extracted from the video.")
    return frames


def _bgr_to_pil(frame: np.ndarray) -> Image.Image:
    import cv2

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)

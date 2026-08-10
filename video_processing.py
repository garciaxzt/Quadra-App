from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Literal

import imageio_ffmpeg


VideoAspect = Literal["vertical", "horizontal"]


def process_video(source: bytes, original_name: str, aspect: VideoAspect) -> bytes:
    """Converte um vídeo para MP4, recortando-o ao centro no formato escolhido."""
    suffix = Path(original_name).suffix or ".video"
    width, height = (720, 1280) if aspect == "vertical" else (1280, 720)

    input_path: Path | None = None
    output_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as input_file:
            input_file.write(source)
            input_path = Path(input_file.name)

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as output_file:
            output_path = Path(output_file.name)

        video_filter = (
            f"scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},setsar=1"
        )
        command = [
            imageio_ffmpeg.get_ffmpeg_exe(),
            "-y",
            "-i",
            str(input_path),
            "-vf",
            video_filter,
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "23",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-movflags",
            "+faststart",
            str(output_path),
        ]
        result = subprocess.run(command, capture_output=True, text=True, timeout=600)
        if result.returncode != 0 or not output_path.exists() or output_path.stat().st_size == 0:
            detail = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else "Falha desconhecida"
            raise RuntimeError(f"Não foi possível converter este vídeo: {detail}")

        return output_path.read_bytes()
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("O vídeo demorou mais de 10 minutos para ser convertido.") from exc
    finally:
        for path in (input_path, output_path):
            if path and path.exists():
                path.unlink(missing_ok=True)

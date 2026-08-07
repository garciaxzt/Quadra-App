from __future__ import annotations

from io import BytesIO
from typing import Literal

from PIL import Image, ImageOps


MAX_BYTES = 2 * 1024 * 1024
AspectMode = Literal["square", "original"]


def _remove_background(image: Image.Image) -> Image.Image:
    try:
        from rembg import remove
    except ImportError as exc:
        raise RuntimeError(
            "A remoção de fundo não está instalada. Instale as dependências do requirements.txt."
        ) from exc

    source = BytesIO()
    image.save(source, format="PNG")
    result = remove(source.getvalue())
    return Image.open(BytesIO(result)).convert("RGBA")


def _apply_white_background(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    white = Image.new("RGBA", rgba.size, "white")
    white.alpha_composite(rgba)
    return white.convert("RGB")


def _fit_format(image: Image.Image, aspect_mode: AspectMode) -> Image.Image:
    if aspect_mode == "square":
        edge = min(image.size)
        return ImageOps.fit(
            image,
            (edge, edge),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )
    return image.copy()


def _encode_under_limit(image: Image.Image, limit: int = MAX_BYTES) -> bytes:
    working = image.convert("RGB")

    while True:
        for quality in range(92, 29, -7):
            output = BytesIO()
            working.save(
                output,
                format="JPEG",
                quality=quality,
                optimize=True,
                progressive=True,
            )
            data = output.getvalue()
            if len(data) < limit:
                return data

        if min(working.size) <= 640:
            return data

        working.thumbnail(
            (round(working.width * 0.85), round(working.height * 0.85)),
            Image.Resampling.LANCZOS,
        )


def process_image(
    source: bytes,
    aspect_mode: AspectMode = "square",
    remove_background: bool = False,
) -> tuple[bytes, tuple[int, int]]:
    with Image.open(BytesIO(source)) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGBA")

    if remove_background:
        image = _remove_background(image)
        image = _apply_white_background(image)
    else:
        image = image.convert("RGB")

    image = _fit_format(image, aspect_mode)
    dimensions = image.size
    return _encode_under_limit(image), dimensions

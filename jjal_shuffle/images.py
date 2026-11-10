from pathlib import Path

import numpy as np
from PIL import Image, UnidentifiedImageError

# Supported save extensions
FORMATS = {
    ".png": "PNG",
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".bmp": "BMP",
}

def load_image(path: str | Path) -> Image.Image:
    # Open and force RGB
    try:
        with Image.open(path) as image:
            return image.convert("RGB")
    except FileNotFoundError:
        raise FileNotFoundError(f"Image file not found: {path}") from None
    except UnidentifiedImageError:
        raise ValueError(f"Not a valid image: {path}") from None

def resize_image(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    # size is (width, height)
    return image.resize(size)

def grayscale_image(image: Image.Image) -> Image.Image:
    # Single channel, luminance weighted
    return image.convert("L")

def image_as_array(image: Image.Image) -> np.ndarray:
    # Shape (height, width, 3), uint8
    return np.array(image.convert("RGB"), dtype=np.uint8)

def array_as_image(array: np.ndarray) -> Image.Image:
    # Check expected layout
    if array.dtype != np.uint8 or array.ndim != 3 or array.shape[2] != 3:
        raise ValueError(
            "Expected an array of shape (height, width, 3) and dtype uint8, "
            f"got shape {array.shape} and dtype {array.dtype}"
        )
    return Image.fromarray(array)

def save_image(image: Image.Image, path: str | Path) -> None:
    # Format from extension
    extension = Path(path).suffix.lower()
    if extension not in FORMATS:
        supported = ", ".join(sorted(FORMATS))
        raise ValueError(
            f"Unsupported image extension {extension!r} for {path}. "
            f"Supported: {supported}"
        )
    image.save(path, format=FORMATS[extension])

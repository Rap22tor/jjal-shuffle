from __future__ import annotations

import numpy as np

# ITU-R BT.601 luma weights for R, G, B
LUMINANCE_WEIGHTS = np.array([0.299, 0.587, 0.114])

def brightness(pixels: np.ndarray) -> np.ndarray:
    # Weighted sum over the last (channel) axis
    return pixels.astype(np.float64) @ LUMINANCE_WEIGHTS

def _check_image_array(array: np.ndarray, name: str) -> None:
    # Expect (height, width, 3) uint8
    if array.dtype != np.uint8 or array.ndim != 3 or array.shape[2] != 3:
        raise ValueError(
            f"Expected {name} of shape (height, width, 3) and dtype uint8, "
            f"got shape {array.shape} and dtype {array.dtype}"
        )

def shuffle_pixels(source: np.ndarray, target: np.ndarray) -> np.ndarray:
    # Rearrange source pixels so they resemble target, by brightness rank
    _check_image_array(source, "source")
    _check_image_array(target, "target")
    if source.shape != target.shape:
        raise ValueError(
            f"Source and target must have the same shape, "
            f"got {source.shape} and {target.shape}"
        )

    source_pixels = source.reshape(-1, 3)
    # Stable sorts keep ties in scan order, so output is deterministic
    source_order = np.argsort(brightness(source_pixels), kind="stable")
    target_order = np.argsort(brightness(target.reshape(-1, 3)), kind="stable")

    # i-th darkest source pixel goes to the i-th darkest target position
    result = np.empty_like(source_pixels)
    result[target_order] = source_pixels[source_order]
    return result.reshape(target.shape)

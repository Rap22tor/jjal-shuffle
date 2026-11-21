from __future__ import annotations

import numpy as np

# ITU-R BT.601 luma weights for R, G, B
LUMINANCE_WEIGHTS = np.array([0.299, 0.587, 0.114])

def brightness(pixels: np.ndarray) -> np.ndarray:
    # Weighted sum over the last (channel) axis
    return pixels.astype(np.float64) @ LUMINANCE_WEIGHTS

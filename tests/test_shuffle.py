import numpy as np
import pytest

from jjal_shuffle.shuffle import brightness

# Brightness

def test_brightness_uses_luminance_weights():
    # 0.299 * 200 + 0.587 * 100 + 0.114 * 50 = 124.2
    pixels = np.array([[[200, 100, 50]]], dtype=np.uint8)
    assert brightness(pixels)[0, 0] == pytest.approx(124.2)

def test_brightness_extremes():
    pixels = np.array([[[0, 0, 0], [255, 255, 255]]], dtype=np.uint8)
    assert brightness(pixels)[0].tolist() == pytest.approx([0.0, 255.0])

def test_brightness_drops_channel_axis():
    pixels = np.zeros((4, 5, 3), dtype=np.uint8)
    assert brightness(pixels).shape == (4, 5)

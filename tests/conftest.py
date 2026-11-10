import numpy as np
import pytest
from PIL import Image

@pytest.fixture
def gradient_image_path(tmp_path):
    # Red grows left to right, green top to bottom
    width, height = 16, 8
    array = np.zeros((height, width, 3), dtype=np.uint8)
    array[:, :, 0] = np.linspace(0, 255, width, dtype=np.uint8)[None, :]
    array[:, :, 1] = np.linspace(0, 255, height, dtype=np.uint8)[:, None]
    array[:, :, 2] = 128
    path = tmp_path / "gradient.png"
    Image.fromarray(array).save(path)
    return path

@pytest.fixture
def solid_image_path(tmp_path):
    # Single color image
    path = tmp_path / "solid.png"
    Image.new("RGB", (4, 4), (200, 100, 50)).save(path)
    return path

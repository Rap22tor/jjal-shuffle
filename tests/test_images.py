import numpy as np
import pytest
from PIL import Image

from jjal_shuffle.images import (
    array_as_image,
    grayscale_image,
    image_as_array,
    load_image,
    resize_image,
    save_image,
)
# Must match the sizes in conftest.py
GRADIENT_SIZE = (16, 8)  # (width, height)
SOLID_SIZE = (4, 4)
SOLID_COLOR = (200, 100, 50)

# Loading

def test_load_image_returns_rgb(solid_image_path):
    image = load_image(solid_image_path)
    assert image.mode == "RGB"
    assert image.size == SOLID_SIZE
    assert image.getpixel((0, 0)) == SOLID_COLOR

def test_load_image_drops_alpha(tmp_path):
    path = tmp_path / "rgba.png"
    Image.new("RGBA", (4, 4), (10, 20, 30, 0)).save(path)
    image = load_image(path)
    assert image.mode == "RGB"
    assert image.getpixel((0, 0)) == (10, 20, 30)

def test_load_image_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="not found"):
        load_image(tmp_path / "missing.png")

def test_load_image_invalid_file_raises(tmp_path):
    path = tmp_path / "fake.png"
    path.write_text("this is not an image")
    with pytest.raises(ValueError, match="Not a valid image"):
        load_image(path)

# Resizing

def test_resize_image_down(gradient_image_path):
    image = resize_image(load_image(gradient_image_path), (8, 4))
    assert image.size == (8, 4)

def test_resize_image_up_uses_width_then_height(gradient_image_path):
    image = resize_image(load_image(gradient_image_path), (32, 24))
    assert image.size == (32, 24)

# Grayscale

def test_grayscale_image_mode_and_size(gradient_image_path):
    image = load_image(gradient_image_path)
    gray = grayscale_image(image)
    assert gray.mode == "L"
    assert gray.size == image.size

def test_grayscale_image_uses_luminance_weights(solid_image_path):
    # 0.299 * 200 + 0.587 * 100 + 0.114 * 50 = 124.2
    gray = grayscale_image(load_image(solid_image_path))
    assert gray.getpixel((0, 0)) == pytest.approx(124.2, abs=1)

def test_grayscale_image_keeps_extremes():
    black = grayscale_image(Image.new("RGB", (2, 2), (0, 0, 0)))
    white = grayscale_image(Image.new("RGB", (2, 2), (255, 255, 255)))
    assert black.getpixel((0, 0)) == 0
    assert white.getpixel((0, 0)) == 255

def test_grayscale_image_array_has_equal_channels(gradient_image_path):
    array = image_as_array(grayscale_image(load_image(gradient_image_path)))
    assert np.array_equal(array[:, :, 0], array[:, :, 1])
    assert np.array_equal(array[:, :, 1], array[:, :, 2])

def test_grayscale_image_does_not_change_input(solid_image_path):
    image = load_image(solid_image_path)
    grayscale_image(image)
    assert image.mode == "RGB"
    assert image.getpixel((0, 0)) == SOLID_COLOR

# Array conversion

def test_image_to_array_shape_and_dtype(gradient_image_path):
    array = image_as_array(load_image(gradient_image_path))
    width, height = GRADIENT_SIZE
    assert array.shape == (height, width, 3)
    assert array.dtype == np.uint8

def test_array_round_trip(gradient_image_path):
    array = image_as_array(load_image(gradient_image_path))
    assert np.array_equal(image_as_array(array_as_image(array)), array)

def test_array_to_image_wrong_dtype_raises():
    array = np.zeros((4, 4, 3), dtype=np.float32)
    with pytest.raises(ValueError, match="uint8"):
        array_as_image(array)

def test_array_to_image_wrong_shape_raises():
    array = np.zeros((4, 4), dtype=np.uint8)
    with pytest.raises(ValueError, match="shape"):
        array_as_image(array)

# Saving

def test_save_image_png_round_trip(gradient_image_path, tmp_path):
    original = load_image(gradient_image_path)
    out_path = tmp_path / "out.png"
    save_image(original, out_path)
    assert np.array_equal(
        image_as_array(load_image(out_path)), image_as_array(original)
    )

def test_save_image_jpeg(solid_image_path, tmp_path):
    out_path = tmp_path / "out.JPG"
    save_image(load_image(solid_image_path), out_path)
    assert load_image(out_path).size == SOLID_SIZE

@pytest.mark.parametrize("name", ["out.xyz", "out.gif", "out"])
def test_save_image_unsupported_extension_raises(solid_image_path, tmp_path, name):
    out_path = tmp_path / name
    with pytest.raises(ValueError, match="Unsupported image extension"):
        save_image(load_image(solid_image_path), out_path)
    assert not out_path.exists()

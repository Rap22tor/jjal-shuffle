import numpy as np
import pytest
from PIL import Image

from jjal_shuffle.images import (
    array_as_image,
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

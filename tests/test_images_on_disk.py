from pathlib import Path

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
from jjal_shuffle.shuffle import shuffle_pixels

# Real images committed in the repo
IMGS_DIR = Path(__file__).resolve().parent.parent / "imgs"
IMAGE_PATHS = sorted(IMGS_DIR.glob("*.png"))

# Runs every test once per image
real_images = pytest.mark.parametrize(
    "path", IMAGE_PATHS, ids=[p.name for p in IMAGE_PATHS]
)

def test_imgs_directory_has_images():
    # Guard against silently empty parametrize
    assert IMAGE_PATHS, f"No PNG files found in {IMGS_DIR}"

@real_images
def test_load_real_image(path):
    with Image.open(path) as original:
        expected_size = original.size
    image = load_image(path)
    assert image.mode == "RGB"
    assert image.size == expected_size

@real_images
def test_load_real_image_keeps_color_channels(path):
    # Alpha is dropped, RGB values stay untouched
    with Image.open(path) as original:
        expected = np.array(original.convert("RGBA"))[:, :, :3]
    assert np.array_equal(image_as_array(load_image(path)), expected)

@real_images
def test_real_image_array_shape_and_dtype(path):
    image = load_image(path)
    array = image_as_array(image)
    width, height = image.size
    assert array.shape == (height, width, 3)
    assert array.dtype == np.uint8

@real_images
def test_real_image_array_round_trip(path):
    array = image_as_array(load_image(path))
    assert np.array_equal(image_as_array(array_as_image(array)), array)

@real_images
def test_resize_real_image(path):
    image = load_image(path)
    width, height = image.size
    # Halve, then change the aspect ratio
    assert resize_image(image, (width // 2, height // 2)).size == (width // 2, height // 2)
    assert resize_image(image, (100, 50)).size == (100, 50)
    assert image_as_array(resize_image(image, (100, 50))).shape == (50, 100, 3)

@real_images
def test_grayscale_real_image(path):
    image = load_image(path)
    gray = grayscale_image(image)
    assert gray.mode == "L"
    assert gray.size == image.size
    # Each pixel lies between the darkest and brightest channel
    rgb = image_as_array(image).astype(int)
    gray_array = np.array(gray).astype(int)
    assert np.all(gray_array >= rgb.min(axis=2) - 1)
    assert np.all(gray_array <= rgb.max(axis=2) + 1)

@real_images
def test_save_real_image_png_round_trip(path, tmp_path):
    original = load_image(path)
    out_path = tmp_path / "out.png"
    save_image(original, out_path)
    assert np.array_equal(
        image_as_array(load_image(out_path)), image_as_array(original)
    )

@real_images
def test_save_real_image_jpeg(path, tmp_path):
    original = load_image(path)
    out_path = tmp_path / "out.jpg"
    save_image(original, out_path)
    # JPEG is lossy, so only compare size
    assert load_image(out_path).size == original.size

def test_shuffle_real_images():
    # Every real image shuffled into every other one
    size = (64, 48)
    arrays = [image_as_array(resize_image(load_image(p), size)) for p in IMAGE_PATHS]
    for source in arrays:
        for target in arrays:
            result = shuffle_pixels(source, target)
            assert result.shape == target.shape
            # Same multiset of RGB pixels, just rearranged
            result_pixels = np.unique(result.reshape(-1, 3), axis=0, return_counts=True)
            source_pixels = np.unique(source.reshape(-1, 3), axis=0, return_counts=True)
            assert np.array_equal(result_pixels[0], source_pixels[0])
            assert np.array_equal(result_pixels[1], source_pixels[1])

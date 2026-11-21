import numpy as np
import pytest

from jjal_shuffle.shuffle import brightness, shuffle_pixels

def random_image(seed, shape=(8, 12, 3)):
    rng = np.random.default_rng(seed)
    return rng.integers(0, 256, size=shape, dtype=np.uint8)

def sorted_pixels(array):
    # Pixels as a sorted list of RGB rows, ignoring position
    pixels = array.reshape(-1, 3)
    return pixels[np.lexsort(pixels.T[::-1])]

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

# Shuffle

def test_shuffle_keeps_target_shape_and_dtype():
    result = shuffle_pixels(random_image(0), random_image(1))
    assert result.shape == (8, 12, 3)
    assert result.dtype == np.uint8

def test_shuffle_uses_exactly_the_source_pixels():
    source = random_image(0)
    result = shuffle_pixels(source, random_image(1))
    assert np.array_equal(sorted_pixels(result), sorted_pixels(source))

def test_shuffle_is_deterministic():
    source, target = random_image(0), random_image(1)
    first = shuffle_pixels(source, target)
    second = shuffle_pixels(source.copy(), target.copy())
    assert np.array_equal(first, second)

def test_shuffle_does_not_change_inputs():
    source, target = random_image(0), random_image(1)
    source_copy, target_copy = source.copy(), target.copy()
    shuffle_pixels(source, target)
    assert np.array_equal(source, source_copy)
    assert np.array_equal(target, target_copy)

def test_shuffle_mismatched_shapes_raise():
    with pytest.raises(ValueError, match="same shape"):
        shuffle_pixels(random_image(0, (4, 4, 3)), random_image(1, (4, 5, 3)))

@pytest.mark.parametrize(
    "bad",
    [
        np.zeros((4, 4, 3), dtype=np.float32),
        np.zeros((4, 4), dtype=np.uint8),
        np.zeros((4, 4, 4), dtype=np.uint8),
    ],
)
def test_shuffle_invalid_array_raises(bad):
    with pytest.raises(ValueError, match="height, width, 3"):
        shuffle_pixels(bad, bad)

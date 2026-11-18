import pytest
from PIL import Image

from jjal_shuffle.ascii_art import ASCII_RAMP, image_to_ascii

# Output size

@pytest.mark.parametrize(
    "image_size, width, expected_height",
    [
        ((100, 50), 40, 10),   # 50 / 100 * 40 * 0.5
        ((100, 100), 20, 10),  # square image, height is half the width
        ((16, 8), 16, 4),
        ((16, 8), 8, 2),
        ((10, 40), 10, 20),    # tall image
        ((100, 2), 10, 1),     # rounds to 0, clamped to 1
    ],
)
def test_image_to_ascii_line_count_and_length(image_size, width, expected_height):
    lines = image_to_ascii(Image.new("RGB", image_size, (90, 90, 90)), width).split("\n")
    assert len(lines) == expected_height
    assert all(len(line) == width for line in lines)

def test_image_to_ascii_width_one():
    lines = image_to_ascii(Image.new("RGB", (4, 16), (90, 90, 90)), 1).split("\n")
    assert len(lines) == 2
    assert all(len(line) == 1 for line in lines)

def test_image_to_ascii_upscales_small_image():
    lines = image_to_ascii(Image.new("RGB", (2, 2), (90, 90, 90)), 20).split("\n")
    assert len(lines) == 10
    assert all(len(line) == 20 for line in lines)

def test_image_to_ascii_has_no_trailing_newline():
    assert not image_to_ascii(Image.new("RGB", (4, 4), (0, 0, 0)), 4).endswith("\n")

# Brightness mapping

def test_image_to_ascii_black_uses_first_ramp_character():
    art = image_to_ascii(Image.new("RGB", (20, 20), (0, 0, 0)), 10)
    assert set(art.replace("\n", "")) == {ASCII_RAMP[0]}

def test_image_to_ascii_white_uses_last_ramp_character():
    art = image_to_ascii(Image.new("RGB", (20, 20), (255, 255, 255)), 10)
    assert set(art.replace("\n", "")) == {ASCII_RAMP[-1]}

def test_image_to_ascii_gets_brighter_left_to_right():
    # Grayscale ramp from black to white, one column per ramp character
    width = len(ASCII_RAMP)
    gradient = Image.new("L", (width, 4))
    gradient.putdata([round(x / (width - 1) * 255) for _ in range(4) for x in range(width)])
    first_line = image_to_ascii(gradient, width).split("\n")[0]
    # Same size in, same size out, so every character is used in order
    assert first_line == ASCII_RAMP

def test_image_to_ascii_uses_luminance_not_one_channel():
    # Pure green is far brighter than pure blue
    green = image_to_ascii(Image.new("RGB", (4, 4), (0, 255, 0)), 4)
    blue = image_to_ascii(Image.new("RGB", (4, 4), (0, 0, 255)), 4)
    assert ASCII_RAMP.index(green[0]) > ASCII_RAMP.index(blue[0])

def test_image_to_ascii_accepts_other_modes():
    white = {"L": 255, "RGBA": (255, 255, 255, 255)}
    for mode, color in white.items():
        art = image_to_ascii(Image.new(mode, (8, 8), color), 4)
        assert set(art.replace("\n", "")) == {ASCII_RAMP[-1]}

def test_image_to_ascii_does_not_change_input():
    image = Image.new("RGB", (8, 8), (200, 100, 50))
    image_to_ascii(image, 4)
    assert image.mode == "RGB"
    assert image.size == (8, 8)
    assert image.getpixel((0, 0)) == (200, 100, 50)

# Validation

@pytest.mark.parametrize("width", [0, -1, -100])
def test_image_to_ascii_invalid_width_raises(width):
    with pytest.raises(ValueError, match="width"):
        image_to_ascii(Image.new("RGB", (4, 4)), width)

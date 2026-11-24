from PIL import Image

from jjal_shuffle.images import grayscale_image, resize_image

# Dark to bright, assumes light text on a dark terminal
ASCII_RAMP = " .:-=+*#%@"

# Terminal characters are about twice as tall as they are wide
CHAR_ASPECT = 0.5

def image_to_ascii(image: Image.Image, width: int) -> str:
    if width < 1:
        raise ValueError(f"width must be at least 1, got {width}")

    # Resize the image to the desired size and adjust the aspect ratio of the
    # image to better
    orig_width, orig_height = image.size
    height = max(1, round(orig_height / orig_width * width * CHAR_ASPECT))
    gray = resize_image(grayscale_image(image), (width, height))

    pixels = gray.tobytes()
    steps = len(ASCII_RAMP)
    lines = []
    for row in range(height):
        row_pixels = pixels[row * width:(row + 1) * width]
        # 0..255 split into equal bins, so 255 lands on the last character
        lines.append("".join(ASCII_RAMP[p * steps // 256] for p in row_pixels))
    return "\n".join(lines)

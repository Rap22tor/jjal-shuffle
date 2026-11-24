import argparse
import sys
from pathlib import Path

from jjal_shuffle.ascii_art import image_to_ascii
from jjal_shuffle.images import (
    array_as_image,
    image_as_array,
    load_image,
    resize_image,
    save_image,
)
from jjal_shuffle.shuffle import shuffle_pixels

__version__ = "0.1.0"

DEFAULT_OUTPUT = "shuffled.png"
DEFAULT_SIZE = "256x256"
DEFAULT_ASCII_WIDTH = 80

def parse_size(value: str) -> tuple[int, int]:
    # "WxH" -> (width, height), both positive
    parts = value.lower().split("x")
    try:
        width, height = (int(part) for part in parts)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"invalid size {value!r}, expected WxH, e.g. 256x256"
        ) from None
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError(
            f"invalid size {value!r}, width and height must be positive"
        )
    return width, height

def positive_int(value: str) -> int:
    # argparse type, a bad value becomes a usage error
    try:
        number = int(value)
    except ValueError:
        number = 0
    if number < 1:
        raise argparse.ArgumentTypeError(f"expected a positive integer, got {value!r}")
    return number

def run_ascii(args: argparse.Namespace) -> int:
    try:
        art = image_to_ascii(load_image(args.image), args.width)
        if args.output is None:
            print(art)
        else:
            # Same text as stdout, LF on every platform
            Path(args.output).write_text(art + "\n", encoding="utf-8", newline="\n")
    except (OSError, ValueError) as error:
        # Short message, no traceback
        print(f"ascii: {error}", file=sys.stderr)
        return 1
    return 0

def run_shuffle(args: argparse.Namespace) -> int:
    # load -> resize -> shuffle -> save
    try:
        source = image_as_array(resize_image(load_image(args.source), args.size))
        target = image_as_array(resize_image(load_image(args.target), args.size))
        result = shuffle_pixels(source, target)
        save_image(array_as_image(result), args.output)
    except (OSError, ValueError) as error:
        # Short message, no traceback
        print(f"shuffle: error: {error}", file=sys.stderr)
        return 1
    print(f"Saved {args.output}")
    return 0

def add_ascii_parser(subparsers) -> None:
    # Register ascii subcommand
    parser = subparsers.add_parser(
        "ascii",
        help="convert an image to ASCII art",
    )
    parser.add_argument("image", metavar="IMAGE", help="path to the input image")
    parser.add_argument(
        "--width",
        type=positive_int,
        default=DEFAULT_ASCII_WIDTH,
        metavar="N",
        help=f"characters per line (default: {DEFAULT_ASCII_WIDTH})",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="write to a UTF-8 text file instead of stdout",
    )
    # Link handler to subcommand
    parser.set_defaults(handler=run_ascii)

def add_shuffle_parser(subparsers) -> None:
    # Register shuffle subcommand
    parser = subparsers.add_parser(
        "shuffle",
        help="rearrange the pixels of one image to look like another",
        description=(
            "Rearrange the pixels of SOURCE so the result looks like TARGET. "
            "Both images are resized to --size first. The aspect ratio is not "
            "preserved: images are stretched to fit --size."
        ),
    )
    parser.add_argument("source", help="image whose pixels are used")
    parser.add_argument("target", help="image the result should look like")
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"where to save the result (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--size",
        type=parse_size,
        default=DEFAULT_SIZE,
        metavar="WxH",
        help=(
            f"size both images are resized to (default: {DEFAULT_SIZE}); "
            "aspect ratio is not preserved"
        ),
    )
    # Link handler to subcommand
    parser.set_defaults(handler=run_shuffle)

def build_parser() -> argparse.ArgumentParser:
    # Top-level parser
    parser = argparse.ArgumentParser(
        prog="jjal_shuffle",
        description="Jjal-Shuffle: Shuffle your memes.",
    )
    # --version flag
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    # Subcommand container
    subparsers = parser.add_subparsers(title="commands", metavar="<command>")
    add_shuffle_parser(subparsers)
    add_ascii_parser(subparsers)
    return parser

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    # No subcommand given
    if not hasattr(args, "handler"):
        parser.print_help()
        return 0
    # Run chosen subcommand
    return args.handler(args)

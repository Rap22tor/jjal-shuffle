import argparse
import errno
import os
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
    error = argparse.ArgumentTypeError(f"expected a positive integer, got {value!r}")
    try:
        number = int(value)
    except ValueError:
        raise error from None
    if number < 1:
        raise error
    return number

def print_to_pipe(text: str) -> bool:
    # Print text, False if the reader closed stdout early (e.g. `| head`)
    try:
        print(text)
        # Flush now so a closed pipe shows up here, not at exit
        sys.stdout.flush()
    except OSError as error:
        # Closed pipe is EPIPE, but EINVAL on Windows
        closed = isinstance(error, BrokenPipeError) or (
            sys.platform == "win32" and error.errno == errno.EINVAL
        )
        if not closed:
            raise
        # Point stdout at devnull so the flush at exit can't fail again
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        return False
    return True

def run_ascii(args: argparse.Namespace) -> int:
    try:
        art = image_to_ascii(load_image(args.image), args.width)
        if args.output is None:
            if not print_to_pipe(art):
                # No message for a closed pipe, as the Python docs advise
                return 1
        else:
            output = Path(args.output)
            if output.exists() and output.samefile(args.image):
                raise ValueError(f"output would overwrite the input image: {output}")
            # Same text as stdout, LF on every platform
            output.write_text(art + "\n", encoding="utf-8", newline="\n")
            print(f"Saved {output}")
    except (OSError, ValueError) as error:
        # Short message, no traceback
        print(f"ascii: error: {error}", file=sys.stderr)
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
        description=(
            "Convert IMAGE to ASCII art, printed to stdout or written to "
            "--output. The aspect ratio is kept. Characters are chosen for light "
            "text on a dark background, so on a light background (e.g. most "
            "text editors) the picture looks inverted."
        ),
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

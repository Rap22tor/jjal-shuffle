import argparse
import sys

__version__ = "0.1.0"

DEFAULT_OUTPUT = "shuffled.png"
DEFAULT_SIZE = "256x256"

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

def run_shuffle(args: argparse.Namespace) -> int:
    # Stub handler
    # TODO https://github.com/Rap22tor/jjal-shuffle/issues/6
    print("shuffle: not implemented yet", file=sys.stderr)
    return 1

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

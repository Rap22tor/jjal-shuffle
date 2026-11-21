import argparse
import sys

__version__ = "0.1.0"

def run_shuffle(args: argparse.Namespace) -> int:
    # Stub handler
    # TODO https://github.com/Rap22tor/jjal-shuffle/issues/6
    print("shuffle: not implemented yet", file=sys.stderr)
    return 1

def add_shuffle_parser(subparsers) -> None:
    # Register shuffle subcommand
    parser = subparsers.add_parser(
        "shuffle",
        help="TODO",
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

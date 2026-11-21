import argparse

import pytest

from jjal_shuffle.cli import build_parser, main, parse_size

def test_help_exits_with_zero():
    with pytest.raises(SystemExit) as exif:
        main(["--help"])
    assert exif.value.code == 0

def test_version_exits_with_zero():
    with pytest.raises(SystemExit) as exif:
        main(["--version"])
    assert exif.value.code == 0

def test_unknown_subcommand_exits_with_nonzero():
    with pytest.raises(SystemExit) as exif:
        main(["does-not-exist"])
    assert exif.value.code != 0

# Shuffle arguments

def test_shuffle_defaults():
    args = build_parser().parse_args(["shuffle", "a.png", "b.png"])
    assert args.source == "a.png"
    assert args.target == "b.png"
    assert args.output == "shuffled.png"
    assert args.size == (256, 256)

def test_shuffle_output_and_size():
    args = build_parser().parse_args(
        ["shuffle", "a.png", "b.png", "-o", "out.jpg", "--size", "64x32"]
    )
    assert args.output == "out.jpg"
    assert args.size == (64, 32)

@pytest.mark.parametrize("value, expected", [("10x20", (10, 20)), ("1X1", (1, 1))])
def test_parse_size_valid(value, expected):
    assert parse_size(value) == expected

@pytest.mark.parametrize("value", ["256", "axb", "10x", "x10", "10x20x30", "0x10", "10x-5", ""])
def test_parse_size_invalid(value):
    with pytest.raises(argparse.ArgumentTypeError):
        parse_size(value)

def test_shuffle_bad_size_is_argparse_error(capsys):
    with pytest.raises(SystemExit) as exif:
        main(["shuffle", "a.png", "b.png", "--size", "big"])
    assert exif.value.code == 2
    assert "invalid size" in capsys.readouterr().err

def test_shuffle_missing_arguments_exit_nonzero():
    with pytest.raises(SystemExit) as exif:
        main(["shuffle", "a.png"])
    assert exif.value.code != 0

def test_shuffle_help_mentions_aspect_ratio(capsys):
    with pytest.raises(SystemExit):
        main(["shuffle", "--help"])
    assert "aspect ratio" in capsys.readouterr().out

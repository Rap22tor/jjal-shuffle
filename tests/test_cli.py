import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from jjal_shuffle.cli import build_parser, main, parse_size
from jjal_shuffle.images import image_as_array, load_image, resize_image

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

# Shuffle errors

def test_shuffle_missing_source(tmp_path, solid_image_path, capsys):
    code = main(["shuffle", str(tmp_path / "missing.png"), str(solid_image_path)])
    err = capsys.readouterr().err
    assert code != 0
    assert "not found" in err
    assert "Traceback" not in err

def test_shuffle_invalid_target(tmp_path, solid_image_path, capsys):
    fake = tmp_path / "fake.png"
    fake.write_text("this is not an image")
    code = main(["shuffle", str(solid_image_path), str(fake)])
    assert code != 0
    assert "Not a valid image" in capsys.readouterr().err

def test_shuffle_unsupported_output_extension(tmp_path, solid_image_path, capsys):
    out = tmp_path / "out.xyz"
    code = main(["shuffle", str(solid_image_path), str(solid_image_path), "-o", str(out)])
    assert code != 0
    assert "Unsupported image extension" in capsys.readouterr().err
    assert not out.exists()

def test_shuffle_output_directory_missing(tmp_path, solid_image_path, capsys):
    out = tmp_path / "no-such-dir" / "out.png"
    code = main(["shuffle", str(solid_image_path), str(solid_image_path), "-o", str(out)])
    assert code != 0
    assert capsys.readouterr().err.startswith("shuffle: error:")

# Shuffle end to end

def pixel_counts(array):
    # Multiset of RGB pixels, ignoring position
    values, counts = np.unique(array.reshape(-1, 3), axis=0, return_counts=True)
    return values.tolist(), counts.tolist()

def test_shuffle_end_to_end(tmp_path, gradient_image_path):
    # Synthetic target: random noise, different size from the source
    rng = np.random.default_rng(0)
    target_path = tmp_path / "target.png"
    Image.fromarray(rng.integers(0, 256, (10, 20, 3), dtype=np.uint8)).save(target_path)
    out = tmp_path / "result.png"

    code = main([
        "shuffle", str(gradient_image_path), str(target_path),
        "-o", str(out), "--size", "12x6",
    ])

    assert code == 0
    assert out.exists()
    result = load_image(out)
    assert result.size == (12, 6)
    expected = image_as_array(resize_image(load_image(gradient_image_path), (12, 6)))
    assert pixel_counts(image_as_array(result)) == pixel_counts(expected)

def test_shuffle_default_output(tmp_path, monkeypatch, gradient_image_path, capsys):
    monkeypatch.chdir(tmp_path)
    code = main(["shuffle", str(gradient_image_path), str(gradient_image_path)])
    assert code == 0
    assert load_image(tmp_path / "shuffled.png").size == (256, 256)
    assert "shuffled.png" in capsys.readouterr().out

def test_shuffle_via_python_m(tmp_path, gradient_image_path):
    # Runs the real entry point in a subprocess
    out = tmp_path / "out.png"
    completed = subprocess.run(
        [sys.executable, "-m", "jjal_shuffle", "shuffle",
         str(gradient_image_path), str(gradient_image_path),
         "-o", str(out), "--size", "8x8"],
        capture_output=True, text=True,
        cwd=Path(__file__).resolve().parent.parent,
    )
    assert completed.returncode == 0, completed.stderr
    assert load_image(out).size == (8, 8)

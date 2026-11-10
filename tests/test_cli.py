import pytest

from jjal_shuffle.cli import main

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

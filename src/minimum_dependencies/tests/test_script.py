"""Test the minimum_dependencies script itself."""

import pytest

from minimum_dependencies._core import Fail
from minimum_dependencies._script import main

from .common import (
    _TEST,
    _TESTING_NO_EXIST,
    _TESTING_NO_PIN,
    _TESTING_OTHER,
    _TESTING_URL,
    _BaseTest,
    _get_fail_context,
)


class TestMain(_BaseTest):
    """Test the main function."""

    def test_basic_main(self, capsys):
        """Test the main function."""
        main(["minimum_dependencies"])
        assert capsys.readouterr().out == "".join(self.base)

    def test_extras_main(self, capsys):
        """Test the main function with extras."""
        main(
            [
                "minimum_dependencies",
                "--extras",
                _TEST,
                _TESTING_OTHER,
                _TESTING_URL,
            ],
        )
        assert capsys.readouterr().out == "".join(
            self.base_extras + self.test + self.testing_other + self.testing_url,
        )

    def test_filename_main(self, tmp_path, capsys):
        """Test the main function with a filename."""
        filename = tmp_path / "test.txt"
        main(["minimum_dependencies", "--filename", str(filename)])
        assert not capsys.readouterr().out
        assert filename.read_text() == "".join(self.base)

    def test_extras_filename_main(self, tmp_path, capsys):
        """Test the main function with extras and a filename."""
        filename = tmp_path / "test.txt"
        main(
            [
                "minimum_dependencies",
                "--filename",
                str(filename),
                "--extras",
                _TEST,
            ],
        )
        assert not capsys.readouterr().out
        assert filename.read_text() == "".join(
            self.base_extras + self.test,
        )

    @pytest.mark.parametrize("fail", Fail)
    @pytest.mark.parametrize("extras", [_TESTING_NO_EXIST, _TESTING_NO_PIN])
    def test_fail_main(self, capsys, fail, extras):
        """Test the main function with a failure."""
        args = ["minimum_dependencies", "--extras", extras]
        if fail:
            args.append("--fail")

        with _get_fail_context(fail, extras):
            main(args)
            assert capsys.readouterr().out == "".join(
                self.base_extras + self.testing_error,
            )

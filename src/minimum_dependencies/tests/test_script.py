"""Test the minimum_dependencies script itself."""

import pytest
from typer.testing import CliRunner

from minimum_dependencies._core import Fail
from minimum_dependencies._script import app

from .common import (
    _TEST,
    _TESTING_NO_EXIST,
    _TESTING_NO_PIN,
    _TESTING_OTHER,
    _TESTING_URL,
    _BaseTest,
    _get_fail_context,
)

runner = CliRunner()


class TestMain(_BaseTest):
    """Test the main function."""

    def test_basic_main(self):
        """Test the main function."""
        result = runner.invoke(app, ["minimum_dependencies"])
        assert result.stdout == "".join(self.base)

    def test_extras_main(self):
        """Test the main function with extras."""
        result = runner.invoke(
            app,
            [
                "minimum_dependencies",
                "--extras",
                f"{_TEST},{_TESTING_OTHER},{_TESTING_URL}",
            ],
        )
        assert result.stdout == "".join(
            self.base + self.test + self.testing_other + self.testing_url,
        )

    def test_filename_main(self, tmp_path):
        """Test the main function with a filename."""
        filename = tmp_path / "test.txt"
        result = runner.invoke(
            app,
            [
                "minimum_dependencies",
                "--filename",
                str(filename),
            ],
        )
        assert result.stdout == ""
        assert filename.read_text() == "".join(self.base)

    def test_extras_filename_main(self, tmp_path):
        """Test the main function with extras and a filename."""
        filename = tmp_path / "test.txt"
        result = runner.invoke(
            app,
            [
                "minimum_dependencies",
                "--filename",
                str(filename),
                "--extras",
                _TEST,
            ],
        )
        assert result.stdout == ""
        assert filename.read_text() == "".join(
            self.base + self.test,
        )

    @pytest.mark.parametrize("fail", Fail)
    @pytest.mark.parametrize("extras", [_TESTING_NO_EXIST, _TESTING_NO_PIN])
    def test_fail_main(self, fail, extras):
        """Test the main function with a failure."""
        args = ["minimum_dependencies", "--extras", extras]
        if fail:
            args.append("--fail")

        with _get_fail_context(fail, extras):
            result = runner.invoke(app, args, catch_exceptions=False)
            assert result.stdout == "".join(self.base + self.testing_error)

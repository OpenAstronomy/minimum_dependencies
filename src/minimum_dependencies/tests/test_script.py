"""Test the minimum_dependencies script itself."""

import pytest

from minimum_dependencies._core import Fail
from minimum_dependencies._script import main

from .common import _BaseTest, _get_context


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
                "test",
                "testing_other",
                "testing_url",
            ],
        )
        assert capsys.readouterr().out == "".join(
            self.base + self.test + self.testing_other + self.testing_url,
        )

    def test_filename_main(self, tmp_path, capsys):
        """Test the main function with a filename."""
        filename = tmp_path / "test.txt"
        main(["minimum_dependencies", "--filename", str(filename)])
        assert capsys.readouterr().out == ""
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
                "test",
            ],
        )
        assert capsys.readouterr().out == ""
        assert filename.read_text() == "".join(
            self.base + self.test,
        )

    @pytest.mark.parametrize("fail", Fail)
    @pytest.mark.parametrize("extras", ["testing_no_exist", "testing_no_pin"])
    def test_fail_main(self, capsys, fail, extras):
        """Test the main function with a failure."""
        msg = {
            "testing_no_exist": r"Exact version .* not found on PyPi.",
            "testing_no_pin": r"No version specifier for .* in install_requires.",
        }

        args = ["minimum_dependencies", "--extras", extras]
        if fail:
            args.append("--fail")

        with _get_context(fail, msg[extras]):
            main(args)
            assert capsys.readouterr().out == "".join(
                self.base + self.testing_error,
            )

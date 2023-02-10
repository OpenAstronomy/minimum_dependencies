"""Test the minimum_dependencies script itself."""


from minimum_dependencies._script import main

from .common import _BaseTest


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

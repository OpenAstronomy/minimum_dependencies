"""Test the minimum_dependencies script itself."""


from minimum_dependencies._script import main


class TestMain:
    """Test the main function."""

    def setup_class(self):
        """Create the truths for testing."""
        self.base_requrirements = [
            "importlib-metadata==4.11.4\n",
            "packaging==23.0\n",
            "requests==2.25.0\n",
        ]
        self.test_requirements = [
            "pytest==6.0.0\n",
            "pytest-doctestplus==0.12.0\n",
        ]
        self.test_other = [
            "astropy[all]==5.0\n",
        ]

    def test_basic_main(self, capsys):
        """Test the main function."""
        main(["minimum_dependencies"])
        assert capsys.readouterr().out == "".join(self.base_requrirements)

    def test_extras_main(self, capsys):
        """Test the main function with extras."""
        main(["minimum_dependencies", "--extras", "test", "other"])
        assert capsys.readouterr().out == "".join(
            self.base_requrirements + self.test_other + self.test_requirements,
        )

    def test_filename_main(self, tmp_path, capsys):
        """Test the main function with a filename."""
        filename = tmp_path / "test.txt"
        main(["minimum_dependencies", "--filename", str(filename)])
        assert capsys.readouterr().out == ""
        assert filename.read_text() == "".join(self.base_requrirements)

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
            self.base_requrirements + self.test_requirements,
        )

"""Tests for opennb."""

import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import MagicMock, patch

import pytest

from opennb import (
    _convert_github_path_to_raw_url,
    _convert_to_ipynb,
    _get_default_branch,
    main,
    open_notebook_from_url,
)


def test_get_default_branch() -> None:
    """Test getting default branch from GitHub API."""
    # Create a mock that supports context manager
    mock_response = MagicMock()
    mock_response.__enter__.return_value = mock_response
    mock_response.read.return_value = b'{"default_branch": "main"}'

    with patch("urllib.request.urlopen", return_value=mock_response):
        assert _get_default_branch("owner", "repo") == "main"


def test_get_default_branch_not_found() -> None:
    """Test handling of non-existent repository."""
    error = urllib.error.HTTPError(
        url=None,  # type: ignore[arg-type]
        code=404,
        msg="Not Found",
        hdrs=None,  # type: ignore[arg-type]
        fp=None,
    )
    with (
        patch("urllib.request.urlopen", side_effect=error),
        pytest.raises(ValueError, match="Repository owner/repo not found"),
    ):
        _get_default_branch("owner", "repo")


def test_get_default_branch_other_error() -> None:
    """Test handling of other HTTP errors."""
    error = urllib.error.HTTPError(
        url=None,  # type: ignore[arg-type]
        code=500,
        msg="Server Error",
        hdrs=None,  # type: ignore[arg-type]
        fp=None,
    )
    with patch("urllib.request.urlopen", side_effect=error), pytest.raises(urllib.error.HTTPError):
        _get_default_branch("owner", "repo")


@pytest.mark.parametrize(
    ("input_path", "expected_url"),
    [
        (
            "owner/repo/path/notebook.ipynb",
            "https://raw.githubusercontent.com/owner/repo/main/path/notebook.ipynb",
        ),
        (
            "owner/repo@branch#path/notebook.ipynb",
            "https://raw.githubusercontent.com/owner/repo/branch/path/notebook.ipynb",
        ),
        (
            "owner/repo@feature/branch#path/notebook.ipynb",
            "https://raw.githubusercontent.com/owner/repo/feature/branch/path/notebook.ipynb",
        ),
    ],
)
def test_convert_github_path_to_raw_url(input_path: str, expected_url: str) -> None:
    """Test converting various GitHub paths to raw URLs."""
    with patch("opennb._get_default_branch", return_value="main"):
        assert _convert_github_path_to_raw_url(input_path) == expected_url


@pytest.mark.parametrize(
    ("input_path", "error_message"),
    [
        (
            "owner/repo@branch",
            "When using @branch, the path must be specified after #",
        ),
        (
            "owner/repo",
            "Path must be in format: owner/repository/path/to/notebook.ipynb",
        ),
        (
            "owner/repo@branch#path/notebook.txt",
            "Path must end with .ipynb",
        ),
        (
            "invalid@branch#notebook.ipynb",
            "Repository path must be in format: owner/repository",
        ),
    ],
)
def test_convert_github_path_to_raw_url_errors(input_path: str, error_message: str) -> None:
    """Test error handling in GitHub path conversion."""
    with pytest.raises(ValueError, match=error_message):
        _convert_github_path_to_raw_url(input_path)


def test_open_notebook_from_url() -> None:
    """Test opening notebook from URL."""
    with (
        patch("urllib.request.urlretrieve") as mock_retrieve,
        patch("subprocess.run") as mock_run,
    ):
        url = "https://example.com/notebook.ipynb"
        open_notebook_from_url(url)

        mock_retrieve.assert_called_once()
        mock_run.assert_called_once()


def test_open_notebook_from_url_with_args(tmp_path: Path) -> None:
    """Test opening notebook with additional Jupyter arguments."""
    with (
        patch("urllib.request.urlretrieve") as mock_retrieve,
        patch("subprocess.run") as mock_run,
        patch("sys.executable", "/path/to/python"),  # Mock Python executable path
    ):
        url = "https://example.com/notebook.ipynb"
        jupyter_args = ["--port", "8888"]
        open_notebook_from_url(url, output_dir=tmp_path, jupyter_args=jupyter_args)

        mock_retrieve.assert_called_once()
        mock_run.assert_called_once_with(
            [
                "/path/to/python",
                "-m",
                "jupyter",
                "notebook",
                str(tmp_path / "notebook.ipynb"),
                "--port",
                "8888",
            ],
            check=True,
        )


def test_open_notebook_invalid_extension() -> None:
    """Test handling of non-notebook files."""
    with pytest.raises(ValueError, match="URL must point to a Jupyter notebook"):
        open_notebook_from_url("https://example.com/file.txt")


def test_main() -> None:
    """Test main function with command line arguments."""
    test_args = ["owner/repo/notebook.ipynb", "--port", "8888"]
    with (
        patch("sys.argv", ["opennb", *test_args]),
        patch("opennb.open_notebook_from_url") as mock_open,
    ):
        main()
        mock_open.assert_called_once()


def test_main_with_output_dir(tmp_path: Path) -> None:
    """Test main function with output directory specified."""
    test_args = ["owner/repo/notebook.ipynb", "--output-dir", str(tmp_path)]
    with (
        patch("sys.argv", ["opennb", *test_args]),
        patch("opennb.open_notebook_from_url") as mock_open,
    ):
        main()
        mock_open.assert_called_once_with(
            "owner/repo/notebook.ipynb",
            tmp_path,  # Changed from str(tmp_path) to tmp_path
            [],
        )


def test_open_notebook_from_md_url(tmp_path: Path) -> None:
    """Test opening a .md (Jupytext) file from a URL."""
    mock_markdown_content = b"# This is a test markdown file"
    url = "https://example.com/notebook.md"

    with (
        patch("urllib.request.urlopen") as mock_urlopen,
        patch("subprocess.run") as mock_run,
        patch("opennb._convert_to_ipynb", return_value=tmp_path / "temp.ipynb") as mock_convert,
    ):
        # Mock the response from urlopen for the markdown file
        mock_response = MagicMock()
        mock_response.read.return_value = mock_markdown_content
        mock_urlopen.return_value.__enter__.return_value = mock_response

        open_notebook_from_url(url)

        # Assert that _convert_to_ipynb was called
        mock_convert.assert_called_once_with(url)

        # Assert that jupyter notebook was called to open the converted file
        mock_run.assert_called_once()
        args, _ = mock_run.call_args
        assert args[0][4] == str(tmp_path / "temp.ipynb")

        # Check that unlink was not called, since the file should still exist
        assert not (tmp_path / "temp.ipynb").exists()


def test_open_notebook_from_py_url(tmp_path: Path) -> None:
    """Test opening a .py (Jupytext) file from a URL."""
    mock_python_content = b'print("Hello from a test Python file")'
    url = "https://example.com/notebook.py"

    with (
        patch("urllib.request.urlopen") as mock_urlopen,
        patch("subprocess.run") as mock_run,
        patch("opennb._convert_to_ipynb", return_value=tmp_path / "temp.ipynb") as mock_convert,
    ):
        # Mock the response from urlopen for the python file
        mock_response = MagicMock()
        mock_response.read.return_value = mock_python_content
        mock_urlopen.return_value.__enter__.return_value = mock_response

        open_notebook_from_url(url)

        # Assert that _convert_to_ipynb was called
        mock_convert.assert_called_once_with(url)

        # Assert that jupyter notebook was called to open the converted file
        mock_run.assert_called_once()
        args, _ = mock_run.call_args
        assert args[0][4] == str(tmp_path / "temp.ipynb")

        # Check that unlink was not called, since the file should still exist
        assert not (tmp_path / "temp.ipynb").exists()


def test_convert_to_ipynb_success(tmp_path: Path) -> None:
    """Test successful conversion of a Jupytext file to .ipynb."""
    mock_markdown_content = b"# This is a test markdown file"
    url = "https://example.com/notebook.md"

    with (
        patch("urllib.request.urlopen") as mock_urlopen,
        patch("subprocess.run") as mock_run,
        patch(
            "tempfile.NamedTemporaryFile",
            return_value=NamedTemporaryFile(dir=tmp_path, delete=False),
        ) as mock_tempfile,
    ):
        # Mock the response from urlopen
        mock_response = MagicMock()
        mock_response.read.return_value = mock_markdown_content
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Mock subprocess.run to indicate successful conversion
        mock_run.return_value = MagicMock(returncode=0)

        temp_file_path = _convert_to_ipynb(url)

        assert temp_file_path.name == Path(mock_tempfile.return_value.name).name
        assert temp_file_path.suffix == ".ipynb"
        assert temp_file_path.parent == tmp_path
        mock_run.assert_called_once_with(
            [
                "python",
                "-m",
                "jupytext",
                "--to",
                "notebook",
                "--output",
                str(temp_file_path),
                "-",
            ],
            input=mock_markdown_content,
            check=True,
        )


def test_convert_to_ipynb_failure() -> None:
    """Test handling of Jupytext conversion failure."""
    mock_markdown_content = b"# This is a test markdown file"
    url = "https://example.com/notebook.md"

    with (
        patch("urllib.request.urlopen") as mock_urlopen,
        patch("subprocess.run") as mock_run,
        patch("tempfile.NamedTemporaryFile") as mock_tempfile,
        patch("pathlib.Path.unlink") as mock_unlink,
    ):
        # Mock the response from urlopen
        mock_response = MagicMock()
        mock_response.read.return_value = mock_markdown_content
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Mock the temporary file
        mock_tempfile.return_value.__enter__.return_value.name = "temp.ipynb"

        # Mock subprocess.run to simulate conversion error
        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd", "error")

        with pytest.raises(ValueError, match="Failed to convert markdown to Jupyter notebook"):
            _convert_to_ipynb(url)

        mock_unlink.assert_called_once()

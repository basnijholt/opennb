#!/usr/bin/env python3
"""Download and open a Jupyter notebook from a URL or GitHub repository."""

import subprocess
import urllib.request
import json
from pathlib import Path
from urllib.parse import urlparse


def _get_default_branch(owner: str, repo: str) -> str:
    """Get the default branch of a GitHub repository using GitHub's API.

    Parameters
    ----------
    owner
        Repository owner
    repo
        Repository name

    Returns
    -------
    Default branch name
    """
    url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read())
            return data["default_branch"]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise ValueError(f"Repository {owner}/{repo} not found") from e
        raise


def _convert_github_path_to_raw_url(path: str) -> str:
    """
    Convert a GitHub repository path to a raw content URL.

    Parameters
    ----------
    path
        GitHub repository path in one of these formats:
        - owner/repository/path/to/notebook.ipynb (uses default branch)
        - owner/repository@branch/name#path/to/notebook.ipynb

        Both branch names and file paths can contain slashes.
        The notebook path must end with .ipynb.

    Returns
    -------
    Raw content URL for the notebook
    """
    # First split on # to separate file path
    parts = path.split("#", 1)
    repo_part = parts[0]
    file_path = parts[1] if len(parts) > 1 else None

    # Then handle repository and branch
    if "@" in repo_part:
        repo_info, branch = repo_part.split("@", 1)
    else:
        repo_info = repo_part
        branch = None  # Will be set to default branch later

    # Parse owner/repository
    repo_parts = repo_info.strip("/").split("/")
    if len(repo_parts) != 2:
        raise ValueError("Repository path must be in format: owner/repository")
    owner, repo = repo_parts

    # If no branch specified, get the default branch
    if branch is None:
        branch = _get_default_branch(owner, repo)

    # Handle file path
    if file_path is None:
        # No # separator, so the file path must be in the branch part
        if "/" not in branch:
            raise ValueError("No file path specified")
        # Last part of branch is actually the file path
        branch, file_path = branch.split("/", 1)

    if not file_path.endswith(".ipynb"):
        raise ValueError("Path must end with .ipynb")

    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"


def open_notebook_from_url(
    url: str, output_dir: Path | None = None, jupyter_args: list[str] | None = None
) -> None:
    """
    Download a Jupyter notebook from URL or GitHub repository and open it.

    Parameters
    ----------
    url
        URL or GitHub path of the Jupyter notebook to download.
        For GitHub, use either format:
        - owner/repository/path/to/notebook.ipynb (uses default branch)
        - owner/repository@branch/name#path/to/notebook.ipynb
    output_dir
        Directory to save the notebook in. If None, uses current directory
    jupyter_args
        Additional arguments to pass to jupyter notebook command
    """
    # Check if it's a GitHub repository path
    if not url.startswith(("http://", "https://")):
        url = _convert_github_path_to_raw_url(url)

    # Parse the filename from the URL
    filename = Path(urlparse(url).path).name
    if not filename.endswith(".ipynb"):
        raise ValueError("URL must point to a Jupyter notebook (.ipynb file)")

    # Set output directory
    output_dir = output_dir or Path.cwd()
    output_path = output_dir / filename

    # Download the notebook
    print(f"Downloading notebook from {url}")
    urllib.request.urlretrieve(url, output_path)

    # Prepare jupyter notebook command
    cmd = ["jupyter", "notebook", str(output_path)]
    if jupyter_args:
        cmd.extend(jupyter_args)

    # Open the notebook
    print(f"Opening notebook {output_path}")
    subprocess.run(cmd, check=True)  # noqa: S603


def main() -> None:
    """Parse command line arguments and open the notebook."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Download and open a Jupyter notebook from URL or GitHub repository"
    )
    parser.add_argument(
        "url",
        help=(
            "URL or GitHub path. Examples:\n"
            "  - owner/repo#path/to/notebook.ipynb\n"
            "  - owner/repo@branch#path/to/notebook.ipynb\n"
            "  - owner/repo/path/to/notebook.ipynb\n"
            "  - https://example.com/notebook.ipynb"
        ),
    )
    parser.add_argument(
        "--output-dir", type=Path, help="Directory to save the notebook in"
    )
    parser.add_argument(
        "jupyter_args",
        nargs="*",
        help="Additional arguments to pass to jupyter notebook command",
    )

    # Parse known args first to handle --output-dir
    args, unknown = parser.parse_known_args()

    # Combine explicit jupyter_args with unknown args
    all_jupyter_args = args.jupyter_args + unknown

    open_notebook_from_url(args.url, args.output_dir, all_jupyter_args)


if __name__ == "__main__":
    main()

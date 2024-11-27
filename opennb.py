#!/usr/bin/env python3
"""Download and open a Jupyter notebook from a URL or GitHub repository."""

import json
import subprocess
import urllib.request
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
        with urllib.request.urlopen(url) as response:  # noqa: S310
            data = json.loads(response.read())
            return data["default_branch"]
    except urllib.error.HTTPError as e:
        if e.code == 404:  # noqa: PLR2004
            msg = f"Repository {owner}/{repo} not found"
            raise ValueError(msg) from e
        raise


def _convert_github_path_to_raw_url(path: str) -> str:
    """Convert a GitHub repository path to a raw content URL.

    Parameters
    ----------
    path
        GitHub repository path in one of these formats:
        - owner/repository/path/to/notebook.ipynb (uses default branch)
        - owner/repository@branch#path/to/notebook.ipynb

    Returns
    -------
    Raw content URL for the notebook

    """
    if "@" in path:
        # Handle owner/repo@branch#path format
        repo_part, rest = path.split("@", 1)
        if "#" not in rest:
            msg = (
                "When using @branch, the path must be specified after # "
                "(e.g., owner/repo@branch#path/to/notebook.ipynb)"
            )
            raise ValueError(msg)
        branch, file_path = rest.split("#", 1)
        repo_parts = repo_part.strip("/").split("/")
        if len(repo_parts) != 2:  # noqa: PLR2004
            msg = "Repository path must be in format: owner/repository"
            raise ValueError(msg)
        owner, repo = repo_parts
    else:
        # Handle owner/repo/path format
        parts = path.strip("/").split("/")
        if len(parts) < 3:  # noqa: PLR2004
            msg = "Path must be in format: owner/repository/path/to/notebook.ipynb"
            raise ValueError(msg)
        owner, repo = parts[:2]
        file_path = "/".join(parts[2:])
        branch = _get_default_branch(owner, repo)

    if not file_path.endswith(".ipynb"):
        msg = "Path must end with .ipynb"
        raise ValueError(msg)

    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"


def open_notebook_from_url(
    url: str,
    output_dir: Path | None = None,
    jupyter_args: list[str] | None = None,
) -> None:
    """Download a Jupyter notebook from URL or GitHub repository and open it.

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
        msg = "URL must point to a Jupyter notebook (.ipynb file)"
        raise ValueError(msg)

    # Set output directory
    output_dir = output_dir or Path.cwd()
    output_path = output_dir / filename

    # Download the notebook
    print(f"Downloading notebook from {url}")
    urllib.request.urlretrieve(url, output_path)  # noqa: S310

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
        description="Download and open a Jupyter notebook from URL or GitHub repository",
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
    parser.add_argument("--output-dir", type=Path, help="Directory to save the notebook in")
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

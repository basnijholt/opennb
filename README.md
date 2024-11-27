# opennb 📓

[![PyPI](https://img.shields.io/pypi/v/opennb)](https://pypi.org/project/opennb/)
[![Python Versions](https://img.shields.io/pypi/pyversions/opennb)](https://pypi.org/project/opennb/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pytest](https://github.com/basnijholt/opennb/actions/workflows/pytest-uv.yml/badge.svg)](https://github.com/basnijholt/opennb/actions/workflows/pytest-uv.yml)

📓 Open Jupyter notebooks from GitHub repositories or URLs directly in Jupyter.
Very useful in conjunction with [`uvx`](https://docs.astral.sh/uv/concepts/tools/#tools).

> [!TIP]
> Try `uvx --with "pipefunc[docs]" opennb pipefunc/pipefunc/example.ipynb` to open a notebook from the [`pipefunc`](https://github.com/pipefunc/pipefunc) repository and ensure its dependencies are installed.

<details>
<summary>ToC</summary>
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Features](#features)
- [Usage](#usage)
  - [Arguments](#arguments)
- [Examples](#examples)
- [Installation](#installation)
- [License](#license)
- [Contributing](#contributing)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->
</details>

## Features

- 📦 Open notebooks directly from GitHub repositories
- 🔄 Automatic default branch detection
- 🌳 Support for specific branches
- 🔗 Direct URL support
- 🚀 Pass-through of Jupyter notebook arguments
- 📥 Integration with `uvx` for dependency management

## Usage

Open a notebook from a GitHub repository:

```bash
opennb owner/repo/path/to/notebook.ipynb
```

This defaults to the default branch of the repository.

Or specify a specific branch:

```bash
opennb owner/repo@branch#path/to/notebook.ipynb
```

Open directly from a URL:

```bash
opennb https://example.com/notebook.ipynb
```

> [!IMPORTANT]
> `opennb` is especially useful when used with [`uvx`](https://docs.astral.sh/uv/guides/tools/).

Use with `uvx` to install dependencies and open a notebook in one go:

```bash
uvx --with dependency opennb owner/repo/path/to/notebook.ipynb
```

For example, to open a notebook from the `pipefunc` repository and ensure its dependencies are installed:

```bash
uvx --with "pipefunc[docs]" opennb pipefunc/pipefunc/example.ipynb
```

### Arguments

All arguments after the notebook specification are passed directly to `jupyter notebook`:

```bash
opennb owner/repo/notebook.ipynb --port 8888 --no-browser
```

## Examples

Open a notebook from the main branch:

```bash
opennb owner/repo/notebook.ipynb
```

Open from a specific branch:

```bash
opennb jupyter/notebook@main#docs/source/examples/Notebook/Notebook%20Basics.ipynb
```

Open with custom Jupyter settings:

```bash
opennb owner/repo/notebook.ipynb --NotebookApp.token='my-token'
```

## Installation

Install using pip:

```bash
pip install opennb
```

Or using [uv](https://github.com/astral-sh/uv):

```bash
uv pip install opennb
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

# opennb 📓

[![PyPI](https://img.shields.io/pypi/v/opennb)](https://pypi.org/project/opennb/)
[![Python Versions](https://img.shields.io/pypi/pyversions/opennb)](https://pypi.org/project/opennb/)

📓 Open Jupyter notebooks from GitHub repositories or URLs directly in Jupyter.
Very useful in conjunction with [`uv run`](https://docs.astral.sh/uv/guides/projects/#running-commands).

## Installation

Install using pip:

```bash
pip install opennb
```

Or using [uv](https://github.com/astral-sh/uv):

```bash
uv pip install opennb
```

## Usage

Open a notebook from a GitHub repository:

```bash
opennb owner/repo#path/to/notebook.ipynb
```

Specify a branch:

```bash
opennb owner/repo@branch#path/to/notebook.ipynb
```

Open directly from a URL:

```bash
opennb https://example.com/notebook.ipynb
```

Use with `uv run` to install dependencies and open a notebook in one go:

```bash
uv run --from owner/repo opennb owner/repo#path/to/notebook.ipynb
```

For example, to open a notebook from the `pipefunc` repository and ensure its dependencies are installed:

```bash
uv run --from pipefunc --from notebook opennb pipefunc/pipefunc/example.ipynb
```

### Arguments

All arguments after the notebook specification are passed directly to `jupyter notebook`:

```bash
opennb owner/repo#notebook.ipynb --port 8888 --no-browser
```

## Examples

Open a notebook from the main branch:

```bash
opennb scipy/scipy#doc/source/tutorial/basic.ipynb
```

Open from a specific branch:

```bash
opennb pandas-dev/pandas@main#doc/source/getting_started/intro_tutorials/01_table_oriented.ipynb
```

Open with custom Jupyter settings:

```bash
opennb owner/repo#notebook.ipynb --NotebookApp.token='my-token'
```

## Features

- 📦 Open notebooks directly from GitHub repositories
- 🔄 Automatic default branch detection
- 🌳 Support for specific branches
- 🔗 Direct URL support
- 🚀 Pass-through of Jupyter notebook arguments
- 📥 Integration with `uv run` for dependency management

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

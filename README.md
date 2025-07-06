# uithub-local

Flatten a local Git repository into a single text dump with an approximate token count.

## Quick Start

```bash
pip install .

uithub path/to/repo --include "*.py" --exclude "tests/*"
```

## Usage

Run `uithub --help` for all options. The dump can be printed to STDOUT or saved to a file. JSON output is available using `--format json`.

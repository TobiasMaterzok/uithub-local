# uithub-local

Flatten a local or remote Git repository into a single text dump with an approximate token count.

## Quick Start

```bash
pip install .

uithub path/to/repo --include "*.py" --exclude "tests/*"

# remote repo
uithub --remote-url https://github.com/user/private --private-token $GITHUB_TOKEN --no-stdout
```

## Usage

Run `uithub --help` for all options. The dump can be printed to STDOUT or saved to a file. JSON output is available using `--format json`. Use `--remote-url` and optionally `--private-token` to process remote repositories.

## Tests

Install dev dependencies and run:

```bash
pip install .[test]
make test
```

# uithub-local

Flatten a local Git repository into a single text dump with an approximate token count.

## Quick Start

```bash
pip install .

uithub path/to/repo --include "*.py" --exclude "tests/*"
uithub --remote-url https://github.com/owner/repo
```

## Usage

Run `uithub --help` for all options. The dump can be printed to STDOUT or saved to a file. JSON output is available using `--format json`. Remote repositories can be processed with `--remote-url`; provide `--private-token` or set `GITHUB_TOKEN` for private repos. Use `--max-size` to skip files larger than the given number of bytes (default 1048576).

### Running the test-suite

Install development dependencies and run tests:

```bash
pip install .[test]
uithub-local.test
```

### Adjusting file size limit

The `--max-size` option expects bytes. Raise it if needed, e.g.:

```bash
uithub path/to/repo --max-size $((2 * 1048576))
```

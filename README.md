# uithub-local

Flatten a local Git repository into a single text dump with an approximate token count.

## About
Uithub-local packages repository contents into plain text, JSON or HTML dumps. Use it to prep code for large-context LLMs or save lightweight archives.

## Quick Start

```bash
pip install .

# trailing slash means recursive
uithub path/to/repo --include "*.py" --exclude "tests/"
uithub --remote-url https://github.com/owner/repo
```

## Usage

Run `uithub --help` for all options. The dump can be printed to STDOUT or saved to a file. JSON output is available using `--format json`. Use `--format html` for a self-contained HTML dump with collapsible sections. Remote repositories can be processed with `--remote-url`; provide `--private-token` or set `GITHUB_TOKEN` for private repos. Use `--max-size` to skip files larger than the given number of bytes (default 1048576).
`.git/` directories are skipped automatically unless explicitly included.

To save an HTML dump and open it in your default browser:

```bash
uithub path/to/repo --format html --outfile dump.html && xdg-open dump.html
```

The generated HTML arranges files in collapsible "file cards" styled for a dark
theme. Cards sit on a charcoal background with light text and a bright blue
accent. A small chevron rotates when a card is opened, and file paths truncate
in the middle to keep extensions visible. Code blocks scroll horizontally and
cards are stacked in a centred container with a subtle drop shadow.

Save a plain text dump with explicit encoding:

```bash
uithub path/to/repo --outfile dump.txt --encoding utf-8
```

### Running the test-suite

Install development dependencies and run tests with coverage:

```bash
pip install .[test]
pytest --cov=uithub_local -q
```

### Adjusting file size limit

The `--max-size` option expects bytes. Raise it if needed, e.g.:

```bash
uithub path/to/repo --max-size $((2 * 1048576))
```

## Changelog

### 0.1.3
- Directory patterns now match recursively ("dir/" excludes everything under it).
- `.git/` is excluded automatically unless explicitly included.
- Correct repo name shown when dumping `.`.
### 0.1.2
- Added ``--encoding`` option for file output.
- Fixed UTF-8 writes when saving dumps.

### 0.1.1
- HTML export improvements (lang attribute, mobile viewport, truncated summaries).
- Programmatic `dump_repo` helper function.
- Coverage gate at 90%.

### 0.1.0
- Initial release.

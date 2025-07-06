"""CLI entry point for uithub-local."""

from __future__ import annotations

from pathlib import Path
from typing import List

import click

from .renderer import render
from .walker import collect_files


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("path", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--include", multiple=True, default=["*"], help="Glob(s) to include")
@click.option("--exclude", multiple=True, help="Glob(s) to exclude")
@click.option("--max-tokens", type=int, help="Hard cap; truncate largest files first")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
@click.option("--stdout/--no-stdout", default=True, help="Print dump to STDOUT")
@click.option("--outfile", type=click.Path(path_type=Path), help="Write dump to file")
@click.version_option()
def main(
    path: Path,
    include: List[str],
    exclude: List[str],
    max_tokens: int | None,
    fmt: str,
    stdout: bool,
    outfile: Path | None,
) -> None:
    """Flatten a repository into one text dump."""
    try:
        files = collect_files(path, include, exclude)
        output = render(files, path, max_tokens=max_tokens, fmt=fmt)
    except Exception as exc:  # pragma: no cover - fatal CLI errors
        click.echo(str(exc), err=True)
        raise SystemExit(1)

    if outfile:
        outfile.write_text(output)
    if stdout:
        click.echo(output)


if __name__ == "__main__":  # pragma: no cover
    main()

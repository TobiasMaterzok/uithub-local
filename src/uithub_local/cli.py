"""CLI entry point for uithub-local."""

from __future__ import annotations

from pathlib import Path
from typing import List

import click

from .downloader import download_repo
from .renderer import render
from .walker import collect_files


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument(
    "path",
    required=False,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.option("--remote-url", help="Download and use remote repository")
@click.option(
    "--private-token",
    envvar="GITHUB_TOKEN",
    help="Token for private repository",
)
@click.option("--include", multiple=True, default=["*"], help="Glob(s) to include")
@click.option("--exclude", multiple=True, help="Glob(s) to exclude")
@click.option("--max-tokens", type=int, help="Hard cap; truncate largest files first")
@click.option(
    "--max-size",
    type=int,
    default=1_048_576,
    show_default=True,
    help="Skip files larger than this size (bytes)",
)
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
@click.option("--stdout/--no-stdout", default=True, help="Print dump to STDOUT")
@click.option("--outfile", type=click.Path(path_type=Path), help="Write dump to file")
@click.version_option()
def main(
    path: Path | None,
    remote_url: str | None,
    private_token: str | None,
    include: List[str],
    exclude: List[str],
    max_tokens: int | None,
    max_size: int,
    fmt: str,
    stdout: bool,
    outfile: Path | None,
) -> None:
    """Flatten a repository into one text dump."""

    if not path and not remote_url:
        raise click.UsageError("Provide PATH or --remote-url")
    if path and remote_url:
        raise click.UsageError("Cannot combine PATH and --remote-url")

    try:
        if remote_url:
            with download_repo(remote_url, private_token) as tmp:
                files = collect_files(tmp, include, exclude, max_size=max_size)
                output = render(files, tmp, max_tokens=max_tokens, fmt=fmt)
        else:
            assert path is not None
            files = collect_files(path, include, exclude, max_size=max_size)
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

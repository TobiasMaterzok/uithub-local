"""High-level programmatic API for uithub-local."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .downloader import download_repo
from .renderer import render
from .walker import DEFAULT_MAX_SIZE, collect_files


def dump_repo(
    path_or_url: str | Path,
    *,
    fmt: str = "text",
    encoding: str = "utf-8",
    **cli_kwargs: Any,
) -> str:
    """Return a repository dump as a string.

    Parameters
    ----------
    path_or_url:
        Local directory or remote repository URL.
    fmt:
        Output format ("text", "json" or "html").
    encoding:
        Encoding to use when writing the returned dump to disk.
    **cli_kwargs:
        Extra options matching the CLI, such as ``include``, ``exclude``,
        ``max_size``, ``max_tokens``, ``binary_strict`` and ``private_token``.
    This function does not write to disk. Callers can write the returned
    string using ``Path.write_text(output, encoding=encoding)``.
    """

    include = cli_kwargs.get("include", ["*"])
    exclude = cli_kwargs.get("exclude", [])
    max_size = cli_kwargs.get("max_size", DEFAULT_MAX_SIZE)
    max_tokens = cli_kwargs.get("max_tokens")
    binary_strict = cli_kwargs.get("binary_strict", True)
    private_token = cli_kwargs.get("private_token")

    path = Path(path_or_url)
    if path.exists():
        files = collect_files(
            path,
            include,
            exclude,
            max_size=max_size,
            binary_strict=binary_strict,
        )
        return render(files, path, max_tokens=max_tokens, fmt=fmt)

    url = str(path_or_url)
    with download_repo(url, private_token) as tmp:
        files = collect_files(
            tmp,
            include,
            exclude,
            max_size=max_size,
            binary_strict=binary_strict,
        )
        return render(files, tmp, max_tokens=max_tokens, fmt=fmt)

"""Safe file loader with encoding fallback."""

from __future__ import annotations

from pathlib import Path


MAX_SIZE = 1_048_576  # 1 MiB


def load_text(path: Path) -> str:
    """Return text of *path*, skipping files larger than ``MAX_SIZE``.

    Text is read with UTF-8 and fallback to ``errors='replace'``.
    """
    if path.stat().st_size > MAX_SIZE:
        raise ValueError("File too large")

    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")

"""Utility helpers for uithub-local."""

from __future__ import annotations

import mimetypes
from pathlib import Path


def is_binary_path(path: Path) -> bool:
    """Return True if file looks binary."""
    mime, _ = mimetypes.guess_type(path.as_posix())
    if mime is not None and not mime.startswith("text"):
        return True
    try:
        with open(path, "rb") as fh:
            chunk = fh.read(1024)
        return b"\0" in chunk
    except OSError:
        return True

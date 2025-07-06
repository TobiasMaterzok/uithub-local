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
            chunk = fh.read(8192)
        if b"\0" in chunk:
            return True
        non_text = sum(byte < 9 or 14 <= byte < 32 or byte > 127 for byte in chunk)
        return non_text / len(chunk) > 0.3 if chunk else False
    except OSError:
        return True

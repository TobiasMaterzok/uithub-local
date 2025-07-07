"""Collects file paths and metadata."""

from __future__ import annotations

import fnmatch
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from .utils import is_binary_path

DEFAULT_MAX_SIZE = 1_048_576


@dataclass
class FileInfo:
    """Metadata about a file in the repository."""

    path: Path
    size: int
    mtime: float


def collect_files(
    path: Path,
    include: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
    max_size: int = DEFAULT_MAX_SIZE,
    *,
    binary_strict: bool = True,
) -> List[FileInfo]:
    """Return list of readable, non-binary files under *path*.

    Parameters
    ----------
    path:
        Directory to walk.
    include:
        Glob patterns to include.
    exclude:
        Glob patterns to exclude.
    max_size:
        Skip files larger than this number of bytes.
    binary_strict:
        Use strict binary detection.
    """
    include = list(include or ["*"])
    exclude = list(exclude or [])
    files: List[FileInfo] = []
    root = Path(path)

    for file in root.rglob("*"):
        rel = file.relative_to(root)
        if not file.is_file():
            continue
        if not any(fnmatch.fnmatch(str(rel), pattern) for pattern in include):
            continue
        if any(fnmatch.fnmatch(str(rel), pattern) for pattern in exclude):
            continue
        if is_binary_path(file, strict=binary_strict):
            continue
        try:
            stat = file.stat()
            if not os.access(file, os.R_OK):
                continue
        except OSError:
            continue
        if stat.st_size > max_size:
            continue
        files.append(FileInfo(path=rel, size=stat.st_size, mtime=stat.st_mtime))
    return files

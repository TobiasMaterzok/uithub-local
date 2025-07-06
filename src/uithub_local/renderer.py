"""Render repository files into a single dump."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from .loader import load_text
from .tokenizer import approximate_tokens
from .walker import FileInfo


class FileDump:
    """A file plus its loaded contents and token count."""

    def __init__(self, info: FileInfo, root: Path) -> None:
        self.path = info.path
        self.full_path = root / info.path
        self.size = info.size
        self.tokens = 0
        self.content = ""
        try:
            self.content = load_text(self.full_path)
            self.tokens = approximate_tokens(self.content)
        except Exception:
            self.content = ""
            self.tokens = 0


class Dump:
    def __init__(
        self,
        files: List[FileInfo],
        root: Path,
        max_tokens: int | None = None,
    ) -> None:
        self.root = root
        self.file_dumps: List[FileDump] = [FileDump(info, root) for info in files]
        self.total_tokens = sum(fd.tokens for fd in self.file_dumps)
        if max_tokens is not None and self.total_tokens > max_tokens:
            self._truncate(max_tokens)

    def _truncate(self, limit: int) -> None:
        self.file_dumps.sort(key=lambda f: f.tokens, reverse=True)
        while self.total_tokens > limit and self.file_dumps:
            victim = self.file_dumps.pop(0)
            self.total_tokens -= victim.tokens

    def as_text(self, repo_name: str) -> str:
        timestamp = datetime.now(timezone.utc).isoformat()
        lines = [f"# Uithub-local dump – {repo_name} – {timestamp}"]
        lines.append(f"# ≈ {self.total_tokens} tokens")
        for fd in self.file_dumps:
            lines.append(f"\n### {fd.path.as_posix()}")
            lines.append(fd.content)
        lines.append("")
        return "\n".join(lines)

    def as_json(self, repo_name: str) -> str:
        obj = {
            "repo": repo_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_tokens": self.total_tokens,
            "files": [
                {
                    "path": fd.path.as_posix(),
                    "contents": fd.content,
                    "tokens": fd.tokens,
                }
                for fd in self.file_dumps
            ],
        }
        return json.dumps(obj, indent=2)


def render(
    files: List[FileInfo],
    root: Path,
    *,
    max_tokens: int | None = None,
    fmt: str = "text",
) -> str:
    dump = Dump(files, root, max_tokens)
    repo_name = root.name
    if fmt == "json":
        return dump.as_json(repo_name)
    return dump.as_text(repo_name)

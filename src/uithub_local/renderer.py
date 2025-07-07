"""Render repository files into a single dump."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List
import html

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
        self.file_dumps.sort(key=lambda f: (f.tokens, f.path.as_posix()), reverse=True)
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

    def as_html(self, repo_name: str) -> str:
        timestamp = datetime.now(timezone.utc).isoformat()
        style = """
        <style>
        body {background:#f7f7f7;font:16px/1.5 system-ui,monospace;}
        .container {max-width:800px;margin:2rem auto;}
        details {margin:0.5rem 0;box-shadow:0 1px 3px rgba(0,0,0,0.1);}
        summary {
            background:#34495e;
            color:#fff;
            font-weight:bold;
            padding:0.75rem 1rem;
            border:1px solid #2c3e50;
            border-radius:4px;
            cursor:pointer;
            display:flex;
            align-items:center;
        }
        summary:hover {background:#3b5770;}
        summary::-webkit-details-marker {display:none;}
        summary::before {
            content:'\25B6';
            display:inline-block;
            margin-right:0.5rem;
            transition:transform 0.2s;
        }
        details[open] summary::before {transform:rotate(90deg);}
        details[open] > summary {
            border-bottom-left-radius:0;
            border-bottom-right-radius:0;
        }
        pre {
            background:#fff;
            font-family:monospace;
            overflow:auto;
            padding:1rem;
            margin:0;
            border:1px solid #2c3e50;
            border-top:none;
            border-radius:0 0 4px 4px;
        }
        </style>
        """
        lines = [
            "<!DOCTYPE html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="UTF-8">',
            '<meta name="viewport" content="width=device-width,initial-scale=1">',
            f"<title>{repo_name} dump</title>",
            style,
            "</head>",
            "<body>",
            "<div class='container'>",
            f"<h1>Uithub-local dump – {repo_name} – {timestamp}</h1>",
            f"<p>≈ {self.total_tokens} tokens</p>",
        ]
        for fd in self.file_dumps:
            lines.append("<details>")
            lines.append(f"<summary>{fd.path.as_posix()}</summary>")
            lines.append("<pre><code>")
            lines.append(html.escape(fd.content))
            lines.append("</code></pre>")
            lines.append("</details>")
        lines.append("</div></body></html>")
        return "\n".join(lines)


def render(
    files: List[FileInfo],
    root: Path,
    *,
    max_tokens: int | None = None,
    fmt: str = "text",
) -> str:
    dump = Dump(files, root, max_tokens)
    resolved = root.resolve()
    repo_name = resolved.name or resolved.parent.name
    if fmt == "json":
        return dump.as_json(repo_name)
    if fmt == "html":
        return dump.as_html(repo_name)
    return dump.as_text(repo_name)

"""Remote repository downloader."""

from __future__ import annotations

import contextlib
import io
import tempfile
import zipfile
from pathlib import Path
from typing import Iterator

import requests  # type: ignore


def _zip_url(remote_url: str, branch: str = "main", private: bool = False) -> str:
    if remote_url.endswith(".git"):
        remote_url = remote_url[:-4]
    if remote_url.startswith("https://"):
        base = remote_url
    else:
        base = f"https://github.com/{remote_url}"

    if "github.com" in base:
        if private:
            return f"https://api.github.com/repos/{base.split('github.com/')[-1]}/zipball/{branch}"
        return f"{base}/archive/refs/heads/{branch}.zip"
    if "bitbucket.org" in base:
        return f"{base}/get/{branch}.zip"
    raise ValueError("Unsupported remote host")


@contextlib.contextmanager
def download_repo(remote_url: str, token: str | None = None) -> Iterator[Path]:
    """Yield a temporary directory with the downloaded repo."""

    private = token is not None
    url = _zip_url(remote_url, private=private)
    headers = {"Authorization": f"token {token}"} if token else {}
    with tempfile.TemporaryDirectory() as td:
        dest = Path(td)
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = io.BytesIO(resp.content)
        with zipfile.ZipFile(data) as zf:
            zf.extractall(dest)
        roots = [p for p in dest.iterdir() if p.is_dir()]
        yield roots[0] if len(roots) == 1 else dest

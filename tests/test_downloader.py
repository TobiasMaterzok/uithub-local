import io
import zipfile

import responses
import pytest

from uithub_local.downloader import download_repo


@responses.activate
def test_download_repo(tmp_path):
    data = io.BytesIO()
    with zipfile.ZipFile(data, "w") as zf:
        zf.writestr("repo/file.txt", "hello")
    responses.add(
        responses.GET,
        "https://api.github.com/repos/foo/bar/zipball",
        body=data.getvalue(),
        status=200,
        content_type="application/zip",
    )
    with download_repo("https://github.com/foo/bar") as path:
        assert (path / "file.txt").read_text() == "hello"


@responses.activate
def test_download_repo_with_token():
    data = io.BytesIO()
    with zipfile.ZipFile(data, "w") as zf:
        zf.writestr("repo/f.txt", "x")
    responses.add(
        responses.GET,
        "https://api.github.com/repos/foo/bar/zipball",
        body=data.getvalue(),
        status=200,
        content_type="application/zip",
    )
    with download_repo("foo/bar", token="t") as path:
        assert (path / "f.txt").read_text() == "x"


def test_archive_url_invalid():
    from uithub_local.downloader import _archive_url

    with pytest.raises(ValueError):
        _archive_url("https://example.com/foo.git")

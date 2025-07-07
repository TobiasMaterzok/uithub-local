import io
import zipfile

import responses
import pytest

from uithub_local.downloader import download_repo, _archive_url


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


@responses.activate
def test_download_repo_gitlab_retry(tmp_path):
    data = io.BytesIO()
    with zipfile.ZipFile(data, "w") as zf:
        zf.writestr("repo/g.txt", "hi")
    url = "https://gitlab.com/foo/bar/-/archive/master/bar-master.zip"
    responses.add(responses.GET, url, status=500)
    responses.add(
        responses.GET,
        url,
        body=data.getvalue(),
        status=200,
        content_type="application/zip",
    )
    with download_repo("https://gitlab.com/foo/bar") as path:
        assert (path / "g.txt").read_text() == "hi"
    assert len(responses.calls) == 2


def test_archive_url_invalid():
    with pytest.raises(ValueError):
        _archive_url("https://example.com/foo.git")


def test_archive_url_gitlab_and_zip():
    gitlab = _archive_url("https://gitlab.com/foo/bar")
    assert gitlab == "https://gitlab.com/foo/bar/-/archive/master/bar-master.zip"
    direct = _archive_url("https://example.com/archive.zip")
    assert direct == "https://example.com/archive.zip"


def test_archive_url_scp_style():
    url = _archive_url("git@github.com:foo/bar.git")
    assert url == "https://api.github.com/repos/foo/bar/zipball"

import io
import zipfile

import responses

from uithub_local.downloader import download_repo, _zip_url


@responses.activate
def test_download_repo(tmp_path):
    # Create in-memory zip
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("repo-main/hello.txt", "hi")
    buf.seek(0)

    url = "https://github.com/user/repo"
    zip_url = "https://github.com/user/repo/archive/refs/heads/main.zip"
    responses.add(responses.GET, zip_url, body=buf.getvalue(), status=200)

    with download_repo(url) as path:
        assert (path / "hello.txt").read_text() == "hi"


def test_zip_url_variants():
    assert _zip_url("user/repo").startswith("https://github.com/user/repo")
    assert _zip_url("https://bitbucket.org/team/proj.git").endswith("/get/main.zip")
    assert _zip_url("user/private", private=True).startswith(
        "https://api.github.com/repos/user/private/zipball/"
    )

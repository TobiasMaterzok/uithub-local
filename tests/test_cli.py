from pathlib import Path

import io
import zipfile
import responses
from click.testing import CliRunner

from uithub_local.cli import main


def test_cli_basic(tmp_path: Path):
    (tmp_path / "a.txt").write_text("hello")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path)])
    assert result.exit_code == 0
    assert "hello" in result.output


def test_cli_outfile(tmp_path: Path):

    (tmp_path / "a.txt").write_text("hello")
    outfile = tmp_path / "out.txt"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [str(tmp_path), "--outfile", str(outfile), "--no-stdout"],
    )
    assert result.exit_code == 0
    assert outfile.read_text()


@responses.activate
def test_cli_remote(tmp_path: Path):

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("repo-main/a.txt", "hello")
    buf.seek(0)
    url = "https://github.com/user/repo"
    zip_url = "https://github.com/user/repo/archive/refs/heads/main.zip"
    responses.add(responses.GET, zip_url, body=buf.getvalue(), status=200)

    runner = CliRunner()
    result = runner.invoke(main, ["--remote-url", url, "--no-stdout"])
    assert result.exit_code == 0

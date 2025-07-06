from pathlib import Path

from click.testing import CliRunner
import io
import zipfile
import responses

from uithub_local.cli import main


def test_cli_basic(tmp_path: Path):
    (tmp_path / "a.txt").write_text("hello")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path)])
    assert result.exit_code == 0
    assert "hello" in result.output


def test_cli_outfile(tmp_path: Path):
    from click.testing import CliRunner

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
    data = io.BytesIO()
    with zipfile.ZipFile(data, "w") as zf:
        zf.writestr("repo/file.txt", "hi")
    responses.add(
        responses.GET,
        "https://api.github.com/repos/foo/bar/zipball",
        body=data.getvalue(),
        status=200,
        content_type="application/zip",
    )
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--remote-url", "https://github.com/foo/bar", "--no-stdout"],
    )
    assert result.exit_code == 0

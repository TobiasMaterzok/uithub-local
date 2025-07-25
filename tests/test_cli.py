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


def test_cli_outfile_utf8(tmp_path: Path):
    (tmp_path / "a.txt").write_text("hi")
    out = tmp_path / "out.txt"
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path), "--outfile", str(out)])
    assert result.exit_code == 0
    assert out.read_text(encoding="utf-8").startswith("# Uithub-local")


def test_cli_outfile_cp1252(tmp_path: Path):
    (tmp_path / "a.txt").write_text("hi")
    out = tmp_path / "o.txt"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [str(tmp_path), "--outfile", str(out), "--encoding", "cp1252", "--no-stdout"],
    )
    assert result.exit_code == 0
    assert out.read_text(encoding="cp1252").startswith("# Uithub-local")


def test_cli_max_size(tmp_path: Path):
    from uithub_local.walker import DEFAULT_MAX_SIZE

    big = tmp_path / "big.txt"
    big.write_bytes(b"x" * (DEFAULT_MAX_SIZE + 1))
    (tmp_path / "small.txt").write_text("ok")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path)])
    assert result.exit_code == 0
    assert "big.txt" not in result.output
    result = runner.invoke(
        main, [str(tmp_path), "--max-size", str(DEFAULT_MAX_SIZE * 2)]
    )
    assert result.exit_code == 0
    assert "big.txt" in result.output


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
        ["--remote-url", "https://github.com/foo/bar"],
    )
    assert result.exit_code == 0
    assert "file.txt" in result.output
    assert "hi" in result.output


def test_cli_no_binary_strict(tmp_path: Path):
    noisy = tmp_path / "n.txt"
    noisy.write_bytes(b"\x80" * 40 + b"a" * 10)
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path), "--no-binary-strict"])
    assert result.exit_code == 0
    assert "n.txt" in result.output


def test_cli_html(tmp_path: Path):
    (tmp_path / "a.txt").write_text("hello")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path), "--format", "html"])
    assert result.exit_code == 0
    assert "<details class='file-card'>" in result.output


def test_cli_exclude_directory(tmp_path: Path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "data").write_text("x")
    (tmp_path / "a.txt").write_text("hi")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path), "--exclude", ".git"])
    assert result.exit_code == 0
    assert ".git/data" not in result.output
    assert "a.txt" in result.output


def test_cli_exclude_tests(tmp_path: Path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "a.txt").write_text("x")
    (tmp_path / "b.txt").write_text("y")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path), "--exclude", "tests/"])
    assert result.exit_code == 0
    assert "tests/a.txt" not in result.output
    assert "b.txt" in result.output


def test_cli_auto_excludes_git(tmp_path: Path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("x")
    (tmp_path / "a.txt").write_text("hi")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path)])
    assert result.exit_code == 0
    assert ".git/config" not in result.output

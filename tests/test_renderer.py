from pathlib import Path, PureWindowsPath
import pytest

from freezegun import freeze_time

from uithub_local.renderer import render
from uithub_local.walker import collect_files, FileInfo
from uithub_local.tokenizer import approximate_tokens


golden = Path(__file__).parent / "golden" / "dump.txt"


@freeze_time("2024-01-01T00:00:00+00:00")
def test_render_text(tmp_path: Path):
    (tmp_path / "a.txt").write_text("hello")
    files = collect_files(tmp_path, ["*"], [])
    output = render(files, tmp_path)
    expected = golden.read_text().strip()
    # Replace repo name 'sample' with actual tmp dir name
    expected = expected.replace("sample", tmp_path.name)
    assert output.strip() == expected


@freeze_time("2024-01-01T00:00:00+00:00")
def test_render_json(tmp_path: Path):
    import json

    (tmp_path / "a.txt").write_text("hello")
    files = collect_files(tmp_path, ["*"], [])
    output = render(files, tmp_path, fmt="json")
    data = json.loads(output)
    assert data["repo"] == tmp_path.name
    assert data["total_tokens"] > 0


@freeze_time("2024-01-01T00:00:00+00:00")
def test_render_truncate(tmp_path: Path):
    (tmp_path / "a.txt").write_text("a" * 100)
    (tmp_path / "b.txt").write_text("b" * 100)
    files = collect_files(tmp_path, ["*.txt"], [])
    # limit tokens to roughly one file
    output = render(files, tmp_path, max_tokens=approximate_tokens("a" * 100))
    assert "a.txt" in output
    assert "b.txt" not in output


@freeze_time("2024-01-01T00:00:00+00:00")
def test_render_html(tmp_path: Path):
    (tmp_path / "a.txt").write_text("hello")
    files = collect_files(tmp_path, ["*"], [])
    output = render(files, tmp_path, fmt="html")
    assert "<h1>Uithub-local dump" in output
    assert "<details>" in output
    assert "hello" in output


@freeze_time("2024-01-01T00:00:00+00:00")
@pytest.mark.parametrize("path_cls", [Path, PureWindowsPath])
def test_render_windows_paths(tmp_path: Path, path_cls):
    (tmp_path / "a.txt").write_text("hello")
    files = collect_files(tmp_path, ["*"], [])
    files = [FileInfo(path_cls(f.path.as_posix()), f.size, f.mtime) for f in files]
    output = render(files, tmp_path)
    assert "a.txt" in output


@freeze_time("2024-01-01T00:00:00+00:00")
def test_render_repo_name_dot(tmp_path: Path, monkeypatch):
    (tmp_path / "a.txt").write_text("hi")
    monkeypatch.chdir(tmp_path)
    files = collect_files(Path("."), ["*"], [])
    output = render(files, Path("."))
    assert tmp_path.name in output.splitlines()[0]

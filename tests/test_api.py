from pathlib import Path

from uithub_local import dump_repo


def test_dump_repo(tmp_path: Path):
    (tmp_path / "a.txt").write_text("hi")
    output = dump_repo(tmp_path, fmt="text")
    assert "hi" in output

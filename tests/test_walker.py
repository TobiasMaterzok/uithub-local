def test_collect_files_exclude_binary(tmp_path):
    from uithub_local.walker import collect_files

    (tmp_path / "bin").write_bytes(b"\0\1")
    (tmp_path / "a.txt").write_text("hi")
    files = collect_files(tmp_path, ["*"], [])
    assert len(files) == 1
    assert files[0].path.name == "a.txt"


def test_collect_files_respects_max_size(tmp_path):
    from uithub_local.walker import collect_files, DEFAULT_MAX_SIZE

    big = tmp_path / "big.txt"
    big.write_bytes(b"x" * (DEFAULT_MAX_SIZE + 1))
    small = tmp_path / "a.txt"
    small.write_text("hi")
    files = collect_files(tmp_path, ["*"], [], max_size=DEFAULT_MAX_SIZE)
    names = {f.path.name for f in files}
    assert names == {"a.txt"}


def test_collect_files_exclude_dir(tmp_path):
    from uithub_local.walker import collect_files

    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("x")
    (tmp_path / "a.txt").write_text("hi")
    files = collect_files(tmp_path, ["*"], [".git"])
    names = {f.path.as_posix() for f in files}
    assert "a.txt" in names
    assert not any(n.startswith(".git/") for n in names)


def test_collect_files_trailing_slash(tmp_path):
    from uithub_local.walker import collect_files

    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "a.txt").write_text("x")
    (tmp_path / "b.txt").write_text("y")

    names = {f.path.as_posix() for f in collect_files(tmp_path, ["*"], ["tests/"])}
    assert "b.txt" in names
    assert not any(n.startswith("tests/") for n in names)


def test_collect_files_trailing_backslash(tmp_path):
    from uithub_local.walker import collect_files

    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "a.txt").write_text("x")
    (tmp_path / "b.txt").write_text("y")

    names = {f.path.as_posix() for f in collect_files(tmp_path, ["*"], ["tests\\"])}
    assert "b.txt" in names
    assert not any(n.startswith("tests/") for n in names)

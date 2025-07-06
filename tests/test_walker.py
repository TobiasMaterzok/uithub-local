def test_collect_files_exclude_binary(tmp_path):
    from uithub_local.walker import collect_files

    (tmp_path / "bin").write_bytes(b"\0\1")
    (tmp_path / "a.txt").write_text("hi")
    files = collect_files(tmp_path, ["*"], [])
    assert len(files) == 1
    assert files[0].path.name == "a.txt"

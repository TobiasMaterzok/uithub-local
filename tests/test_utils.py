def test_is_binary_path(tmp_path):
    from uithub_local.utils import is_binary_path

    text = tmp_path / "a.txt"
    text.write_text("hello")
    binary = tmp_path / "b.bin"
    binary.write_bytes(b"\0\1")
    assert not is_binary_path(text)
    assert is_binary_path(binary)

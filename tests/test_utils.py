def test_is_binary_path(tmp_path):
    from uithub_local.utils import is_binary_path

    text = tmp_path / "a.txt"
    text.write_text("hello")
    binary = tmp_path / "b.bin"
    binary.write_bytes(b"\0\1")
    assert not is_binary_path(text)
    assert is_binary_path(binary)


def test_is_binary_path_high_ascii(tmp_path):
    from uithub_local.utils import is_binary_path

    noisy = tmp_path / "noise.txt"
    noisy.write_bytes(b"\x80" * 40 + b"a" * 10)
    assert is_binary_path(noisy)
    assert not is_binary_path(noisy, strict=False)

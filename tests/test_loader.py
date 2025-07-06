def test_load_text_skip_large(tmp_path):
    from uithub_local.loader import load_text, MAX_SIZE

    p = tmp_path / "big.txt"
    p.write_bytes(b"a" * (MAX_SIZE + 1))
    import pytest

    with pytest.raises(ValueError):
        load_text(p)


def test_load_text_success(tmp_path):
    from uithub_local.loader import load_text

    p = tmp_path / "a.txt"
    p.write_text("hi")
    assert load_text(p) == "hi"

def test_load_text_success(tmp_path):
    from uithub_local.loader import load_text

    p = tmp_path / "a.txt"
    p.write_text("hi")
    assert load_text(p) == "hi"

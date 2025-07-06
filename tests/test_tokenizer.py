from pathlib import Path

from uithub_local.tokenizer import approximate_tokens, total_tokens


def test_approximate_tokens():
    assert approximate_tokens("abcd") >= 1


def test_total_tokens(tmp_path: Path):
    p = tmp_path / "a.txt"
    p.write_text("hello")
    assert total_tokens([p]) >= 1

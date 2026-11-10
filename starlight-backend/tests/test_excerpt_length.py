import pytest
from utils import make_excerpt


def test_make_excerpt_rejects_non_positive_length() -> None:
    html = "<p>hello world there</p>"
    with pytest.raises(ValueError, match="positive integer"):
        make_excerpt(html, 0)
    with pytest.raises(ValueError, match="positive integer"):
        make_excerpt(html, -5)
    assert make_excerpt(html) == "hello world there"

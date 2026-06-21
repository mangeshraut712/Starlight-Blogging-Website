"""Backend security and sanitization tests."""
import pytest
from sanitize import sanitize_html


def test_sanitize_strips_script_tags():
    dirty = '<p>Hello</p><script>alert("xss")</script>'
    clean = sanitize_html(dirty)
    assert '<script>' not in clean
    assert 'Hello' in clean


def test_sanitize_allows_basic_formatting():
    html = '<p><strong>Bold</strong> text</p>'
    clean = sanitize_html(html)
    assert '<strong>Bold</strong>' in clean

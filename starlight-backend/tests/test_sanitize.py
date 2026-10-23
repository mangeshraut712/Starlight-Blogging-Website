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


def test_sanitize_strips_javascript_urls_and_handlers():
    dirty = '<a href="javascript:alert(1)" onclick="alert(1)">x</a><img src="javascript:alert(1)" onerror="alert(1)">'
    clean = sanitize_html(dirty).lower()
    assert 'javascript:' not in clean
    assert 'onclick' not in clean
    assert 'onerror' not in clean


def test_sanitize_adds_noopener_to_links():
    clean = sanitize_html('<a href="https://example.com" target="_blank">x</a>')
    assert 'noopener' in clean
    assert 'noreferrer' in clean
    assert 'https://example.com' in clean

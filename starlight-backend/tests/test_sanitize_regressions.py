"""Regression tests for plain-text entities and quoted '>' in anchor attributes."""
from html.parser import HTMLParser

from sanitize import sanitize_html, strip_html


def test_strip_html_returns_plain_text_not_entities():
    assert strip_html('Tom & Jerry') == 'Tom & Jerry'
    assert strip_html('5 < 10 is true') == '5 < 10 is true'


def test_strip_html_still_removes_markup():
    assert strip_html('<b>hi</b> <script>alert(1)</script>there') == 'hi there'


def test_anchor_with_gt_inside_attribute_keeps_rel_in_place():
    out = sanitize_html('<a href="https://example.com" title="a > b">x</a>')
    anchors = []

    class Collect(HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag == 'a':
                anchors.append(dict(attrs))

    Collect().feed(out)
    assert anchors == [{'href': 'https://example.com', 'title': 'a > b', 'rel': 'noopener noreferrer'}], out

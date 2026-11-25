import html
import re

import bleach
from bleach import html5lib_shim
from bleach.sanitizer import Cleaner

ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'b', 'i',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'a', 'img', 'blockquote', 'pre', 'code', 'span', 'div',
]
ALLOWED_ATTRS = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title'],
    '*': ['class'],
}
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']

_DROP_BLOCKS = re.compile(r'<(script|style)\b[^>]*>.*?</\1\s*>', re.IGNORECASE | re.DOTALL)
_DROP_UNCLOSED = re.compile(r'<(script|style)\b[^>]*>.*', re.IGNORECASE | re.DOTALL)


def _drop_active_content(value: str) -> str:
    """Remove script and style elements, including their text."""
    without = _DROP_BLOCKS.sub('', value or '')
    return _DROP_UNCLOSED.sub('', without)


class _AnchorRelFilter(html5lib_shim.Filter):
    """Add rel="noopener noreferrer" to every <a> in bleach's token stream."""

    def __iter__(self):
        for token in super().__iter__():
            if token['type'] in ('StartTag', 'EmptyTag') and token['name'] == 'a':
                attrs = dict(token['data'])
                tokens = attrs.get((None, 'rel'), '').split()
                for value in ('noopener', 'noreferrer'):
                    if value not in tokens:
                        tokens.append(value)
                attrs[(None, 'rel')] = ' '.join(tokens)
                token['data'] = attrs
            yield token


_CLEANER = Cleaner(
    tags=ALLOWED_TAGS,
    attributes=ALLOWED_ATTRS,
    protocols=ALLOWED_PROTOCOLS,
    strip=True,
    filters=[_AnchorRelFilter],
)


def sanitize_html(html: str) -> str:
    if not html:
        return ''
    return _CLEANER.clean(_drop_active_content(html))


def strip_html(value: str) -> str:
    """Reduce untrusted text (comments, names) to plain text."""
    if not value:
        return ''
    text = bleach.clean(
        _drop_active_content(value),
        tags=[],
        attributes={},
        protocols=[],
        strip=True,
    )
    # bleach returns serialized HTML; decode entities so callers get plain text.
    return re.sub(r'\s+', ' ', html.unescape(text)).strip()

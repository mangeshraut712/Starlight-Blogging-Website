import re

import bleach

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

_ANCHOR_RE = re.compile(r'<a\b[^>]*>', re.IGNORECASE)
_REL_RE = re.compile(r'\brel\s*=\s*(["\'])(.*?)\1', re.IGNORECASE)
_DROP_BLOCKS = re.compile(r'<(script|style)\b[^>]*>.*?</\1\s*>', re.IGNORECASE | re.DOTALL)
_DROP_UNCLOSED = re.compile(r'<(script|style)\b[^>]*>.*', re.IGNORECASE | re.DOTALL)


def _drop_active_content(value: str) -> str:
    """Remove script and style elements, including their text."""
    without = _DROP_BLOCKS.sub('', value or '')
    return _DROP_UNCLOSED.sub('', without)


def _ensure_anchor_rel(clean_html: str) -> str:
    def fix(match: re.Match) -> str:
        tag = match.group(0)
        rel_match = _REL_RE.search(tag)
        if not rel_match:
            return tag[:-1] + ' rel="noopener noreferrer">'
        tokens = rel_match.group(2).split()
        for token in ('noopener', 'noreferrer'):
            if token not in tokens:
                tokens.append(token)
        quote = rel_match.group(1)
        replacement = f'rel={quote}{" ".join(tokens)}{quote}'
        return tag[:rel_match.start()] + replacement + tag[rel_match.end():]

    return _ANCHOR_RE.sub(fix, clean_html)


def sanitize_html(html: str) -> str:
    if not html:
        return ''
    cleaned = bleach.clean(
        _drop_active_content(html),
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
    return _ensure_anchor_rel(cleaned)


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
    return re.sub(r'\s+', ' ', text).strip()

import html
import re
import unicodedata


_INVALID_XML_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def _strip_tags(html_content: str) -> str:
    out = []
    in_tag = False
    for ch in html_content or "":
        if ch == "<":
            in_tag = True
        elif ch == ">":
            in_tag = False
            out.append(" ")
        elif not in_tag:
            out.append(ch)
    return "".join(out)


def slugify(text: str) -> str:
    text = unicodedata.normalize('NFKD', text or '').encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-')


def make_unique_slug(title: str, post_id: int = None) -> str:
    base = (slugify(title) or 'post')[:80]
    if post_id is not None:
        return f"{base}-{post_id}"
    return base


def make_excerpt(html_content: str, length: int = 160) -> str:
    if length <= 0:
        raise ValueError(f"length must be a positive integer, got {length}")
    text = html.unescape(_strip_tags(html_content))
    text = re.sub(r'\s+', ' ', text).strip()
    if length <= 0:
        return ''
    if len(text) <= length:
        return text
    clipped = text[:length]
    if ' ' not in clipped:
        return clipped + '...'
    return clipped.rsplit(' ', 1)[0] + '...'


def make_username(email: str, first: str, last: str, user_id: int = None) -> str:
    base = slugify(f"{first}{last}") or slugify((email or '').split('@')[0]) or 'user'
    if user_id is not None:
        return f"{base}{user_id}"
    return base


def escape_like(value: str) -> str:
    """Escape LIKE wildcards so user input is matched literally."""
    return (
        (value or '')
        .replace('\\', '\\\\')
        .replace('%', '\\%')
        .replace('_', '\\_')
    )


def reading_time_minutes(html_content: str, wpm: int = 200) -> int:
    if wpm <= 0:
        raise ValueError(f"wpm must be a positive integer, got {wpm}")
    text = re.sub(r'\s+', ' ', html.unescape(_strip_tags(html_content or ''))).strip()
    if not text:
        return 1
    words = len(text.split())
    return max(1, (words + wpm - 1) // wpm)


def cdata_safe(value: str) -> str:
    """Keep user text from breaking out of an XML CDATA section and strip invalid XML control characters."""
    cleaned = _INVALID_XML_CHARS.sub("", value or "")
    return cleaned.replace(']]>', ']]]]><![CDATA[>')

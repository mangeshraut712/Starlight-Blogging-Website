import html
import re
import unicodedata


def _strip_tags(html_content: str) -> str:
    out = []
    in_tag = False
    for ch in html_content or "":
        if ch == "<":
            in_tag = True
        elif ch == ">":
            in_tag = False
        elif not in_tag:
            out.append(ch)
    return "".join(out)


def slugify(text: str) -> str:
    text = unicodedata.normalize('NFKD', text or '').encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-') or 'post'


def make_unique_slug(title: str, post_id: int = None) -> str:
    base = slugify(title)[:80]
    if post_id:
        return f"{base}-{post_id}"
    return base


def make_excerpt(html_content: str, length: int = 160) -> str:
    text = html.unescape(_strip_tags(html_content))
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + '...'


def make_username(email: str, first: str, last: str, user_id: int = None) -> str:
    base = slugify(f"{first}{last}") or slugify(email.split('@')[0])
    if user_id:
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


def reading_time_minutes(html_content: str) -> int:
    text = re.sub(r'\s+', ' ', _strip_tags(html_content or '')).strip()
    if not text:
        return 1
    words = len(text.split())
    return max(1, (words + 199) // 200)


def cdata_safe(value: str) -> str:
    """Keep user text from breaking out of an XML CDATA section."""
    return (value or '').replace(']]>', ']]]]><![CDATA[>')

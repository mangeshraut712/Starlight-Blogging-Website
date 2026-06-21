import re
import unicodedata


def slugify(text: str) -> str:
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-') or 'post'


def make_unique_slug(title: str, post_id: int = None) -> str:
    base = slugify(title)[:80]
    if post_id:
        return f"{base}-{post_id}"
    return base


def make_excerpt(html_content: str, length: int = 160) -> str:
    text = re.sub(r'<[^>]+>', '', html_content or '')
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + '...'


def make_username(email: str, first: str, last: str, user_id: int = None) -> str:
    base = slugify(f"{first}{last}") or slugify(email.split('@')[0])
    if user_id:
        return f"{base}{user_id}"
    return base

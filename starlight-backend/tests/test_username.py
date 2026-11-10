from utils import make_unique_slug, make_username, slugify


def test_slugify_returns_empty_string_when_nothing_usable_remains():
    assert slugify("") == ""
    assert slugify("!!!") == ""
    assert slugify("  Hello World!  ") == "hello-world"


def test_make_unique_slug_falls_back_to_post_for_empty_titles():
    assert make_unique_slug("") == "post"
    assert make_unique_slug("!!!", post_id=12) == "post-12"


def test_make_username_uses_email_when_the_display_name_does_not_slugify():
    assert make_username("ada@example.com", "", "") == "ada"
    assert make_username("ada@example.com", "!!!", "") == "ada"
    assert make_username("ada@example.com", "Ada", "Lovelace") == "adalovelace"
    assert make_username("ada@example.com", "", "", user_id=7) == "ada7"


def test_make_username_falls_back_to_user_when_email_is_also_empty():
    assert make_username("", "", "") == "user"
    assert make_username("", "!!!", "", user_id=3) == "user3"

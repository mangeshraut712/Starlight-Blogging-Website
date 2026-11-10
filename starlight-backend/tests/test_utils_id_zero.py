from utils import make_unique_slug, make_username


def test_zero_ids_are_kept_as_suffixes() -> None:
    assert make_unique_slug("Hello World", 0) == "hello-world-0"
    assert make_unique_slug("Hello World", 1) == "hello-world-1"
    assert make_unique_slug("Hello World") == "hello-world"
    assert make_username("a@b.com", "Jane", "Doe", 0) == "janedoe0"
    assert make_username("a@b.com", "Jane", "Doe", 1) == "janedoe1"
    assert make_username("a@b.com", "Jane", "Doe") == "janedoe"

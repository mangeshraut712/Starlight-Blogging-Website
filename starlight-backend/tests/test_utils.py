from utils import cdata_safe, escape_like, make_excerpt, reading_time_minutes


def test_escape_like_treats_wildcards_as_literal():
    assert escape_like('100%_done') == '100\\%\\_done'
    assert escape_like('a\\b') == 'a\\\\b'


def test_make_excerpt_strips_tags_and_truncates():
    excerpt = make_excerpt('<p>Hello <strong>world</strong></p>', length=20)
    assert '<' not in excerpt
    assert excerpt.startswith('Hello world')


def test_reading_time_uses_word_count():
    words = ' '.join(['word'] * 400)
    assert reading_time_minutes(f'<p>{words}</p>') == 2
    assert reading_time_minutes('') == 1


def test_reading_time_custom_wpm_and_validation():
    words = ' '.join(['word'] * 100)
    assert reading_time_minutes(words, wpm=100) == 1
    assert reading_time_minutes(words, wpm=50) == 2
    assert reading_time_minutes(words, wpm=25) == 4
    assert reading_time_minutes('', wpm=150) == 1

    import pytest
    with pytest.raises(ValueError, match="wpm must be a positive integer"):
        reading_time_minutes(words, wpm=0)
    with pytest.raises(ValueError, match="wpm must be a positive integer"):
        reading_time_minutes(words, wpm=-10)


def test_cdata_safe_breaks_early_terminator():
    assert cdata_safe('end ]]> here') == 'end ]]]]><![CDATA[> here'
    assert cdata_safe('clean\x00null\x0cformfeed\x7fdel') == 'cleannullformfeeddel'


def test_slugify_and_make_unique_slug():
    from utils import make_unique_slug, make_username, slugify
    assert slugify('Hello, World! 123') == 'hello-world-123'
    assert slugify('  Spaced  Out  ') == 'spaced-out'
    assert slugify('Crème Brûlée') == 'creme-brulee'
    assert slugify(None) == ''

    assert make_unique_slug('My First Post', 42) == 'my-first-post-42'
    assert make_unique_slug('', 42) == 'post-42'
    assert make_unique_slug('No ID') == 'no-id'

    assert make_username('ada@lovelace.org', 'Ada', 'Lovelace', 1) == 'adalovelace1'
    assert make_username('anonymous@domain.test', '', '', 99) == 'anonymous99'


def test_make_excerpt_separates_adjacent_block_tags():
    assert make_excerpt('<p>Paragraph one</p><p>Paragraph two</p>') == 'Paragraph one Paragraph two'



def test_make_excerpt_hard_truncates_unbroken_text():
    url = 'https://example.com/' + ('a' * 80)
    excerpt = make_excerpt(url, length=20)
    assert excerpt.endswith('...')
    assert len(excerpt) <= 23
    assert ' ' not in excerpt[:-3]

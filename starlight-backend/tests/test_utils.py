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


def test_cdata_safe_breaks_early_terminator():
    assert cdata_safe('end ]]> here') == 'end ]]]]><![CDATA[> here'

"""Regression tests for quoted '>' in anchors and comment edit round trips."""
from html.parser import HTMLParser

from sanitize import sanitize_html, strip_html

_GOOD = 'phrase-one-ok'


def _register(client, email='ada@example.com', phrase=_GOOD, first='Ada', last='Lovelace'):
    return client.post('/api/register', json={
        'email': email,
        'password': phrase,
        'first': first,
        'last': last,
    })


def _create_post(client, title='A real story', content='<p>Hello readers</p>', label='Fiction', status='published'):
    return client.post('/api/new-post', json={
        'title': title,
        'content': content,
        'label': label,
        'status': status,
    })


def test_strip_html_still_removes_markup():
    assert strip_html('<b>hi</b> <script>alert(1)</script>there') == 'hi there'


def test_strip_html_keeps_encoded_formatting_example_on_re_edit():
    # Legacy storage keeps already-escaped tag examples encoded. The comment
    # editor sends that stored body back, so a re-edit must not treat the
    # example as markup and drop it. (Decoding for display is a separate
    # product decision; see the follow-up issue.)
    original = 'Use &lt;strong&gt; for emphasis.'
    stored = strip_html(original)
    assert stored == 'Use &lt;strong&gt; for emphasis.'
    reedited = strip_html(stored + ' Thanks!')
    assert reedited == 'Use &lt;strong&gt; for emphasis. Thanks!'


def test_anchor_with_gt_inside_attribute_keeps_rel_in_place():
    out = sanitize_html('<a href="https://example.com" title="a > b">x</a>')
    anchors = []

    class Collect(HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag == 'a':
                anchors.append(dict(attrs))

    Collect().feed(out)
    assert anchors == [{'href': 'https://example.com', 'title': 'a > b', 'rel': 'noopener noreferrer'}], out


def test_comment_create_return_re_edit_keeps_encoded_formatting_example(client):
    _register(client)
    post_id = _create_post(client).get_json()['post']['id']
    created = client.post(
        f'/api/posts/{post_id}/comments',
        json={'body': 'Use &lt;strong&gt; for emphasis.'},
    )
    assert created.status_code == 200
    body = created.get_json()['body']
    assert body == 'Use &lt;strong&gt; for emphasis.'
    comment_id = created.get_json()['id']

    updated = client.put(
        f'/api/update-comment/{comment_id}',
        json={'body': body + ' Thanks!'},
    )
    assert updated.status_code == 200
    assert updated.get_json()['body'] == 'Use &lt;strong&gt; for emphasis. Thanks!'

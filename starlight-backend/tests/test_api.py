"""Route tests for auth, authorization, validation, and discovery."""
import datetime

from app import app as flask_app
from models import Bookmark, Like, PostModel, db


def _register(client, email='ada@example.com', password='password1', first='Ada', last='Lovelace'):
    return client.post('/api/register', json={
        'email': email,
        'password': password,
        'first': first,
        'last': last,
    })


def _login(client, email='ada@example.com', password='password1'):
    return client.post('/api/login', json={'email': email, 'password': password})


def _create_post(client, title='A real story', content='<p>Hello readers</p>', label='Fiction', status='published'):
    return client.post('/api/new-post', json={
        'title': title,
        'content': content,
        'label': label,
        'status': status,
    })


def test_register_rejects_missing_and_short_passwords(client):
    missing = client.post('/api/register', json={})
    assert missing.status_code == 400
    short = _register(client, password='short')
    assert short.status_code == 400


def test_register_duplicate_email_and_login_session(client):
    created = _register(client)
    assert created.status_code == 200
    assert created.get_json()['uid']
    duplicate = _register(client)
    assert duplicate.status_code == 409

    client.post('/api/logout')
    anonymous = client.get('/api/current_user')
    assert anonymous.status_code == 401

    logged_in = _login(client)
    assert logged_in.status_code == 200
    me = client.get('/api/current_user')
    assert me.status_code == 200
    assert me.get_json()['email'] == 'ada@example.com'


def test_logout_is_post_only(client):
    _register(client)
    rejected = client.get('/api/logout')
    assert rejected.status_code == 405
    assert client.get('/api/current_user').status_code == 200
    assert client.post('/api/logout').status_code == 200
    assert client.get('/api/current_user').status_code == 401


def test_cors_does_not_reflect_arbitrary_origins(client):
    evil = client.options('/api/login', headers={
        'Origin': 'https://evil.example',
        'Access-Control-Request-Method': 'POST',
    })
    assert evil.headers.get('Access-Control-Allow-Origin') != 'https://evil.example'

    local = client.options('/api/login', headers={
        'Origin': 'http://localhost:4200',
        'Access-Control-Request-Method': 'POST',
    })
    assert local.headers.get('Access-Control-Allow-Origin') == 'http://localhost:4200'
    assert local.headers.get('Access-Control-Allow-Credentials') == 'true'


def test_reset_token_cannot_be_reused_and_drops_old_session(client):
    _register(client)
    forgot = client.post('/api/forgot_password', json={'email': 'ada@example.com'})
    token = forgot.get_json()['reset_token']
    first = client.post('/api/reset_password', json={
        'token': token,
        'new_password': 'newpassword1',
        'confirm_password': 'newpassword1',
    })
    assert first.status_code == 200
    reused = client.post('/api/reset_password', json={
        'token': token,
        'new_password': 'newpassword2',
        'confirm_password': 'newpassword2',
    })
    assert reused.status_code == 400
    assert client.get('/api/current_user').status_code == 401
    assert _login(client, password='newpassword1').status_code == 200
    assert _login(client, password='password1').status_code == 401


def test_delete_post_removes_likes_and_bookmarks(client):
    _register(client)
    created = _create_post(client)
    post_id = created.get_json()['post']['id']
    assert client.post(f'/api/posts/{post_id}/like').status_code == 200
    assert client.post(f'/api/posts/{post_id}/bookmark').status_code == 200

    deleted = client.delete(f'/api/delete-post/{post_id}')
    assert deleted.status_code == 200
    assert client.get(f'/api/posts/{post_id}').status_code == 404
    with flask_app.app_context():
        assert Like.query.filter_by(post_id=post_id).count() == 0
        assert Bookmark.query.filter_by(post_id=post_id).count() == 0


def test_like_and_comment_missing_post_are_404(client):
    _register(client)
    assert client.post('/api/posts/999/like').status_code == 404
    missing = client.post('/api/posts/999/comments', json={'body': 'hi'})
    assert missing.status_code == 404


def test_comment_strips_html_and_rejects_empty_or_long_body(client):
    _register(client)
    post_id = _create_post(client).get_json()['post']['id']
    empty = client.post(f'/api/posts/{post_id}/comments', json={'body': '<script>x</script>'})
    assert empty.status_code == 400
    too_long = client.post(f'/api/posts/{post_id}/comments', json={'body': 'a' * 1001})
    assert too_long.status_code == 400
    created = client.post(f'/api/posts/{post_id}/comments', json={'body': '<b>Nice</b> story'})
    assert created.status_code == 200
    assert created.get_json()['body'] == 'Nice story'


def test_cannot_delete_someone_elses_post(client):
    _register(client)
    post_id = _create_post(client).get_json()['post']['id']
    client.post('/api/logout')
    _register(client, email='bea@example.com', first='Bea', last='Miles')
    forbidden = client.delete(f'/api/delete-post/{post_id}')
    assert forbidden.status_code == 403


def test_drafts_are_hidden_from_other_readers(client):
    _register(client)
    created = _create_post(client, title='Secret draft', status='draft')
    slug = created.get_json()['post']['slug']
    client.post('/api/logout')
    assert client.get(f'/api/posts/slug/{slug}').status_code == 404
    listed = client.get('/api/posts')
    assert all(item['slug'] != slug for item in listed.get_json())


def test_explore_sort_oldest_and_most_liked(client):
    _register(client)
    older = _create_post(client, title='Older tale').get_json()['post']
    newer = _create_post(client, title='Newer tale').get_json()['post']
    with flask_app.app_context():
        old_row = db.session.get(PostModel, older['id'])
        new_row = db.session.get(PostModel, newer['id'])
        old_row.created_at = datetime.datetime(2020, 1, 1)
        new_row.created_at = datetime.datetime(2024, 1, 1)
        new_row.likes = 5
        db.session.commit()

    oldest = client.get('/api/posts?page=1&sort=oldest').get_json()['posts']
    assert [post['title'] for post in oldest] == ['Older tale', 'Newer tale']
    liked = client.get('/api/posts?page=1&sort=most_liked').get_json()['posts']
    assert liked[0]['title'] == 'Newer tale'


def test_search_escapes_like_wildcards_and_omits_body(client):
    _register(client)
    _create_post(client, title='100% done', content='<p>percent piece</p>')
    _create_post(client, title='Other story', content='<p>nothing to see</p>')

    wildcard = client.get('/api/search?q=%25').get_json()
    assert wildcard['count'] == 1
    assert wildcard['results'][0]['title'] == '100% done'
    assert 'content' not in wildcard['results'][0]

    everything = client.get('/api/search?q=%').get_json()
    assert everything['count'] == 1


def test_update_excerpt_comes_from_sanitized_html(client):
    _register(client)
    post_id = _create_post(client).get_json()['post']['id']
    updated = client.put(f'/api/update-post/{post_id}', json={
        'title': 'Clean title',
        'content': '<p>Visible</p><script>alert(1)</script>',
    })
    assert updated.status_code == 200
    body = updated.get_json()
    assert '<script>' not in body['content']
    assert 'alert' not in body['excerpt']
    assert 'Visible' in body['excerpt']


def test_rss_escapes_cdata_terminator(client):
    _register(client)
    created = _create_post(client, title='Breakout', content='<p>end ]]> here</p>')
    assert created.status_code == 200
    rss = client.get('/api/feed/rss').get_data(as_text=True)
    assert '<![CDATA[end ]]]]><![CDATA[> here]]>' in rss


def test_trending_rejects_negative_limit(client):
    _register(client)
    _create_post(client, title='Only one')
    payload = client.get('/api/trending?limit=-5')
    assert payload.status_code == 200
    assert len(payload.get_json()) == 1
    stats = client.get('/api/stats').get_json()
    assert stats['posts'] == 1
    assert stats['communities'] == 1


def test_profile_username_rejects_path_characters(client):
    _register(client)
    bad = client.put('/api/update-profile', json={
        'first': 'Ada',
        'last': 'Lovelace',
        'username': '../admin',
    })
    assert bad.status_code == 400

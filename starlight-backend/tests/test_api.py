"""Route tests for auth, authorization, validation, and discovery."""
import datetime

from app import app as flask_app
from models import Bookmark, Follow, Like, PostModel, UserModel, db

_GOOD = 'phrase-one-ok'
_SHORT = 'short'
_UPDATED = 'phrase-three-ok'
_REUSED = 'phrase-four-ok'


def _register(client, email='ada@example.com', phrase=_GOOD, first='Ada', last='Lovelace'):
    return client.post('/api/register', json={
        'email': email,
        'password': phrase,
        'first': first,
        'last': last,
    })


def _login(client, email='ada@example.com', phrase=_GOOD):
    return client.post('/api/login', json={'email': email, 'password': phrase})


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
    short = _register(client, phrase=_SHORT)
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
        'new_password': _UPDATED,
        'confirm_password': _UPDATED,
    })
    assert first.status_code == 200
    reused = client.post('/api/reset_password', json={
        'token': token,
        'new_password': _REUSED,
        'confirm_password': _REUSED,
    })
    assert reused.status_code == 400
    assert client.get('/api/current_user').status_code == 401
    assert _login(client, phrase=_UPDATED).status_code == 200
    assert _login(client, phrase=_GOOD).status_code == 401


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


def test_other_readers_cannot_touch_or_list_a_draft(client):
    _register(client)
    draft = _create_post(client, title='Unpublished notes', status='draft').get_json()['post']
    post_id = draft['id']
    client.post('/api/logout')

    _register(client, email='grace@example.com', first='Grace', last='Hopper')
    assert client.post(f'/api/posts/{post_id}/like').status_code == 404
    assert client.post(f'/api/posts/{post_id}/comments', json={'body': 'nice'}).status_code == 404
    assert client.get(f'/api/posts/{post_id}/comments').status_code == 404
    assert client.get(f'/api/posts/{post_id}/likes').status_code == 404
    assert client.post(f'/api/posts/{post_id}/bookmark').status_code == 404
    with flask_app.app_context():
        assert Like.query.filter_by(post_id=post_id).count() == 0
        db.session.add(Bookmark(user_id=2, post_id=post_id))
        db.session.commit()
    titles = [item['title'] for item in client.get('/api/bookmarks').get_json()]
    assert 'Unpublished notes' not in titles


def test_author_can_still_work_with_their_own_draft(client):
    _register(client)
    draft = _create_post(client, title='My draft', status='draft').get_json()['post']
    post_id = draft['id']
    assert client.post(f'/api/posts/{post_id}/comments', json={'body': 'todo: intro'}).status_code == 200
    assert client.get(f'/api/posts/{post_id}/comments').status_code == 200
    assert client.post(f'/api/posts/{post_id}/bookmark').status_code == 200
    titles = [item['title'] for item in client.get('/api/bookmarks').get_json()]
    assert titles == ['My draft']


def test_author_profile_and_author_posts(client):
    """GET /api/authors/<username> and /api/authors/<username>/posts contracts."""
    reg = _register(client, email='marie@example.com', first='Marie', last='Curie')
    uid = reg.get_json()['uid']

    with flask_app.app_context():
        user = db.session.get(UserModel, uid)
        user.username = 'mariecurie'
        db.session.commit()

    # Create one published post and one draft
    _create_post(client, title='Radioactivity Discoveries', status='published')
    _create_post(client, title='Private Lab Notes', status='draft')

    # Query author profile
    profile = client.get('/api/authors/mariecurie')
    assert profile.status_code == 200
    pdata = profile.get_json()
    assert pdata['first'] == 'Marie'
    assert pdata['last'] == 'Curie'
    assert pdata['post_count'] == 1  # Only published count
    assert pdata['follower_count'] == 0

    # Non-existent author returns 404
    assert client.get('/api/authors/nonexistent_author').status_code == 404

    # Query author posts: must only contain published posts
    posts_res = client.get('/api/authors/mariecurie/posts')
    assert posts_res.status_code == 200
    posts_data = posts_res.get_json()
    assert posts_data['total'] == 1
    assert len(posts_data['posts']) == 1
    assert posts_data['posts'][0]['title'] == 'Radioactivity Discoveries'

    # Non-existent author posts returns 404
    assert client.get('/api/authors/nonexistent_author/posts').status_code == 404


def test_follow_user_workflow_and_guards(client):
    # Unauthenticated follow returns 401
    assert client.post('/api/users/1/follow').status_code == 401
    assert client.delete('/api/users/1/follow').status_code == 401

    # Register user 1
    u1_reg = _register(client, email='user1@example.com', phrase=_GOOD, first='User', last='One')
    u1_id = u1_reg.get_json()['uid']

    # Cannot follow oneself returns 400
    self_follow = client.post(f'/api/users/{u1_id}/follow')
    assert self_follow.status_code == 400
    assert 'Cannot follow yourself' in self_follow.get_json()['error']

    # Follow non-existent user returns 404
    assert client.post('/api/users/999999/follow').status_code == 404

    # Register user 2
    client.post('/api/logout')
    u2_reg = _register(client, email='user2@example.com', phrase=_GOOD, first='User', last='Two')
    u2_id = u2_reg.get_json()['uid']

    # User 2 follows User 1
    res = client.post(f'/api/users/{u1_id}/follow')
    assert res.status_code == 200
    assert res.get_json()['following'] is True

    # Duplicate follow is idempotent
    dup_res = client.post(f'/api/users/{u1_id}/follow')
    assert dup_res.status_code == 200
    assert dup_res.get_json()['following'] is True

    # User 2 unfollows User 1
    unfollow_res = client.delete(f'/api/users/{u1_id}/follow')
    assert unfollow_res.status_code == 200
    assert unfollow_res.get_json()['following'] is False

    # Duplicate unfollow is idempotent
    dup_unfollow = client.delete(f'/api/users/{u1_id}/follow')
    assert dup_unfollow.status_code == 200
    assert dup_unfollow.get_json()['following'] is False


def test_update_profile_workflow_and_guards(client):
    # Unauthenticated request returns 401
    assert client.put('/api/update-profile', json={'first': 'Alice'}).status_code == 401

    # Register initial user
    u1_reg = _register(client, email='profileuser@example.com', phrase=_GOOD, first='Alice', last='Smith')
    u1_username = u1_reg.get_json()['username']

    # Empty first name returns 400
    bad_name = client.put('/api/update-profile', json={'first': '   ', 'last': 'Smith'})
    assert bad_name.status_code == 400
    assert 'First and last name must be 1-100 characters' in bad_name.get_json()['error']

    # Excessively long last name returns 400
    long_last = client.put('/api/update-profile', json={'first': 'Alice', 'last': 'x' * 101})
    assert long_last.status_code == 400
    assert 'First and last name must be 1-100 characters' in long_last.get_json()['error']

    # Bio exceeding MAX_BIO_LENGTH (2000 chars) returns 400
    long_bio = client.put('/api/update-profile', json={'first': 'Alice', 'last': 'Smith', 'bio': 'a' * 2001})
    assert long_bio.status_code == 400
    assert 'Bio is too long' in long_bio.get_json()['error']

    # Password update with short password (< 8 chars) returns 400
    short_pw = client.put('/api/update-profile', json={
        'first': 'Alice',
        'last': 'Smith',
        'password': 'short',
        'old_password': _GOOD,
    })
    assert short_pw.status_code == 400
    assert 'Password must be at least 8 characters' in short_pw.get_json()['error']

    # Password update with wrong current password returns 400
    wrong_pw = client.put('/api/update-profile', json={
        'first': 'Alice',
        'last': 'Smith',
        'password': 'NewPassword123!',
        'old_password': 'WrongPassword!',
    })
    assert wrong_pw.status_code == 400
    assert 'Current password is incorrect' in wrong_pw.get_json()['error']

    # Register second user to test username collision
    client.post('/api/logout')
    _register(client, email='seconduser@example.com', phrase=_GOOD, first='Bob', last='Jones')
    # Try updating Bob's username to Alice's username
    conflict = client.put('/api/update-profile', json={
        'first': 'Bob',
        'last': 'Jones',
        'username': u1_username,
    })
    assert conflict.status_code == 409
    assert 'Username already taken' in conflict.get_json()['error']

    # Successful profile and password update
    new_phrase = 'BrandNewPassword999!'
    ok_res = client.put('/api/update-profile', json={
        'first': 'Robert',
        'last': 'Jones Jr.',
        'bio': 'Software engineer and author.',
        'username': 'bobjonesjr',
        'password': new_phrase,
        'old_password': _GOOD,
    })
    assert ok_res.status_code == 200
    data = ok_res.get_json()
    assert data['message'] == 'Profile updated successfully!'
    assert data['user']['first'] == 'Robert'
    assert data['user']['last'] == 'Jones Jr.'
    assert data['user']['username'] == 'bobjonesjr'
    assert data['user']['bio'] == 'Software engineer and author.'

    # Re-login with old password fails
    client.post('/api/logout')
    login_old = _login(client, email='seconduser@example.com', phrase=_GOOD)
    assert login_old.status_code == 401

    # Re-login with new password succeeds
    login_ok = _login(client, email='seconduser@example.com', phrase=new_phrase)
    assert login_ok.status_code == 200


def test_bookmark_workflow_and_guards(client):
    # Unauthenticated requests return 401
    assert client.get('/api/bookmarks').status_code == 401
    assert client.post('/api/posts/1/bookmark').status_code == 401
    assert client.delete('/api/posts/1/bookmark').status_code == 401

    # Register user and create published post
    _register(client, email='reader@example.com', first='Reader', last='One')
    post_res = _create_post(client, title='Fascinating Article', status='published')
    post_id = post_res.get_json()['post']['id']

    # Bookmarks list is initially empty
    init_bookmarks = client.get('/api/bookmarks')
    assert init_bookmarks.status_code == 200
    assert len(init_bookmarks.get_json()) == 0

    # Add bookmark via POST
    bm_add = client.post(f'/api/posts/{post_id}/bookmark')
    assert bm_add.status_code == 200
    assert bm_add.get_json()['bookmarked'] is True

    # Duplicate POST is idempotent
    bm_dup = client.post(f'/api/posts/{post_id}/bookmark')
    assert bm_dup.status_code == 200
    assert bm_dup.get_json()['bookmarked'] is True

    # Bookmarks list now contains the post
    bms = client.get('/api/bookmarks')
    assert bms.status_code == 200
    titles = [item['title'] for item in bms.get_json()]
    assert titles == ['Fascinating Article']

    # Remove bookmark via DELETE
    bm_del = client.delete(f'/api/posts/{post_id}/bookmark')
    assert bm_del.status_code == 200
    assert bm_del.get_json()['bookmarked'] is False

    # Duplicate DELETE is idempotent
    bm_del_dup = client.delete(f'/api/posts/{post_id}/bookmark')
    assert bm_del_dup.status_code == 200
    assert bm_del_dup.get_json()['bookmarked'] is False

    # Bookmarks list is empty again
    empty_bms = client.get('/api/bookmarks')
    assert empty_bms.status_code == 200
    assert len(empty_bms.get_json()) == 0

    # Non-existent post returns 404
    assert client.post('/api/posts/999999/bookmark').status_code == 404
    assert client.delete('/api/posts/999999/bookmark').status_code == 404


def test_post_like_toggle_and_get_likes(client):
    # Unauthenticated like returns 401
    assert client.post('/api/posts/1/like').status_code == 401

    # Register and create post
    _register(client, 'author_like@example.com', _GOOD)
    _login(client, 'author_like@example.com', _GOOD)
    res = _create_post(client, title='Liking Demo', content='<p>Likes test</p>')
    assert res.status_code == 200
    post_id = res.get_json()['post']['id']

    # Initial like returns 'liked'
    like_res1 = client.post(f'/api/posts/{post_id}/like')
    assert like_res1.status_code == 200
    assert like_res1.get_json()['success'] == 'liked'

    # Check post likes count
    p1 = client.get(f'/api/posts/{post_id}').get_json()
    assert p1['likes'] == 1

    # Likes endpoint lists 1 like
    likes_data = client.get(f'/api/posts/{post_id}/likes')
    assert likes_data.status_code == 200
    assert len(likes_data.get_json()) == 1

    # Toggling like again unlikes it
    like_res2 = client.post(f'/api/posts/{post_id}/like')
    assert like_res2.status_code == 200
    assert like_res2.get_json()['success'] == 'unliked'

    p2 = client.get(f'/api/posts/{post_id}').get_json()
    assert p2['likes'] == 0

    # Likes endpoint is empty now
    assert len(client.get(f'/api/posts/{post_id}/likes').get_json()) == 0

    # Non-existent post returns 404
    assert client.post('/api/posts/999999/like').status_code == 404
    assert client.get('/api/posts/999999/likes').status_code == 404


def test_platform_stats_and_trending(client):
    # Stats before post creation
    stats_initial = client.get('/api/stats')
    assert stats_initial.status_code == 200
    data0 = stats_initial.get_json()
    assert 'writers' in data0
    assert 'posts' in data0
    assert 'communities' in data0
    assert 'comments' in data0
    assert 'total_likes' in data0

    # Create user and published posts
    _register(client, 'stats_author@example.com', _GOOD)
    _login(client, 'stats_author@example.com', _GOOD)
    _create_post(client, title='Trending Post 1', content='<p>Post 1</p>', label='AI')
    _create_post(client, title='Trending Post 2', content='<p>Post 2</p>', label='Design')

    stats_after = client.get('/api/stats').get_json()
    assert stats_after['posts'] >= 2
    assert stats_after['communities'] >= 2

    # Trending posts returns array with limit bounds
    trending = client.get('/api/trending?limit=5')
    assert trending.status_code == 200
    items = trending.get_json()
    assert isinstance(items, list)
    assert len(items) <= 5
    assert len(items) >= 2

    # Negative or non-integer limit clamps safely
    trending_clamped = client.get('/api/trending?limit=-10')
    assert trending_clamped.status_code == 200
    assert len(trending_clamped.get_json()) >= 1


def test_comments_crud_authorization_and_sanitization(client):
    # Register author and create post
    _register(client, 'comm_author1@example.com', _GOOD)
    _login(client, 'comm_author1@example.com', _GOOD)
    res = _create_post(client, title='Discussion Topic', content='<p>Let us talk</p>')
    assert res.status_code == 200
    post_id = res.get_json()['post']['id']

    # Logout to test unauthenticated comment submission on existing post
    client.post('/api/logout')
    assert client.post(f'/api/posts/{post_id}/comments', json={'body': 'Nice'}).status_code == 401

    # Login back
    _login(client, 'comm_author1@example.com', _GOOD)

    # Non-existent post returns 404
    assert client.post('/api/posts/999999/comments', json={'body': 'Hello'}).status_code == 404
    assert client.get('/api/posts/999999/comments').status_code == 404

    # Empty comment body returns 400
    assert client.post(f'/api/posts/{post_id}/comments', json={'body': ''}).status_code == 400
    assert client.post(f'/api/posts/{post_id}/comments', json={'body': '   <p></p>  '}).status_code == 400

    # Valid comment with HTML strips HTML
    created = client.post(
        f'/api/posts/{post_id}/comments',
        json={'body': '<b>Bold comment</b> and normal text'}
    )
    assert created.status_code == 200
    comm_data = created.get_json()
    assert '<b>' not in comm_data['body']
    assert 'Bold comment and normal text' in comm_data['body']
    comment_id = comm_data['id']

    # GET comments lists the created comment
    listing = client.get(f'/api/posts/{post_id}/comments')
    assert listing.status_code == 200
    assert len(listing.get_json()) == 1

    # Register user 2 and attempt unauthorized update and delete
    _register(client, 'comm_user2@example.com', _GOOD)
    _login(client, 'comm_user2@example.com', _GOOD)
    unauth_edit = client.put(f'/api/update-comment/{comment_id}', json={'body': 'Hacked body'})
    assert unauth_edit.status_code == 403
    unauth_del = client.delete(f'/api/delete-comment/{comment_id}')
    assert unauth_del.status_code == 403

    # Log back in as user 1 and update comment
    _login(client, 'comm_author1@example.com', _GOOD)
    updated = client.put(f'/api/update-comment/{comment_id}', json={'body': 'Updated my thought'})
    assert updated.status_code == 200
    assert updated.get_json()['body'] == 'Updated my thought'

    # Delete comment
    del_res = client.delete(f'/api/delete-comment/{comment_id}')
    assert del_res.status_code == 200

    # Comments list is empty again
    assert len(client.get(f'/api/posts/{post_id}/comments').get_json()) == 0

    # Deleting or updating non-existent comment returns 404
    assert client.delete(f'/api/delete-comment/{comment_id}').status_code == 404
    assert client.put(f'/api/update-comment/{comment_id}', json={'body': 'Test'}).status_code == 404


def test_search_posts_queries_and_filters(client):
    """Verify search endpoint contracts: validation, query matching, and label filtering."""
    # Both missing returns 400
    assert client.get('/api/search').status_code == 400
    assert client.get('/api/search?q=   &label=  ').status_code == 400

    # Overlong query returns 400
    long_query = 'a' * 201
    assert client.get(f'/api/search?q={long_query}').status_code == 400

    # Register author and create sample posts
    _register(client, 'search_author@example.com', _GOOD, first='Search', last='Expert')
    _login(client, 'search_author@example.com', _GOOD)
    _create_post(
        client,
        title='Quantum Computing Breakthrough',
        content='<p>Superposition and entanglement details</p>',
        label='Technology',
        status='published'
    )
    _create_post(
        client,
        title='Culinary Wonders of Tokyo',
        content='<p>Ramen and sushi exploration</p>',
        label='Food',
        status='published'
    )
    # Draft post should never appear in search results
    _create_post(
        client,
        title='Secret Quantum Project',
        content='<p>Unpublished notes</p>',
        label='Technology',
        status='draft'
    )

    # Search by keyword
    search_res = client.get('/api/search?q=Quantum')
    assert search_res.status_code == 200
    data = search_res.get_json()
    assert data['count'] == 1
    assert data['results'][0]['title'] == 'Quantum Computing Breakthrough'

    # Search by label filter
    label_res = client.get('/api/search?label=Food')
    assert label_res.status_code == 200
    food_data = label_res.get_json()
    assert food_data['count'] == 1
    assert food_data['results'][0]['title'] == 'Culinary Wonders of Tokyo'

    # Filter with both query and label
    combined_res = client.get('/api/search?q=Tokyo&label=Food')
    assert combined_res.status_code == 200
    assert combined_res.get_json()['count'] == 1

    # Mismatched combination returns empty list
    mismatch_res = client.get('/api/search?q=Quantum&label=Food')
    assert mismatch_res.status_code == 200
    assert mismatch_res.get_json()['count'] == 0


def test_rss_feed_generation(client):
    """Verify RSS 2.0 XML generation, content-type, and post inclusion."""
    _register(client, 'rss_author@example.com', _GOOD, first='RSS', last='Writer')
    _login(client, 'rss_author@example.com', _GOOD)
    _create_post(
        client,
        title='First RSS Story',
        content='<p>Exciting news for RSS subscribers</p>',
        label='News',
        status='published'
    )

    response = client.get('/api/feed/rss')
    assert response.status_code == 200
    assert response.headers['Content-Type'].startswith('application/rss+xml')
    body = response.data.decode('utf-8')
    assert '<?xml version="1.0" encoding="UTF-8"?>' in body
    assert '<rss version="2.0">' in body
    assert '<title>StarLight Blog</title>' in body
    assert '<title>First RSS Story</title>' in body
    assert '<description><![CDATA[' in body
    assert 'Exciting news for RSS subscribers' in body


def test_follow_user_contracts_and_lifecycle(client):
    """Verify follow and unfollow contracts: authorization, self-follow guard, and lifecycle."""
    # Anonymous follow and unfollow are rejected with 401
    assert client.post('/api/users/1/follow').status_code == 401
    assert client.delete('/api/users/1/follow').status_code == 401

    # Register user 1 and log in
    u1_res = _register(client, 'follow_u1@example.com', _GOOD, first='Follower', last='One')
    assert u1_res.status_code == 200
    u1_id = u1_res.get_json()['uid']
    _login(client, 'follow_u1@example.com', _GOOD)

    # Self-follow guard returns 400
    self_res = client.post(f'/api/users/{u1_id}/follow')
    assert self_res.status_code == 400
    assert self_res.get_json() == {'error': 'Cannot follow yourself'}

    # Target user not found returns 404
    missing_res = client.post('/api/users/99999/follow')
    assert missing_res.status_code == 404
    assert missing_res.get_json() == {'error': 'User not found'}

    # Register target user 2
    u2_res = _register(client, 'follow_u2@example.com', _GOOD, first='Followed', last='Two')
    assert u2_res.status_code == 200
    u2_id = u2_res.get_json()['uid']

    # Log back in as user 1 to follow user 2
    _login(client, 'follow_u1@example.com', _GOOD)
    follow_res = client.post(f'/api/users/{u2_id}/follow')
    assert follow_res.status_code == 200
    assert follow_res.get_json() == {'following': True}

    with flask_app.app_context():
        assert Follow.query.filter_by(follower_id=u1_id, following_id=u2_id).count() == 1

    # Repeat follow is idempotent
    repeat_res = client.post(f'/api/users/{u2_id}/follow')
    assert repeat_res.status_code == 200
    assert repeat_res.get_json() == {'following': True}
    with flask_app.app_context():
        assert Follow.query.filter_by(follower_id=u1_id, following_id=u2_id).count() == 1

    # Unfollow returns following: False
    unfollow_res = client.delete(f'/api/users/{u2_id}/follow')
    assert unfollow_res.status_code == 200
    assert unfollow_res.get_json() == {'following': False}

    with flask_app.app_context():
        assert Follow.query.filter_by(follower_id=u1_id, following_id=u2_id).count() == 0

    # Repeat unfollow is idempotent
    repeat_unfollow = client.delete(f'/api/users/{u2_id}/follow')
    assert repeat_unfollow.status_code == 200
    assert repeat_unfollow.get_json() == {'following': False}








def test_root_health_auth_state_and_users_routes(client, monkeypatch):
    """Verify root, health (200 and 503), /api/data, /api/current_user, and /api/users endpoints."""
    root_res = client.get('/')
    assert root_res.status_code == 200
    assert root_res.get_json()['status'] == 'Running'

    health_ok = client.get('/api/health')
    assert health_ok.status_code == 200
    assert health_ok.get_json()['status'] == 'healthy'
    assert health_ok.get_json()['database'] == 'connected'

    # Simulate DB failure on /api/health
    def _boom(*_args, **_kwargs):
        raise RuntimeError('db down')

    monkeypatch.setattr(db.session, 'execute', _boom)
    health_err = client.get('/api/health')
    assert health_err.status_code == 503
    assert health_err.get_json()['status'] == 'unhealthy'
    monkeypatch.undo()

    # Anonymous auth state checks
    assert client.get('/api/data').status_code == 404
    assert client.get('/api/current_user').status_code == 401
    assert client.get('/api/users').status_code == 401
    assert client.get('/api/users/99999').status_code == 404

    reg = _register(client, 'directory@example.com', _GOOD, first='Dir', last='User')
    uid = int(reg.get_json()['uid'])

    assert client.get('/api/data').status_code == 200
    me = client.get('/api/current_user')
    assert me.status_code == 200
    assert me.get_json()['email'] == 'directory@example.com'

    users_list = client.get('/api/users')
    assert users_list.status_code == 200
    items = users_list.get_json()
    assert len(items) == 1
    assert 'email' not in items[0]  # public serialization hides email

    by_id = client.get(f'/api/users/{uid}')
    assert by_id.status_code == 200
    assert by_id.get_json()['first'] == 'Dir'
    assert 'email' not in by_id.get_json()


def test_pagination_zero_and_sorting_modes(client):
    """Verify ?page=0 clamps to page 1 paginated response and all sort modes succeed."""
    _register(client, 'pager@example.com', _GOOD, first='Page', last='Author')
    p1 = _create_post(client, title='Zeta Post', content='<p>Body one</p>', label='Tech').get_json()['post']
    p2 = _create_post(client, title='Alpha Post', content='<p>Body two</p>', label='Tech').get_json()['post']
    client.post(f"/api/posts/{p2['id']}/like")

    page_zero = client.get('/api/posts?page=0&per_page=1')
    assert page_zero.status_code == 200
    payload = page_zero.get_json()
    assert isinstance(payload, dict)
    assert payload['page'] == 1
    assert payload['per_page'] == 1
    assert payload['total'] == 2
    assert payload['has_more'] is True

    alpha = client.get('/api/posts?sort=alphabetical').get_json()
    assert [item['title'] for item in alpha] == ['Alpha Post', 'Zeta Post']

    least = client.get('/api/posts?sort=least_liked').get_json()
    assert least[0]['id'] == p1['id']

    trending = client.get('/api/posts?sort=trending').get_json()
    assert trending[0]['id'] == p2['id']


def test_update_post_status_label_and_slug_contracts(client):
    """Verify update_post supports publishing drafts, updating labels, and rejecting invalid inputs."""
    assert client.put('/api/update-post/1', json={'title': 'T', 'content': 'C'}).status_code == 401

    _register(client, 'editor@example.com', _GOOD, first='Edit', last='Owner')
    draft = _create_post(
        client, title='Initial Draft', content='<p>Draft text</p>', label='Notes', status='draft'
    ).get_json()['post']

    # Invalid status and label rejected with 400
    bad_status = client.put(
        f"/api/update-post/{draft['id']}",
        json={'title': 'Valid', 'content': '<p>Valid</p>', 'status': 'archived'},
    )
    assert bad_status.status_code == 400

    bad_label = client.put(
        f"/api/update-post/{draft['id']}",
        json={'title': 'Valid', 'content': '<p>Valid</p>', 'label': '   '},
    )
    assert bad_label.status_code == 400

    # Publish draft and update community label + regenerate slug
    published_res = client.put(
        f"/api/update-post/{draft['id']}",
        json={
            'title': 'Published Launch Post',
            'content': '<p>Ready for everyone</p>',
            'status': 'published',
            'label': 'Announcements',
        },
    )
    assert published_res.status_code == 200
    updated = published_res.get_json()
    assert updated['status'] == 'published'
    assert updated['label'] == 'Announcements'
    assert updated['slug'].startswith('published-launch-post')

    # Slug lookup increments view_count and populates reader flags
    _register(client, 'reader2@example.com', _GOOD, first='Read', last='Two')
    client.post(f"/api/posts/{draft['id']}/bookmark")
    client.post(f"/api/posts/{draft['id']}/like")
    client.post(f"/api/users/{draft['author_id']}/follow")

    slug_res = client.get(f"/api/posts/slug/{updated['slug']}")
    assert slug_res.status_code == 200
    slug_data = slug_res.get_json()
    assert slug_data['view_count'] >= 1
    assert slug_data['is_bookmarked'] is True
    assert slug_data['is_liked'] is True
    assert slug_data['is_following_author'] is True

    # Non-owner cannot edit
    forbidden = client.put(
        f"/api/update-post/{draft['id']}",
        json={'title': 'Hijack', 'content': '<p>No</p>'},
    )
    assert forbidden.status_code == 403


def test_password_reset_validation_and_enumeration_safety(client):
    """Verify forgot_password and reset_password validation guards."""
    assert client.post('/api/forgot_password', json={}).status_code == 400

    # Unknown email returns generic 200 without leaking a reset_token
    unknown = client.post('/api/forgot_password', json={'email': 'nobody@example.com'})
    assert unknown.status_code == 200
    assert 'reset_token' not in unknown.get_json()

    _register(client, 'resetme@example.com', _GOOD, first='Reset', last='Me')
    forgot = client.post('/api/forgot_password', json={'email': 'resetme@example.com'})
    token = forgot.get_json()['reset_token']

    # Validation failures on reset_password
    assert client.post('/api/reset_password', json={}).status_code == 400
    assert client.post(
        '/api/reset_password',
        json={'token': token, 'new_password': _SHORT, 'confirm_password': _SHORT},
    ).status_code == 400
    assert client.post(
        '/api/reset_password',
        json={'token': token, 'new_password': _UPDATED, 'confirm_password': 'different-password'},
    ).status_code == 400
    assert client.post(
        '/api/reset_password',
        json={'token': 'tampered-invalid-token', 'new_password': _UPDATED, 'confirm_password': _UPDATED},
    ).status_code == 400

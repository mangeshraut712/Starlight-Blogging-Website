from app import app as flask_app
from models import Bookmark, Comment, Follow, Like, PostModel, UserModel, db, load_user


def test_user_model_password_and_serialization(client):
    with flask_app.app_context():
        user = UserModel(
            email='ada@example.test',
            username='adalovelace',
            first='Ada',
            last='Lovelace',
            bio='Analytical Engine programmer',
            avatar_url='https://example.test/ada.png',
        )
        user.set_password('Secret123!')
        db.session.add(user)
        db.session.commit()

        assert user.check_password('Secret123!') is True
        assert user.check_password('WrongPass') is False
        assert user.get_full_name() == 'Ada Lovelace'
        assert user.get_id() == user.id

        private_data = user.serialize(public=False)
        assert private_data['email'] == 'ada@example.test'
        assert private_data['username'] == 'adalovelace'
        assert private_data['first'] == 'Ada'

        public_data = user.serialize(public=True)
        assert 'email' not in public_data
        assert public_data['username'] == 'adalovelace'
        assert public_data['first'] == 'Ada'


def test_load_user_helper(client):
    with flask_app.app_context():
        user = UserModel(
            email='grace@example.test',
            username='gracehopper',
            first='Grace',
            last='Hopper',
            password_hash='hash123',
        )
        db.session.add(user)
        db.session.commit()

        assert load_user(user.id) == user
        assert load_user(str(user.id)) == user
        assert load_user(None) is None
        assert load_user('invalid-id') is None
        assert load_user(999999) is None


def test_post_model_serialization(client):
    with flask_app.app_context():
        user = UserModel(
            email='margaret@example.test',
            username='mghamilton',
            first='Margaret',
            last='Hamilton',
            password_hash='hash123',
        )
        db.session.add(user)
        db.session.commit()

        post = PostModel(
            title='Apollo Guidance Software',
            slug='apollo-guidance-software',
            content='Detailed explanation of software engineering concepts in aerospace.',
            excerpt='Overview of Apollo guidance.',
            label='Engineering',
            author_id=user.id,
            author_name=user.get_full_name(),
        )
        db.session.add(post)
        db.session.commit()

        full_data = post.serialize(include_content=True)
        assert full_data['title'] == 'Apollo Guidance Software'
        assert full_data['author_username'] == 'mghamilton'
        assert 'content' in full_data
        assert full_data['reading_minutes'] >= 1

        summary_data = post.serialize(include_content=False)
        assert 'content' not in summary_data
        assert summary_data['title'] == 'Apollo Guidance Software'


def test_relationships_and_serialization(client):
    with flask_app.app_context():
        user1 = UserModel(email='u1@example.test', username='u1', first='U', last='One', password_hash='h')
        user2 = UserModel(email='u2@example.test', username='u2', first='U', last='Two', password_hash='h')
        db.session.add_all([user1, user2])
        db.session.commit()

        post = PostModel(title='Post 1', content='Content', label='Tech', author_id=user1.id, author_name='U One')
        db.session.add(post)
        db.session.commit()

        like = Like(post_id=post.id, user_id=user2.id)
        comment = Comment(post_id=post.id, author_id=user2.id, author_name='U Two', body='Great post!')
        bookmark = Bookmark(post_id=post.id, user_id=user2.id)
        follow = Follow(follower_id=user2.id, following_id=user1.id)
        db.session.add_all([like, comment, bookmark, follow])
        db.session.commit()

        assert like.serialize() == {'id': like.id, 'user_id': user2.id, 'post_id': post.id}
        assert comment.serialize()['body'] == 'Great post!'
        assert bookmark.serialize()['user_id'] == user2.id
        assert post.comment_count == 1

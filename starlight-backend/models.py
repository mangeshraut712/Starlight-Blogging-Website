from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager
from datetime import datetime
from sqlalchemy.orm import backref

login = LoginManager()
db = SQLAlchemy()


class UserModel(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=True)
    first = db.Column(db.String(100), nullable=False)
    last = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    password_hash = db.Column(db.String(), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def get_id(self):
        return self.id

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_full_name(self):
        return f"{self.first} {self.last}"

    def serialize(self, public=False):
        data = {
            'id': self.id,
            'username': self.username,
            'first': self.first,
            'last': self.last,
            'bio': self.bio or '',
            'avatar_url': self.avatar_url,
        }
        if not public:
            data['email'] = self.email
        return data


class PostModel(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    slug = db.Column(db.String(200), unique=True, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author_name = db.Column(db.String(255))
    author = db.relationship('UserModel', backref=backref('posts', lazy=True))
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text, nullable=True)
    cover_image = db.Column(db.String(500), nullable=True)
    likes = db.Column(db.Integer, nullable=False, default=0)
    view_count = db.Column(db.Integer, nullable=False, default=0)
    label = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='published')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def serialize(self, include_content=True):
        author_username = self.author.username if self.author else None
        data = {
            'id': self.id,
            'slug': self.slug,
            'title': self.title,
            'author_id': self.author_id,
            'author_name': self.author_name,
            'author_username': author_username,
            'excerpt': self.excerpt,
            'cover_image': self.cover_image,
            'likes': self.likes,
            'view_count': self.view_count or 0,
            'label': self.label,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
        if include_content:
            data['content'] = self.content
        return data


class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='unique_like'),)

    def serialize(self):
        return {'id': self.id, 'user_id': self.user_id, 'post_id': self.post_id}


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    post = db.relationship('PostModel', backref=backref('comments', lazy=True, cascade='all, delete-orphan'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author_name = db.Column(db.String(255), nullable=False)
    author = db.relationship('UserModel', backref=backref('user_comments', lazy=True))
    body = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def serialize(self):
        return {
            'id': self.id,
            'author_id': self.author_id,
            'author_name': self.author_name,
            'post_id': self.post_id,
            'body': self.body,
            'created_at': self.created_at,
        }


class Bookmark(db.Model):
    __tablename__ = 'bookmarks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_bookmark'),)

    def serialize(self):
        return {'id': self.id, 'user_id': self.user_id, 'post_id': self.post_id, 'created_at': self.created_at}


class Follow(db.Model):
    __tablename__ = 'follows'
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('follower_id', 'following_id', name='unique_follow'),)


@login.user_loader
def load_user(id):
    return UserModel.query.get(id)

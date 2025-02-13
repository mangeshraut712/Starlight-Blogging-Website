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
    first = db.Column(db.String(100), nullable=False)
    last = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(), nullable=False)
 
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
     
    def get_id(self):
        return self.id
    

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
    
    def get_full_name(self):
        return f"{self.first} {self.last}"
    
    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'first': self.first,
            'last': self.last,
        }

class PostModel(db.Model):
    __tablename__ = 'posts'
 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author_name = db.Column(db.String(255))
    author = db.relationship('UserModel', backref=backref('users', lazy=True))
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, nullable=False)
    # likes = db.relationship
    label = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
 
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'author_id': self.author_id,
            'author_name': self.author_name,
            'content': self.content,
            'likes': self.likes,
            'label': self.label,
            'created_at': self.created_at,
        }
        
class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'post_id': self.post_id,
        }
    

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    post = db.relationship('PostModel', backref=backref('posts', lazy=True,cascade='all, delete-orphan'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author_name = db.Column(db.String(255), nullable=False)
    author = db.relationship('UserModel', backref=backref('user_author', lazy=True))
    body = db.Column(db.String(500), nullable=False)
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
  

@login.user_loader
def load_user(id):
    return UserModel.query.get(id)
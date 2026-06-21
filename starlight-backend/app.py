# app.py
import os
import datetime
import flask
from dotenv import load_dotenv
from flask import Flask, jsonify, request, session
from flask_cors import CORS, cross_origin
from models import db, login, UserModel, PostModel, Like, Comment
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token
from sqlalchemy import or_

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')

database_url = os.environ.get('DATABASE_URL', 'sqlite:///starlight.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.permanent_session_lifetime = datetime.timedelta(hours=24)
is_production = os.environ.get('FLASK_ENV') == 'production'
if is_production:
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

allowed_origins = os.environ.get('ALLOWED_ORIGINS', '*').split(',')
CORS(app,
     supports_credentials=True,
     origins=allowed_origins,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

db.init_app(app)
migrate = Migrate(app, db, render_as_batch=True)
jwt = JWTManager(app)
login.init_app(app)
# login.login_view = 'login'

# Create tables within app context
with app.app_context():
    db.create_all()

def get_current_user_id():
    return session.get('user_id')

def get_data():
    return request.get_json()

def get_current_user():
    user_id = get_current_user_id()
    user = UserModel.query.filter_by(id=user_id).first()
    return user

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = flask.make_response()
        response.headers.add("Access-Control-Allow-Origin", request.headers.get('Origin', '*'))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        return response

@app.route('/')
def root():
    return jsonify({
        'message': 'Starlight Blogging Backend API',
        'status': 'Running',
        'version': '2.0.0',
        'timestamp': datetime.datetime.now().isoformat(),
        'documentation': 'Available endpoints: /api/health, /api/login, /api/register, /api/posts, /api/search, etc.'
    })


@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'database': 'connected'
    }), 200


@app.route('/api/search', methods=['GET'])
def search_posts():
    query = request.args.get('q', '').strip()
    label = request.args.get('label', '').strip()

    if not query and not label:
        return jsonify({'error': 'Search query or label filter required'}), 400

    posts_query = PostModel.query

    if label:
        posts_query = posts_query.filter_by(label=label)

    if query:
        search_term = f'%{query}%'
        posts_query = posts_query.filter(
            or_(
                PostModel.title.ilike(search_term),
                PostModel.content.ilike(search_term),
                PostModel.author_name.ilike(search_term),
                PostModel.label.ilike(search_term)
            )
        )

    posts = posts_query.all()
    post_list = [post.serialize() for post in posts]
    sorted_posts = sorted(post_list, key=lambda x: x['created_at'], reverse=True)
    return jsonify({
        'results': sorted_posts,
        'count': len(sorted_posts),
        'query': query,
        'label': label
    })

################ AUTHENTICATION ROUTES ###############
@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    data = get_data()
    email = data['email'].lower().strip()
    password = data['password']
    user = UserModel.query.filter_by(email=email).first()
    if user and user.check_password(password):
        session['user_id'] = user.id
        print("user id ...", user.id)
        # login_user(user, force=True)
        # print("user is auth?", current_user.get_id())

        access_token = create_access_token(identity=email)
        uid = str(user.id)
        print("the session id is and user id are : ", uid, user.id)
        return jsonify({'user': user.id, 'uid':uid, 'message': 'Login is successfull', 'token': access_token}), 200
    else:
        return jsonify({'error': 'Invalid email or password.'}), 401


@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register():
    data = get_data()
    email = data['email'].lower().strip()
    password = data['password']
    first = data['first']
    last = data['last']
    user = UserModel.query.filter_by(email=email).first()
    if user:
        return jsonify({'error': 'This email belongs to an already existing user'}), 401
    else:
        new_user = UserModel(email=email, first=first, last=last)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        return jsonify({'message': 'new user registered successfully'}), 200


@app.route('/api/data')
def data():
    if 'user_id' in session:
        return jsonify({'data': 'The user is logged in'})
    else:
        return jsonify({'error': 'Not authorized, user not logged in'}),404


@app.route('/api/logout')
def logout():
    print("the user id", session.get('user_id'))
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'}), 200


@app.route('/api/forgot_password', methods=['POST'])
def forgot_password():
    data = get_data()
    email = data['email'].lower().strip()
    if email is None:
        return jsonify({'error': 'Email is required'}), 400
    
    user = UserModel.query.filter_by(email=email).first()
    if user:
        user_id = user.id
        return jsonify({'user_id': user_id}), 200
    else:
        return jsonify({'error': 'Invalid email address'}), 404
    
    
@app.route('/api/reset_password', methods=['POST'])
def reset_password():
    data = get_data()
    user_id = data['user_id']
    user = UserModel.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({'error': 'User not found based on given id'}), 404
    
    new_password = data['new_password']
    confirm_password = data['confirm_password']

    if new_password != confirm_password:
        return jsonify({'message': 'The passwords do not match.'}), 400
    else:
        user.set_password(new_password)
        db.session.commit()
        return jsonify({'message': 'Password updated successfully'}), 200


################ USER MODEL RELATED ROUTES ###############  
@app.route('/api/current_user')
def get_current_user_info():
    # user_id = request.get_json()['uid']
    # print("user id now", user_id)
    user = get_current_user()
    if user:
        return jsonify(user.serialize())
    else:
        return jsonify({'error': 'Not authorized, user not logged in'})


@app.route('/api/update-profile', methods=['PUT'])
def update_profile():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not authorized'}), 401
    user = UserModel.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    
    data = get_data()
    first = data['first']
    last = data['last']

    # Check if new password has a value
    if 'password' in data:
        password = data['password']
        user.set_password(password)
    else:
        if first == user.first and last == user.last:
            return jsonify({'message': 'Nothing was changed.'})
        
    # Check if first name or last name has been changed
    if first != user.first:
        user.first = first
    if last != user.last:
        user.last = last
        
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully!'})
       
    
@app.route('/api/users', methods=['GET'])
def get_all_users():
    users = UserModel.query.all()
    user_list = [user.serialize() for user in users]
    return jsonify(user_list)
    

@app.route('/api/users/<int:id>', methods=['GET'])
def get_user_by_id(id):
    user = UserModel.query.filter_by(id=id).first()
    if user:
        return jsonify(user.serialize())
    else:
        return jsonify({'error': 'User not found by id', 'message':id}), 404


################ POST MODEL RELATED ROUTES ###############
@app.route('/api/new-post', methods=['POST'])
def create_new_post():
    data = get_data()
    print(f"=== DEBUG: NEW POST REQUEST ===")
    print(f"DEBUG: Received headers: {dict(request.headers)}")
    print(f"DEBUG: Received data: {data}")
    print(f"DEBUG: All session data: {dict(session)}")
    print(f"DEBUG: Session ID: {session.get('_id', 'None')}")

    user_id = get_current_user_id()
    print(f"DEBUG: user_id from get_current_user_id(): {user_id}")

    if not user_id:
        print("DEBUG: No user ID found in session, returning 401")
        return jsonify({'error': 'Not authorized - Please login first'}), 401

    user = UserModel.query.filter_by(id=user_id).first()
    print(f"DEBUG: Found user: {user}")

    if user:
        author_id = user.id
        author_name = user.get_full_name()
        title = data.get('title')
        content = data.get('content')
        likes = 0
        label = data.get('label')

        print(f"DEBUG: Creating post - title: {title}, label: {label}")

        new_post = PostModel(author_id=author_id, author_name=author_name, title=title, content=content, likes=likes, label=label)
        db.session.add(new_post)
        try:
            db.session.commit()
            print(f"DEBUG: Post created successfully with ID: {new_post.id}")
            return jsonify({'message': 'Post was added successfully', 'post': new_post.serialize()}), 200
        except Exception as e:
            db.session.rollback()
            print(f"DEBUG: Failed to commit post: {e}")
            return jsonify({'error': 'Failed to save post to database'}), 500
    else:
        print("DEBUG: User not found in database")
        return jsonify({'error': 'User does not exist to create new post'}), 404
        
            
@app.route('/api/posts', methods=['GET'])
def get_all_posts():
    label = request.args.get('label')
    if label:
        posts = PostModel.query.filter_by(label=label).all()
    else:
        posts = PostModel.query.all()
        
    post_list = [post.serialize() for post in posts]
    sorted_posts = sorted(post_list, key=lambda x: x['created_at'], reverse=True)
    return jsonify(sorted_posts)
    

@app.route('/api/user-posts', methods=['GET'])
def get_user_posts():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not authorized'}), 401
    posts = PostModel.query.filter_by(author_id=user_id)
    post_list = [post.serialize() for post in posts]

    sorted_posts = sorted(post_list, key=lambda x: x['created_at'], reverse=True)
    return jsonify(sorted_posts)


@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post_by_id(post_id):
    post = PostModel.query.filter_by(id=post_id).first()
    if post:
        return jsonify(post.serialize())
    else:
        return jsonify({'error': 'Post not found by post_id', 'message':id}), 404


#liking a post
@app.route('/api/posts/<int:post_id>/like', methods=['POST','OPTIONS'])
def like_post(post_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not authorized'}), 401
    like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
    
    if like:
        # If the user has already liked the post before, remove the like from the database
        db.session.delete(like)
        db.session.commit()
        
        # Decrement the number of likes for that post
        post = PostModel.query.get(post_id)
        post.likes = Like.query.filter_by(post_id=post_id).count()
        db.session.commit()
    
        return jsonify({'success': 'unliked'})
    else:
        # If the user has not liked the post before, add a new like entry to the database
        like = Like(post_id=post_id, user_id=user_id)
        db.session.add(like)
        db.session.commit()
        
        # Increment the number of likes for that post
        post = PostModel.query.get(post_id)
        post.likes = Like.query.filter_by(post_id=post_id).count()
        db.session.commit()
        
        return jsonify({'success': 'liked'})


@app.route('/api/posts/<int:post_id>/likes', methods=['GET'])
def get_post_likes(post_id):
    likes = Like.query.filter_by(post_id=post_id).all()
    like_list = [like.serialize() for like in likes]
    return jsonify(like_list)


#comment on post
@app.route('/api/posts/<int:post_id>/comments', methods=['GET','POST','OPTIONS'])
def comments(post_id):
    if request.method == 'GET':
        comments = Comment.query.filter_by(post_id=post_id).all()
        comments_list = [comment.serialize() for comment in comments]
        return jsonify(comments_list)
    
    elif request.method == 'POST':
        data = get_data()
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'error': 'Not authorized'}), 401
        user = UserModel.query.filter_by(id=user_id).first()
        if user:
            author_id = user.id
            author_name = user.get_full_name()
            body = data['body']
            
            comment = Comment(post_id= post_id, author_id=author_id, author_name=author_name, body=body)
            db.session.add(comment)
            db.session.commit()
            return jsonify(comment.serialize()), 200
        else:
            return jsonify({'error': 'User does not exist to comment'}), 404
    
  
#delete post
@app.route('/api/delete-post/<int:post_id>', methods=["DELETE"])
@cross_origin(supports_credentials=True)
def delete_post(post_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not authorized'}), 401

    post = PostModel.query.filter_by(id=post_id).first()
    if not post:
        return jsonify({'error': 'Post not found'}), 404

    if post.author_id != user_id:
        return jsonify({'error': 'Not authorized to delete this post'}), 403

    db.session.delete(post)
    db.session.commit()

    return jsonify("Post was deleted"), 200

#update post
@app.route('/api/update-post/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not authorized'}), 401

    data = get_data()
    new_title = data.get('title', '').strip()
    new_content = data.get('content', '').strip()

    if not new_title or not new_content:
        return jsonify({'error': 'Title and content cannot be empty'}), 400

    post = PostModel.query.filter_by(id=post_id).first()
    if not post:
        return jsonify({'error': 'Post not found'}), 404

    if post.author_id != user_id:
        return jsonify({'error': 'Not authorized to edit this post'}), 403

    post.title = new_title
    post.content = new_content
    db.session.commit()

    return jsonify(post.serialize()), 200

#delete comment
@app.route('/api/delete-comment/<int:comment_id>', methods=["DELETE"])
def delete_comment(comment_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not authorized'}), 401

    comment = Comment.query.filter_by(id=comment_id).first()
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404

    if comment.author_id != user_id:
        return jsonify({'error': 'Not authorized to delete this comment'}), 403

    db.session.delete(comment)
    db.session.commit()

    return jsonify("Comment was deleted"), 200

#update comment
@app.route('/api/update-comment/<int:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not authorized'}), 401

    data = get_data()
    new_body = data.get('body', '').strip()

    if not new_body:
        return jsonify({'error': 'Comment body cannot be empty'}), 400

    comment = Comment.query.filter_by(id=comment_id).first()
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404

    if comment.author_id != user_id:
        return jsonify({'error': 'Not authorized to edit this comment'}), 403

    comment.body = new_body
    db.session.commit()

    return jsonify(comment.serialize()), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV', 'development') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)

# app.py
import os
import datetime
import flask
from dotenv import load_dotenv
from flask import Flask, jsonify, request, session
from flask_cors import CORS, cross_origin
from models import db, login, UserModel, PostModel, Like, Comment, Bookmark, Follow
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token
from sqlalchemy import or_, func, desc
from utils import make_unique_slug, make_excerpt, make_username
from schema_migrate import migrate_schema, backfill_data

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
    migrate_schema()
    backfill_data()

def published_posts_query():
    return PostModel.query.filter(
        (PostModel.status == 'published') | (PostModel.status == None)
    )

def paginate_query(query, page, per_page):
    page = max(1, page)
    per_page = min(max(1, per_page), 50)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return {
        'posts': [p.serialize(include_content=False) for p in items],
        'page': page,
        'per_page': per_page,
        'total': total,
        'has_more': (page * per_page) < total
    }

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

    posts_query = published_posts_query()

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
        db.session.flush()
        new_user.username = make_username(email, first, last, new_user.id)
        db.session.commit()
        session['user_id'] = new_user.id
        return jsonify({'message': 'new user registered successfully', 'username': new_user.username}), 200


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
    first = data.get('first', user.first)
    last = data.get('last', user.last)
    bio = data.get('bio', user.bio)

    if 'password' in data and data['password']:
        user.set_password(data['password'])

    user.first = first
    user.last = last
    user.bio = bio

    if 'username' in data and data['username']:
        existing = UserModel.query.filter_by(username=data['username']).first()
        if existing and existing.id != user.id:
            return jsonify({'error': 'Username already taken'}), 409
        user.username = data['username'].lower().strip()

    db.session.commit()
    return jsonify({'message': 'Profile updated successfully!', 'user': user.serialize()})
       
    
@app.route('/api/users', methods=['GET'])
def get_all_users():
    if not get_current_user_id():
        return jsonify({'error': 'Not authorized'}), 401
    users = UserModel.query.all()
    return jsonify([user.serialize(public=True) for user in users])
    

@app.route('/api/users/<int:id>', methods=['GET'])
def get_user_by_id(id):
    user = UserModel.query.filter_by(id=id).first()
    if user:
        return jsonify(user.serialize(public=True))
    return jsonify({'error': 'User not found'}), 404


################ POST MODEL RELATED ROUTES ###############
@app.route('/api/new-post', methods=['POST'])
def create_new_post():
    data = get_data()
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not authorized - Please login first'}), 401

    user = UserModel.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': 'User does not exist to create new post'}), 404

    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    label = data.get('label', '').strip()
    status = data.get('status', 'published')

    if not title or not content or not label:
        return jsonify({'error': 'Title, content, and community are required'}), 400

    new_post = PostModel(
        author_id=user.id,
        author_name=user.get_full_name(),
        title=title,
        content=content,
        excerpt=make_excerpt(content),
        likes=0,
        label=label,
        status=status,
        view_count=0
    )
    db.session.add(new_post)
    db.session.flush()
    new_post.slug = make_unique_slug(title, new_post.id)
    db.session.commit()
    return jsonify({'message': 'Post was added successfully', 'post': new_post.serialize()}), 200
        
            
@app.route('/api/posts', methods=['GET'])
def get_all_posts():
    label = request.args.get('label')
    sort = request.args.get('sort', 'newest')
    page = request.args.get('page', type=int)
    per_page = request.args.get('per_page', 12, type=int)

    query = published_posts_query()
    if label:
        query = query.filter_by(label=label)

    if sort == 'trending':
        query = query.order_by(desc(PostModel.likes + PostModel.view_count), desc(PostModel.created_at))
    elif sort == 'popular':
        query = query.order_by(desc(PostModel.likes), desc(PostModel.created_at))
    else:
        query = query.order_by(desc(PostModel.created_at))

    if page:
        return jsonify(paginate_query(query, page, per_page))

    posts = query.all()
    return jsonify([post.serialize(include_content=False) for post in posts])
    

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
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    if post.status == 'draft' and post.author_id != get_current_user_id():
        return jsonify({'error': 'Post not found'}), 404
    post.view_count = (post.view_count or 0) + 1
    db.session.commit()
    return jsonify(post.serialize())


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
    post.excerpt = make_excerpt(new_content)
    post.updated_at = datetime.datetime.utcnow()
    if post.slug:
        post.slug = make_unique_slug(new_title, post.id)
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


################ PLATFORM & DISCOVERY ROUTES ###############

@app.route('/api/stats', methods=['GET'])
def platform_stats():
    return jsonify({
        'writers': UserModel.query.count(),
        'posts': published_posts_query().count(),
        'communities': db.session.query(PostModel.label).distinct().count(),
        'comments': Comment.query.count(),
        'total_likes': db.session.query(func.sum(PostModel.likes)).scalar() or 0
    })


@app.route('/api/trending', methods=['GET'])
def trending_posts():
    limit = min(request.args.get('limit', 6, type=int), 20)
    posts = published_posts_query().order_by(
        desc(PostModel.likes + PostModel.view_count),
        desc(PostModel.created_at)
    ).limit(limit).all()
    return jsonify([p.serialize(include_content=False) for p in posts])


@app.route('/api/posts/slug/<slug>', methods=['GET'])
def get_post_by_slug(slug):
    post = PostModel.query.filter_by(slug=slug).first()
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    if post.status == 'draft' and post.author_id != get_current_user_id():
        return jsonify({'error': 'Post not found'}), 404
    post.view_count = (post.view_count or 0) + 1
    db.session.commit()
    return jsonify(post.serialize())


@app.route('/api/authors/<username>', methods=['GET'])
def get_author(username):
    user = UserModel.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'Author not found'}), 404
    post_count = published_posts_query().filter_by(author_id=user.id).count()
    follower_count = Follow.query.filter_by(following_id=user.id).count()
    data = user.serialize(public=True)
    data['post_count'] = post_count
    data['follower_count'] = follower_count
    return jsonify(data)


@app.route('/api/authors/<username>/posts', methods=['GET'])
def get_author_posts(username):
    user = UserModel.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'Author not found'}), 404
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    query = published_posts_query().filter_by(author_id=user.id).order_by(desc(PostModel.created_at))
    return jsonify(paginate_query(query, page, per_page))


@app.route('/api/posts/<int:post_id>/bookmark', methods=['POST', 'DELETE'])
def bookmark_post(post_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not authorized'}), 401
    post = PostModel.query.get(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404

    existing = Bookmark.query.filter_by(user_id=user_id, post_id=post_id).first()
    if request.method == 'POST':
        if existing:
            return jsonify({'bookmarked': True})
        db.session.add(Bookmark(user_id=user_id, post_id=post_id))
        db.session.commit()
        return jsonify({'bookmarked': True})
    if existing:
        db.session.delete(existing)
        db.session.commit()
    return jsonify({'bookmarked': False})


@app.route('/api/bookmarks', methods=['GET'])
def get_bookmarks():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Not authorized'}), 401
    bookmarks = Bookmark.query.filter_by(user_id=user_id).order_by(desc(Bookmark.created_at)).all()
    post_ids = [b.post_id for b in bookmarks]
    posts = PostModel.query.filter(PostModel.id.in_(post_ids)).all() if post_ids else []
    post_map = {p.id: p for p in posts}
    return jsonify([post_map[b.post_id].serialize(include_content=False) for b in bookmarks if b.post_id in post_map])


@app.route('/api/users/<int:user_id>/follow', methods=['POST', 'DELETE'])
def follow_user(user_id):
    follower_id = get_current_user_id()
    if not follower_id:
        return jsonify({'error': 'Not authorized'}), 401
    if follower_id == user_id:
        return jsonify({'error': 'Cannot follow yourself'}), 400
    target = UserModel.query.get(user_id)
    if not target:
        return jsonify({'error': 'User not found'}), 404

    existing = Follow.query.filter_by(follower_id=follower_id, following_id=user_id).first()
    if request.method == 'POST':
        if not existing:
            db.session.add(Follow(follower_id=follower_id, following_id=user_id))
            db.session.commit()
        return jsonify({'following': True})
    if existing:
        db.session.delete(existing)
        db.session.commit()
    return jsonify({'following': False})


@app.route('/api/feed/rss', methods=['GET'])
def rss_feed():
    posts = published_posts_query().order_by(desc(PostModel.created_at)).limit(20).all()
    items = []
    for post in posts:
        items.append(f"""    <item>
      <title>{post.title}</title>
      <link>https://starlight-blog.vercel.app/post/{post.slug}</link>
      <description><![CDATA[{post.excerpt or ''}]]></description>
      <author>{post.author_name}</author>
      <pubDate>{post.created_at}</pubDate>
    </item>""")
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>StarLight Blog</title>
    <link>https://starlight-blog.vercel.app</link>
    <description>Stories from the StarLight community</description>
{chr(10).join(items)}
  </channel>
</rss>"""
    return rss, 200, {'Content-Type': 'application/rss+xml'}


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV', 'development') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)

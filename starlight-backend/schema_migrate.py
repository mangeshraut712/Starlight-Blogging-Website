from sqlalchemy import inspect, text
from models import db, UserModel, PostModel
from utils import make_unique_slug, make_excerpt, make_username


def migrate_schema():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()

    column_additions = [
        ('users', 'username', 'VARCHAR(80)'),
        ('users', 'bio', 'TEXT'),
        ('users', 'avatar_url', 'VARCHAR(500)'),
        ('posts', 'slug', 'VARCHAR(200)'),
        ('posts', 'excerpt', 'TEXT'),
        ('posts', 'cover_image', 'VARCHAR(500)'),
        ('posts', 'view_count', 'INTEGER DEFAULT 0'),
        ('posts', 'status', "VARCHAR(20) DEFAULT 'published'"),
        ('posts', 'updated_at', 'DATETIME'),
    ]

    for table, column, col_type in column_additions:
        if table not in tables:
            continue
        existing = {c['name'] for c in inspector.get_columns(table)}
        if column not in existing:
            db.session.execute(text(f'ALTER TABLE {table} ADD COLUMN {column} {col_type}'))
    db.session.commit()


def backfill_data():
    for user in UserModel.query.filter((UserModel.username == None) | (UserModel.username == '')).all():
        user.username = make_username(user.email, user.first, user.last, user.id)

    for post in PostModel.query.all():
        if not post.slug:
            post.slug = make_unique_slug(post.title, post.id)
        if not post.excerpt:
            post.excerpt = make_excerpt(post.content)
        if not post.status:
            post.status = 'published'
        if post.view_count is None:
            post.view_count = 0
        if not post.updated_at:
            post.updated_at = post.created_at

    db.session.commit()

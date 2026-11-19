"""Unit tests for schema migration and data backfill."""

from app import app as flask_app
from models import PostModel, UserModel, db
from schema_migrate import backfill_data, migrate_schema


def test_backfill_data_populates_missing_fields(client):
    with flask_app.app_context():
        # Insert user without username
        user = UserModel(
            email="researcher@example.com",
            first="Grace",
            last="Hopper",
        )
        user.set_password("safe-password-123")
        db.session.add(user)
        db.session.flush()

        # Insert post without slug, excerpt, status, or view_count
        post = PostModel(
            author_id=user.id,
            author_name="Grace Hopper",
            title="Compiler Optimization Techniques",
            content="<p>An in-depth look at compilers and intermediate representations.</p>",
            label="Technology",
            slug=None,
            excerpt=None,
            status=None,
            view_count=None,
            updated_at=None,
        )
        db.session.add(post)
        db.session.commit()

        # Execute backfill
        backfill_data()

        # Verify backfilled records
        refreshed_user = db.session.get(UserModel, user.id)
        assert refreshed_user.username is not None
        assert "gracehopper" in refreshed_user.username or "researcher" in refreshed_user.username

        refreshed_post = db.session.get(PostModel, post.id)
        assert refreshed_post.slug is not None
        assert "compiler-optimization" in refreshed_post.slug
        assert refreshed_post.excerpt is not None
        assert "compilers" in refreshed_post.excerpt
        assert refreshed_post.status == "published"
        assert refreshed_post.view_count == 0
        assert refreshed_post.updated_at is not None
        assert refreshed_post.updated_at >= refreshed_post.created_at


def test_migrate_schema_idempotency(client):
    """Running migrate_schema on an up-to-date schema is a safe no-op."""
    with flask_app.app_context():
        migrate_schema()


def test_column_addition_types_match_the_models_on_postgresql():
    """Added columns use the same base type PostgreSQL gets for the model (no DATETIME)."""
    from sqlalchemy.dialects import postgresql

    from schema_migrate import COLUMN_ADDITIONS

    tables = {"users": UserModel.__table__, "posts": PostModel.__table__}
    for table, column, ddl_type in COLUMN_ADDITIONS:
        compiled = tables[table].c[column].type.compile(dialect=postgresql.dialect())
        assert ddl_type.split("(")[0].split()[0] == compiled.split("(")[0].split()[0], (table, column)

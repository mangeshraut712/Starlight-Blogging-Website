import os
import tempfile

_db_file = tempfile.NamedTemporaryFile(prefix='starlight-test-', suffix='.db', delete=False)
os.environ['DATABASE_URL'] = f'sqlite:///{_db_file.name}'
os.environ['FLASK_ENV'] = 'development'
os.environ['ALLOWED_ORIGINS'] = 'http://localhost:4200'
os.environ['SECRET_KEY'] = 'test-secret'
os.environ['RUN_SCHEMA_PATCH'] = 'true'
os.environ['SITE_URL'] = 'https://example.test/Starlight-Blogging-Website'

import pytest
from app import app as flask_app, limiter
from models import db

limiter.enabled = False


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    flask_app.config['RATELIMIT_ENABLED'] = False
    with flask_app.app_context():
        db.drop_all()
        db.create_all()
    with flask_app.test_client() as test_client:
        yield test_client
    with flask_app.app_context():
        db.session.remove()
        db.drop_all()

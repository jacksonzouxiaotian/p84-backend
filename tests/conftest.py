# tests/conftest.py
# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""

import pytest
from flask_jwt_extended import create_access_token
from research_assistant.app import create_app
from research_assistant.extensions import db as _db
from research_assistant.user.models import User

@pytest.fixture
def app():
    """Create a Flask app instance for testing."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "DEBUG_TB_ENABLED": False,
        "JWT_SECRET_KEY": "test-secret-key",  # Needed for JWT
    })

    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def db(app):
    """Provide the database instance."""
    return _db


@pytest.fixture
def client(app):
    """Provide Flask test client."""
    return app.test_client()


@pytest.fixture
def test_user(db):
    user = User(username="testuser", email="test@example.com", password="123456")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def auth_client(client, test_user):
    token = create_access_token(identity=str(test_user.id)) 
    client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {token}'
    return client

@pytest.fixture
def mock_s3_upload(monkeypatch):
    """Mock S3 upload to avoid real file upload."""
    def mock_upload(file, key):
        return f"https://mock-s3/{key}"
    monkeypatch.setattr("research_assistant.utils.upload_file_to_s3", mock_upload)


@pytest.fixture
def mock_s3_client(monkeypatch, app):
    """Mock the already initialized S3 client in the Flask app context."""
    class MockS3Client:
        def generate_presigned_url(self, *args, **kwargs):
            return "https://mock-presigned-url"
        def delete_object(self, *args, **kwargs):
            return {}
    with app.app_context():
        app.s3_client = MockS3Client()
    yield

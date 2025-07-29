# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""

import logging

# tests/conftest.py

# -*- coding: utf-8 -*-
import pytest
from webtest import TestApp

from research_assistant.app import create_app
from research_assistant.database import db as _db

from .factories import UserFactory


@pytest.fixture
def app():
    """Create application for the tests."""
    _app = create_app("tests.settings")
    _app.logger.setLevel(logging.CRITICAL)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture
def testapp(app):
    """Create Webtest app."""
    return TestApp(app)


@pytest.fixture
def db(app):
    """Create database for the tests."""
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()


@pytest.fixture
def user(db):
    """Create user for the tests."""
    user = UserFactory(password="myprecious")
    db.session.commit()
    return user
from research_assistant.extensions import db as _db
from research_assistant.user.models import User

test_email = "test@example.com"
test_username = "testuser"
test_password = "myprecious"

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "DEBUG_TB_ENABLED": False,
    })

    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()

@pytest.fixture
def db(app):
    return _db

@pytest.fixture
def client(app):
    """提供 Flask test client。"""
    return app.test_client()

@pytest.fixture
def user(db):
    user = User(
        email=test_email,
        username=test_username,
        password=test_password
    )
    user.active = True
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def testapp(app):
    import logging
    app.logger.setLevel(logging.ERROR)
    return TestApp(app)

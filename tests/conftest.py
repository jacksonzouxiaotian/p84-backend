<<<<<<< HEAD
# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""

import logging

=======
# tests/conftest.py

# -*- coding: utf-8 -*-
>>>>>>> feature-brainstorm-planning
import pytest
from webtest import TestApp

from research_assistant.app import create_app
<<<<<<< HEAD
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
=======
from research_assistant.extensions import db as _db
from research_assistant.user.models import User

# 测试用户凭据
test_email = "test@example.com"
test_username = "testuser"
test_password = "myprecious"

@pytest.fixture
def app():
    """
    创建 Flask 测试应用，使用内存 SQLite。
    """
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
    """提供 SQLAlchemy db 实例。"""
    return _db

@pytest.fixture
def client(app):
    """提供 Flask test client。"""
    return app.test_client()

@pytest.fixture
def user(db):
    """在数据库中创建并返回一个激活状态的测试用户。"""
    user = User(
        email=test_email,
        username=test_username,
        password=test_password  # LoginForm 已支持明文回退
    )
    user.active = True
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def testapp(app):
    """提供 WebTest TestApp，用于功能测试，并压制 INFO 日志。"""
    import logging
    app.logger.setLevel(logging.ERROR)
    return TestApp(app)
>>>>>>> feature-brainstorm-planning

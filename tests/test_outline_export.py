# tests/test_outline_export.py
import pytest

from research_assistant.app import create_app
from research_assistant.extensions import db
from research_assistant.outline.models import Section


@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
    })
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_export_empty_outline(client):
    """空大纲时应返回空字符串"""
    resp = client.get('/api/outline/export')
    assert resp.status_code == 200
    assert resp.data.decode('utf-8') == ""

def test_export_single_and_subsections(client, app):
    """有根节点和子节点时，按 Markdown 层级导出"""
    with app.app_context():
        # 创建根节点
        root = Section(title='Root Title', summary='Root summary', order=1)
        db.session.add(root)
        db.session.commit()
        # 创建子节点
        child = Section(
            title='Child Title',
            summary='Child summary',
            parent_id=root.id,
            order=1
        )
        db.session.add(child)
        db.session.commit()

    resp = client.get('/api/outline/export')
    text = resp.data.decode('utf-8').split('\n\n')

    # 检查导出的 Markdown 结构
    assert text[0] == '# Root Title'
    assert text[1] == 'Root summary'
    assert text[2] == '## Child Title'
    assert text[3] == 'Child summary'

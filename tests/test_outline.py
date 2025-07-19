# tests/test_outline.py

import pytest

from research_assistant.app import create_app
from research_assistant.extensions import db
from research_assistant.outline.models import Section
from research_assistant.planning.models import Phase, Task


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
        # 准备一个 Phase，用于测试 Structural Planning 完成标记
        phase = Phase(title='Methodology / Structural Planning')
        db.session.add(phase)
        db.session.commit()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_export_markdown_and_plain(client, app):
    """测试 Markdown 与纯文本导出接口"""
    with app.app_context():
        root = Section(title='R', order=1, summary='Root')
        db.session.add(root)
        db.session.commit()
        child = Section(title='C', order=1, summary='Child', parent_id=root.id)
        db.session.add(child)
        db.session.commit()

    md = client.get('/api/outline/export')
    assert md.status_code == 200
    txt_md = md.data.decode()
    assert '# R' in txt_md and 'Root' in txt_md
    assert '## C' in txt_md and 'Child' in txt_md

    pt = client.get('/api/outline/export/plain')
    assert pt.status_code == 200
    lines = pt.data.decode().splitlines()
    assert lines[0].startswith('- R')
    assert 'Root' in lines[1]
    assert lines[2].strip().startswith('- C')

def test_complete_outline_endpoint(client, app):
    """调用 /export/complete 手动标记 Structural Planning 完成"""
    phase = Phase.query.filter_by(title='Methodology / Structural Planning').first()
    phase.tasks.clear()
    db.session.commit()
    assert len(phase.tasks) == 0

    r = client.post('/api/outline/complete')
    assert r.status_code == 204

    phase = Phase.query.filter_by(title='Methodology / Structural Planning').first()
    assert len(phase.tasks) == 1

def test_outline_chat(client):
    """Mock AI 聊天接口返回格式"""
    r = client.post('/api/outline/chat', json={'content':'test'})
    assert r.status_code == 200
    data = r.get_json()
    assert '[模拟回答]' in data['reply']
    assert 'test' in data['reply']

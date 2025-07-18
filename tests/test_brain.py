# tests/test_brain.py

import pytest
from research_assistant.app import create_app
from research_assistant.extensions import db
from research_assistant.brain.models import BrainEntry
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
        # 准备一个 Phase，用于测试自动/手动完成标记
        phase = Phase(title='Define Topic & Question')
        db.session.add(phase)
        db.session.commit()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_list_empty_brain(client):
    """列表为空时返回空列表"""
    resp = client.get('/api/brainstorm/')
    assert resp.status_code == 200
    assert resp.get_json() == []

def test_create_brain_entry_and_auto_mark(client, app):
    """POST 创建 BrainEntry 时自动标记 Define Topic 阶段完成"""
    phase = Phase.query.filter_by(title='Define Topic & Question').first()
    assert phase is not None
    initial = len(phase.tasks)

    payload = {'why':'Why','what':'What','where':'Where','when':'When','who':'Who'}
    r = client.post('/api/brainstorm/', json=payload)
    assert r.status_code == 201

    phase = Phase.query.filter_by(title='Define Topic & Question').first()
    assert len(phase.tasks) == initial + 1

def test_complete_brainstorm_endpoint(client, app):
    """调用 /complete 手动标记 Define Topic 阶段完成"""
    phase = Phase.query.filter_by(title='Define Topic & Question').first()
    # 清空已有任务
    phase.tasks.clear()
    db.session.commit()
    assert len(phase.tasks) == 0

    r = client.post('/api/brainstorm/complete')
    assert r.status_code == 204

    phase = Phase.query.filter_by(title='Define Topic & Question').first()
    assert len(phase.tasks) == 1

def test_brainstorm_chat(client):
    """Mock AI 聊天接口返回格式"""
    r = client.post('/api/brainstorm/chat', json={'content':'hello'})
    assert r.status_code == 200
    data = r.get_json()
    assert '[模拟回答]' in data['reply']
    assert 'hello' in data['reply']

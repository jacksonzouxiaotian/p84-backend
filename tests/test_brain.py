# tests/test_brain.py

import pytest

from research_assistant.app import create_app
from research_assistant.brain.models import BrainEntry
from research_assistant.extensions import db
from research_assistant.planning.models import Phase, Task


@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })
    with app.app_context():
        db.create_all()
        # 初始化一个 Phase 供 complete 测试使用
        db.session.add(Phase(title='Define Topic & Question', order=1))
        db.session.commit()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_list_and_create_and_auto_complete(client):
    # 列表最初为空
    r = client.get('/api/brainstorm/')
    assert r.status_code == 200
    assert r.get_json() == []

    # 创建不完整的 entry，不应触发自动标记
    payload = {'why':'A', 'what':'B'}
    r = client.post('/api/brainstorm/', json=payload)
    assert r.status_code == 201
    assert 'id' in r.get_json()
    # Phase 下无任务
    from research_assistant.planning.models import Phase
    phase = Phase.query.filter_by(title='Define Topic & Question').first()
    assert phase and len(phase.tasks) == 0

    # 创建完整的 entry，应触发一次自动标记
    payload = {'why':'X','what':'Y','where':'Z','when':'T','who':'U'}
    r = client.post('/api/brainstorm/', json=payload)
    assert r.status_code == 201
    phase = Phase.query.filter_by(title='Define Topic & Question').first()
    # 应只有一条 “Brainstorm Complete”
    assert sum(1 for t in phase.tasks if t.description=='Brainstorm Complete') == 1

def test_update_and_delete_entry(client):
    # 创建一条
    r = client.post('/api/brainstorm/', json={'why':'W'})
    entry = r.get_json()
    eid = entry['id']

    # 更新
    r2 = client.put(f'/api/brainstorm/{eid}', json={'what':'NewWhat'})
    assert r2.status_code == 200
    updated = r2.get_json()
    assert updated['what'] == 'NewWhat'

    # 删除
    r3 = client.delete(f'/api/brainstorm/{eid}')
    assert r3.status_code == 204
    assert client.get('/api/brainstorm/').get_json() == []

def test_complete_endpoint_and_chat(client):
    # 确保 phase 任务清空
    from research_assistant.planning.models import Phase
    phase = Phase.query.filter_by(title='Define Topic & Question').first()
    phase.tasks.clear()
    db.session.commit()
    assert len(phase.tasks) == 0

    # 调用 /complete
    r = client.post('/api/brainstorm/complete')
    assert r.status_code == 204
    phase = Phase.query.filter_by(title='Define Topic & Question').first()
    assert len(phase.tasks) == 1

    # 测试 chat
    r = client.post('/api/brainstorm/chat', json={'content':'hello'})
    assert r.status_code == 200
    reply = r.get_json()['reply']
    assert '模拟回答' in reply and 'hello' in reply

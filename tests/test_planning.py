# tests/test_planning.py

import pytest
from datetime import date
from research_assistant.app import create_app
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
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_planning_chat(client):
    """Mock AI 聊天接口返回格式"""
    r = client.post('/api/planning/chat', json={'content':'help'})
    assert r.status_code == 200
    data = r.get_json()
    assert '[模拟回答]' in data['reply']
    assert 'help' in data['reply']

def test_create_and_list_phase(client):
    """创建 Phase 并通过列表接口获取"""
    r = client.post('/api/planning/', json={
        'title': 'Phase 1',
        'start_date': '2025-07-04',
        'end_date': '2025-07-11',
        'deadline': '2025-07-14',
        'tasks': [
            {'description': 'T1'},
            {'description': 'T2', 'completed': True}
        ]
    })
    assert r.status_code == 201
    p = r.get_json()
    assert p['total_tasks'] == 2
    assert p['completed_tasks'] == 1

    lst = client.get('/api/planning/').get_json()
    assert any(item['title']=='Phase 1' for item in lst)

def test_toggle_and_cascade_delete(client, app):
    """测试任务切换和级联删除"""
    # 先创建一个 Phase
    r = client.post('/api/planning/', json={
        'title': 'Phase X',
        'tasks': [{'description': 'A'}]
    })
    p = r.get_json()
    pid = p['id']
    tid = p['tasks'][0]['id']

    # 切换完成状态
    assert not p['tasks'][0]['completed']
    r1 = client.patch(f'/api/planning/{pid}/tasks/{tid}')
    assert r1.get_json()['completed']

    # 级联删除 Phase 会删除 Task
    assert Task.query.count() == 1
    client.delete(f'/api/planning/{pid}')
    assert Task.query.count() == 0

def test_list_phases_sorted(client, app):
    """列表接口按 start_date 升序返回"""
    with app.app_context():
        p3 = Phase(title='P3', start_date=date(2025,9,3))
        p1 = Phase(title='P1', start_date=date(2025,9,1))
        p2 = Phase(title='P2', start_date=date(2025,9,2))
        db.session.add_all([p3,p1,p2])
        db.session.commit()

    resp = client.get('/api/planning/').get_json()
    titles = [x['title'] for x in resp]
    assert titles == ['P1','P2','P3']

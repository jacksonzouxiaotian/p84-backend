
# tests/test_planning.py

import pytest
from research_assistant.app import create_app
from research_assistant.extensions import db
from research_assistant.planning.models import Phase, Task
from research_assistant.outline.models import Section

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

def test_fetch_empty_planning(client):
    r = client.get('/api/planning/')
    assert r.status_code == 200
    data = r.get_json()
    assert data['sections'] == []
    assert data['timeline'] == []

def test_save_and_fetch_planning(client):
    # 先准备一些示例数据
    sections = [
        {'title':'Sec1','summary':'S1','subsections':[
            {'title':'Sub1','summary':'SS1','subsections':[]}
        ]}
    ]
    timeline = [
        {'title':'P1','start_date':'2025-08-01','end_date':'2025-08-10','deadline':'2025-08-15','tasks':[
            {'description':'T1','completed':False}
        ]}
    ]

    # 保存
    r = client.post('/api/planning/', json={'sections':sections, 'timeline':timeline})
    assert r.status_code == 204

    # 再次 fetch
    r2 = client.get('/api/planning/')
    assert r2.status_code == 200
    data = r2.get_json()
    # Sections
    assert len(data['sections']) == 1
    assert data['sections'][0]['title'] == 'Sec1'
    assert data['sections'][0]['subsections'][0]['title'] == 'Sub1'
    # Timeline
    assert len(data['timeline']) == 1
    ph = data['timeline'][0]
    assert ph['title'] == 'P1'
    assert ph['start_date'] == '2025-08-01'
    assert ph['tasks'][0]['description'] == 'T1'

def test_task_toggle_and_cleanup(client):
    # 保存一个 phase 带任务
    timeline = [{'title':'X','tasks':[{'description':'A'}]}]
    client.post('/api/planning/', json={'sections':[], 'timeline':timeline})
    # 取到它的 id 和 task id
    resp = client.get('/api/planning/').get_json()
    ph = resp['timeline'][0]
    pid = ph['id']
    tid = ph['tasks'][0]['id']

    # 切换完成状态
    r1 = client.patch(f'/api/planning/{pid}/tasks/{tid}')
    assert r1.status_code == 200
    assert r1.get_json()['completed'] is True

    # 删除 phase 应级联删除 tasks
    r2 = client.delete(f'/api/planning/{pid}')
    assert r2.status_code == 204
    # 确保 db 里无残留
    assert Task.query.count() == 0

def test_planning_chat(client):
    r = client.post('/api/planning/chat', json={'content':'help me'})
    assert r.status_code == 200
    body = r.get_json()
    assert '模拟回答' in body['reply'] and 'help me' in body['reply']

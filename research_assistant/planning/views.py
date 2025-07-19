from datetime import date

from flask import Blueprint, jsonify, request

from research_assistant.extensions import db
from research_assistant.outline.models import Section
from research_assistant.planning.models import Phase, Task

planning_bp = Blueprint('planning', __name__, url_prefix='/planning')

@planning_bp.route('/', methods=['GET'])
def fetch_planning():
    """GET /api/planning → { sections, timeline }"""
    roots = Section.query.filter_by(parent_id=None).order_by(Section.order).all()
    sections = [sec.to_dict() for sec in roots]

    phases = Phase.query.order_by(Phase.order).all()
    timeline = [ph.to_dict() for ph in phases]

    return jsonify({'sections': sections, 'timeline': timeline}), 200

@planning_bp.route('/', methods=['POST'])
def save_planning():
    """POST /api/planning {sections, timeline} → 重建 Outline & Phase"""
    data = request.get_json() or {}
    sections_data = data.get('sections', [])
    timeline_data = data.get('timeline', [])

    # 重建 Outline
    from research_assistant.outline.models import Section as SectModel
    SectModel.query.delete()
    db.session.commit()

    def _create_sections(items, parent_id=None):
        for idx, item in enumerate(items):
            sec = SectModel(
                title     = item.get('title'),
                summary   = item.get('summary'),
                parent_id = parent_id,
                order     = idx
            )
            db.session.add(sec)
            db.session.flush()
            for child in item.get('subsections', []):
                _create_sections(item['subsections'], parent_id=sec.id)

    _create_sections(sections_data)

    # 重建 Phases & Tasks
    Task.query.delete()
    Phase.query.delete()
    db.session.commit()

    for idx, item in enumerate(timeline_data):
        ph = Phase(
            title      = item.get('title'),
            start_date = date.fromisoformat(item['start_date']) if item.get('start_date') else None,
            end_date   = date.fromisoformat(item['end_date'])   if item.get('end_date')   else None,
            deadline   = date.fromisoformat(item['deadline'])   if item.get('deadline')   else None,
            order      = idx
        )
        for t in item.get('tasks', []):
            ph.tasks.append(Task(
                description = t.get('description'),
                completed   = bool(t.get('completed', False))
            ))
        db.session.add(ph)

    db.session.commit()
    return '', 204

@planning_bp.route('/<int:phase_id>', methods=['DELETE'])
def delete_phase(phase_id):
    """DELETE /api/planning/<phase_id> → 删除 Phase"""
    phase = Phase.query.get_or_404(phase_id)
    db.session.delete(phase)
    db.session.commit()
    return '', 204

@planning_bp.route('/<int:phase_id>/tasks/<int:task_id>', methods=['PATCH'])
def toggle_task(phase_id, task_id):
    """PATCH /api/planning/<phase_id>/tasks/<task_id> → 切换 Task 完成状态"""
    task = Task.query.filter_by(id=task_id, phase_id=phase_id).first_or_404()
    task.completed = not task.completed
    db.session.commit()
    return jsonify(task.to_dict()), 200

@planning_bp.route('/chat', methods=['POST'])
def planning_chat():
    """Mock AI 聊天接口"""
    data = request.get_json() or {}
    return jsonify({
        'reply': f"[模拟回答] 收到 Planning 阶段的问题：{data.get('content')}"
    }), 200

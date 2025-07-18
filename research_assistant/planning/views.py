from flask import Blueprint, request, jsonify
from research_assistant.extensions import db
from research_assistant.planning.models import Phase, Task
from research_assistant.outline.models import Section
from datetime import date

planning_bp = Blueprint('planning', __name__, url_prefix='/api/planning')

@planning_bp.route('/', methods=['GET'])
def fetch_planning():
    """
    GET /api/planning
    返回 {
      sections: [ ...outline nodes... ],
      timeline: [ ...phase objects... ]
    }
    """
    # 1. Sections 树（Outline 顶级及子节点）
    roots = Section.query.filter_by(parent_id=None).order_by(Section.order).all()
    sections = [sec.to_dict() for sec in roots]

    # 2. Timeline（所有 Phase）
    phases = Phase.query.order_by(Phase.order).all()
    timeline = [ph.to_dict() for ph in phases]

    return jsonify({'sections': sections, 'timeline': timeline}), 200

@planning_bp.route('/', methods=['POST'])
def save_planning():
    """
    POST /api/planning
    接收 { sections: [...], timeline: [...] }，全量重建 Outline 和 Phase
    """
    data = request.get_json() or {}
    sections_data = data.get('sections', [])
    timeline_data = data.get('timeline', [])

    # --- 重建 Outline Sections ---
    from research_assistant.outline.models import Section as SectModel
    # 清空旧的
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
            db.session.flush()  # 拿到 sec.id
            for child in item.get('subsections', []):
                _create_sections(item['subsections'], parent_id=sec.id)

    _create_sections(sections_data)

    # --- 重建 Phases & Tasks ---
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
        # 还原任务
        for t in item.get('tasks', []):
            ph.tasks.append(Task(
                description = t.get('description'),
                completed   = bool(t.get('completed', False))
            ))
        db.session.add(ph)

    db.session.commit()
    return '', 204

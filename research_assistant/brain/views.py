# research_assistant/brain/views.py

from flask import Blueprint, request, jsonify
from research_assistant.extensions import db
from research_assistant.brain.models import BrainEntry
from research_assistant.planning.models import Phase, Task

brainstorm_bp = Blueprint('brainstorm', __name__, url_prefix='/api/brainstorm')

@brainstorm_bp.route('/', methods=['GET'])
def list_brain_entries():
    entries = BrainEntry.query.order_by(BrainEntry.created_at.desc()).all()
    return jsonify([e.to_dict() for e in entries]), 200

@brainstorm_bp.route('/', methods=['POST'])
def create_brain_entry():
    data = request.get_json() or {}
    entry = BrainEntry(
        why   = data.get('why'),
        what  = data.get('what'),
        where = data.get('where'),
        when  = data.get('when'),
        who   = data.get('who'),
    )
    db.session.add(entry)

    # 如果 5W 都填写了，则自动标记 “Define Topic & Question” 阶段完成（Mock）
    if all([entry.why, entry.what, entry.where, entry.when, entry.who]):
        phase = Phase.query.filter_by(title='Define Topic & Question').first()
        if phase:
            # 避免重复插入
            exists = any(t.description == 'Brainstorm Complete' for t in phase.tasks)
            if not exists:
                phase.tasks.append(Task(description='Brainstorm Complete', completed=True))

    db.session.commit()
    return jsonify(entry.to_dict()), 201

@brainstorm_bp.route('/<int:entry_id>', methods=['PUT'])
def update_brain_entry(entry_id):
    entry = BrainEntry.query.get_or_404(entry_id)
    data = request.get_json() or {}
    for field in ('why','what','where','when','who'):
        if field in data:
            setattr(entry, field, data[field])
    db.session.commit()
    return jsonify(entry.to_dict()), 200

@brainstorm_bp.route('/<int:entry_id>', methods=['DELETE'])
def delete_brain_entry(entry_id):
    entry = BrainEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    return '', 204

@brainstorm_bp.route('/complete', methods=['POST'])
def complete_brainstorm():
    """手动标记 Brainstorm（Define Topic）阶段完成"""
    phase = Phase.query.filter_by(title='Define Topic & Question').first()
    if phase:
        exists = any(t.description == 'Brainstorm Complete' for t in phase.tasks)
        if not exists:
            phase.tasks.append(Task(description='Brainstorm Complete', completed=True))
            db.session.commit()
    return '', 204

@brainstorm_bp.route('/chat', methods=['POST'])
def brainstorm_chat():
    """Mock AI 聊天接口"""
    data = request.get_json() or {}
    return jsonify({
        'reply': f"[模拟回答] 收到 Brainstorm 阶段的问题：{data.get('content')}"
    }), 200

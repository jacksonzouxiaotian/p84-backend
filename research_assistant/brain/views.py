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

@brainstorm_bp.route('/save', methods=['POST'])
def save_brainstorm_session():
    """
    前端 saveBrainstormSession() 调用此接口：
      POST /api/brainstorm/save
      payload { messages, fiveW, timestamp }
    我们这里只把 fiveW 写入一条 BrainEntry，messages/timestamp 可根据需求另行存储。
    """
    data = request.get_json() or {}
    fiveW = data.get('fiveW', {})
    entry = BrainEntry(
        why   = fiveW.get('why'),
        what  = fiveW.get('what'),
        where = fiveW.get('where'),
        when  = fiveW.get('when'),
        who   = fiveW.get('who'),
    )
    db.session.add(entry)

    # If all 5W provided, mock 自动标记 “Define Topic & Question” 阶段完成
    if all([entry.why, entry.what, entry.where, entry.when, entry.who]):
        phase = Phase.query.filter_by(title='Define Topic & Question').first()
        if phase and not any(t.description == 'Brainstorm Complete' for t in phase.tasks):
            phase.tasks.append(Task(description='Brainstorm Complete', completed=True))

    db.session.commit()
    return jsonify({'id': entry.id}), 201

# research_assistant/brain/views.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from research_assistant.brain.models import BrainEntry
from research_assistant.extensions import db
from research_assistant.planning.models import Phase, Task
import logging

# 配置 logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Blueprint 定义，统一加上 /brainstorm 前缀
brainstorm_bp = Blueprint('brainstorm', __name__, url_prefix='/brainstorm')

@brainstorm_bp.route('/', methods=['GET'])
@jwt_required()
def list_brain_entries():
    user_id = get_jwt_identity()
    logger.debug(f"[DEBUG] list_brain_entries user_id={user_id}")
    entries = (
        BrainEntry.query
        .filter_by(user_id=user_id)
        .order_by(BrainEntry.created_at.desc())
        .all()
    )
    logger.debug(f"[DEBUG] Found {len(entries)} entries for user_id={user_id}")
    return jsonify([e.to_dict() for e in entries]), 200

@brainstorm_bp.route('/', methods=['POST'])
@jwt_required()
def create_brain_entry():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    entry = BrainEntry(
        why   = data.get('why'),
        what  = data.get('what'),
        where = data.get('where'),
        when  = data.get('when'),
        who   = data.get('who'),
        user_id = user_id,
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify(entry.to_dict()), 201

@brainstorm_bp.route('/<int:entry_id>', methods=['PUT'])
@jwt_required()
def update_brain_entry(entry_id):
    user_id = get_jwt_identity()
    entry = BrainEntry.query.filter_by(id=entry_id, user_id=user_id).first_or_404()
    data = request.get_json() or {}
    for field in ('why','what','where','when','who'):
        if field in data:
            setattr(entry, field, data[field])
    db.session.commit()
    return jsonify(entry.to_dict()), 200

@brainstorm_bp.route('/<int:entry_id>', methods=['DELETE'])
@jwt_required()
def delete_brain_entry(entry_id):
    user_id = get_jwt_identity()
    entry = BrainEntry.query.filter_by(id=entry_id, user_id=user_id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    return '', 204

@brainstorm_bp.route('/save', methods=['POST'])
@jwt_required()
def save_brainstorm_session():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    fiveW = data.get('fiveW', {})
    entry = BrainEntry(
        why   = fiveW.get('why'),
        what  = fiveW.get('what'),
        where = fiveW.get('where'),
        when  = fiveW.get('when'),
        who   = fiveW.get('who'),
        user_id = user_id,
    )
    db.session.add(entry)
    if all([entry.why,entry.what,entry.where,entry.when,entry.who]):
        phase = Phase.query.filter_by(title='Define Topic & Question').first()
        if phase and not any(t.description == 'Brainstorm Complete' for t in phase.tasks):
            new_task = Task(
                user_id = user_id,
                description = 'Brainstorm Complete',
                completed = True
            )
            phase.tasks.append(new_task)
            db.session.add(new_task)
    db.session.commit()
    return jsonify({'id': entry.id}), 201

@brainstorm_bp.route('/chat', methods=['POST'])
@jwt_required()
def brainstorm_chat():
    data = request.get_json() or {}
    user_input = data.get('message') or data.get('content') or ''
    reply = f"[Simulated answer] Received: {user_input}"
    return jsonify({'reply': reply}), 200

@brainstorm_bp.route('/progress', methods=['POST'])
@jwt_required()
def complete_brainstorm_step():
    return jsonify({'status':'ok'}), 200

@brainstorm_bp.route('/overall-feedback', methods=['POST'])
@jwt_required()
def overall_feedback():
    mock_feedback = "✨ This is your overall feedback: Please make sure the WHY, WHAT, etc. are detailed and clear。"
    return jsonify({'feedback': mock_feedback}), 200

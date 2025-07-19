# research_assistant/brain/views.py

from flask import Blueprint, jsonify, request

from research_assistant.brain.models import BrainEntry
from research_assistant.extensions import db
from research_assistant.planning.models import Phase, Task

# —————————————————————————————————————————————————————————
# 1. 一定要用 /api/brainstorm 作为前缀，这样前端对 /api/brainstorm/save 等调用才能命中
# —————————————————————————————————————————————————————————
brainstorm_bp = Blueprint('brainstorm', __name__, url_prefix='/api')

@brainstorm_bp.route('/', methods=['GET'])
def list_brain_entries():
    """GET /api/brainstorm/ → 返回所有 BrainEntry"""
    entries = BrainEntry.query.order_by(BrainEntry.created_at.desc()).all()
    return jsonify([e.to_dict() for e in entries]), 200

@brainstorm_bp.route('/', methods=['POST'])
def create_brain_entry():
    """POST /api/brainstorm/ → 新增一条 5W entry"""
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
    """PUT /api/brainstorm/<id> → 更新一条 5W entry"""
    entry = BrainEntry.query.get_or_404(entry_id)
    data = request.get_json() or {}
    for field in ('why','what','where','when','who'):
        if field in data:
            setattr(entry, field, data[field])
    db.session.commit()
    return jsonify(entry.to_dict()), 200

@brainstorm_bp.route('/<int:entry_id>', methods=['DELETE'])
def delete_brain_entry(entry_id):
    """DELETE /api/brainstorm/<id> → 删除一条 entry"""
    entry = BrainEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    return '', 204

@brainstorm_bp.route('/brainstorm/save', methods=['POST'])
def save_brainstorm_session():
    """
    POST /api/brainstorm/save
    前端 saveBrainstormSession(messages, fiveW) 调用此接口。
    这里只把 fiveW 存一条 BrainEntry，如果需要也可以存 messages、timestamp。
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

    # 如果 5W 都填写，Mock 标记 “Define Topic & Question” 完成
    if all([entry.why, entry.what, entry.where, entry.when, entry.who]):
        phase = Phase.query.filter_by(title='Define Topic & Question').first()
        if phase and not any(t.description=='Brainstorm Complete' for t in phase.tasks):
            phase.tasks.append(Task(description='Brainstorm Complete', completed=True))

    db.session.commit()
    return jsonify({'id': entry.id}), 201

@brainstorm_bp.route('/chat', methods=['POST'])
def brainstorm_chat():
    """
    POST /api/brainstorm/chat
    前端 fetchChatReply(message) 调用，返回 { reply }
    """
    data = request.get_json() or {}
    user_input = data.get('message') or data.get('content') or ''
    # TODO: 在这里接入真实 LLM；当前先返回 Mock
    reply = f"[模拟回答] 收到 Brainstorm 阶段的问题：{user_input}"
    return jsonify({'reply': reply}), 200

@brainstorm_bp.route('/progress', methods=['POST'])
def complete_brainstorm_step():
    """
    POST /api/brainstorm/progress
    前端点击 “Complete Brainstorm Step” 时调用，传 { entryId }
    当前仅返回 { status: 'ok' }
    """
    data = request.get_json() or {}
    entry_id = data.get('entryId')
    # TODO: 根据 entry_id 更新实际进度
    return jsonify({'status': 'ok'}), 200

@brainstorm_bp.route('/brainstorm/overall-feedback', methods=['POST'])
def overall_feedback():
    """
    POST /api/brainstorm/overall-feedback
    前端点击 “Generate Overall AI Feedback” 时调用，
    传 { messages, fiveW }，返回 { feedback }
    """
    data = request.get_json() or {}
    messages = data.get('messages', [])
    fiveW    = data.get('fiveW', {})
    # TODO: 调用 LLM 生成综合反馈
    mock_feedback = "✨ 这是您的整体反馈：请确保 WHY、WHAT 等都详尽清晰。"
    return jsonify({'feedback': mock_feedback}), 200

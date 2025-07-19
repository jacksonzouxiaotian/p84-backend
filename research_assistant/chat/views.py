from flask import Blueprint, request, jsonify

chat_bp = Blueprint('chat', __name__, url_prefix='/api')

@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    对应前端 fetchChatReply() 调用的 /api/chat
    """
    data = request.get_json() or {}
    user_input = data.get('message', '')
    # TODO: 在此处调用真正的 LLM 接口；目前先 Mock
    reply = f"[模拟回答] 收到消息：{user_input}"
    return jsonify({'reply': reply}), 200

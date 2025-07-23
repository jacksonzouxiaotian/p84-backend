# research_assistant/dashboard/views.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from research_assistant.planning.models import Phase

dashboard = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@dashboard.route("/phases", methods=["GET"])
@jwt_required()
def fetch_planning():
    uid = get_jwt_identity()

    # 查询用户所有阶段
    user_phases = Phase.query.filter_by(user_id=uid).all()
    user_phase_map = {p.title: p for p in user_phases}

    # 固定顺序
    desired_order = [
        'Define Topic & Question',
        'Literature Review',
        'Identify Gaps',
        'Plan Methodology',
        'Write & Revise'
    ]

    data = []
    for index, title in enumerate(desired_order):
        phase = user_phase_map.get(title)

        if phase:
            tasks = phase.tasks
            # 所有任务都完成才是 Completed，否则 NotCompleted
            if tasks and all(t.completed for t in tasks):
                status = "Completed"
            else:
                status = "NotCompleted"

            data.append({
                "id": index + 1,  # 顺序编号
                "title": phase.title,
                "status": status
            })
        else:
            # 阶段缺失 = 未完成
            data.append({
                "id": index + 1,
                "title": title,
                "status": "NotCompleted"
            })

    return jsonify({
        "code": 0,
        "data": data
    }), 200

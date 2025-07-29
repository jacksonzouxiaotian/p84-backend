from flask import Blueprint, jsonify, request

from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from research_assistant.extensions import db
from research_assistant.user.models import User
from research_assistant.dashboard.models import PhaseStatus

from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from research_assistant.dashboard.models import PhaseStatus
from research_assistant.extensions import db
from research_assistant.user.models import User


blueprint = Blueprint("user", __name__, url_prefix="/users", static_folder="../static")



@blueprint.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    """
    获取当前用户信息（需要 JWT）
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user:
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email
        }), 200
    return jsonify({"msg": "User not found"}), 404


@blueprint.route("/", methods=["GET"])
@jwt_required()
def members():

    #示例接口：列出成员（仅限登录用户）

    members_list = [
        {"id": 1, "username": "Alice"},
        {"id": 2, "username": "Bob"}
    ]
    return jsonify({
        "code": 0,
        "msg": "success",
        "data": members_list
    })


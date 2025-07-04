from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from research_assistant.extensions import db
from research_assistant.user.models import User

blueprint = Blueprint("user", __name__, url_prefix="/users", static_folder="../static")


@blueprint.route("/register", methods=["POST"])
def register():
    """
    注册用户
    """
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"msg": "Missing fields"}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"msg": "User already exists"}), 400

    user = User(username=username, email=email)
    user.password = password  # 使用加密方法设置密码
    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "Registration successful"}), 200


@blueprint.route("/login", methods=["POST"])
def login():
    """
    登录用户，返回 JWT 令牌
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200

    return jsonify({"msg": "Invalid username or password"}), 401


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


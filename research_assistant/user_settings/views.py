from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from research_assistant.extensions import db
from research_assistant.user_settings.models import UserSettings
from research_assistant.user.models import User
from research_assistant.reference.models import Reference
from research_assistant.tag.models import Tag
from research_assistant.planning.models import Phase, Task


settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.route("/", methods=["GET"])
@jwt_required()
def get_settings():
    user_id = get_jwt_identity()
    settings = UserSettings.query.filter_by(user_id=user_id).first()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if not settings:
        settings = UserSettings(user_id=user_id)
        db.session.add(settings)
        db.session.commit()

    return jsonify({
        "username": user.username,
        "email": user.email,
        **settings.to_dict()
    }), 200


@settings_bp.route("/", methods=["PUT"])
@jwt_required()
def update_settings():
    user_id = get_jwt_identity()
    data = request.get_json()
    settings = UserSettings.query.filter_by(user_id=user_id).first()

    if not settings:
        settings = UserSettings(user_id=user_id)

    if "language" in data:
        settings.language = data["language"]
    if "theme" in data:
        settings.theme = data["theme"]
    if "notifications_enabled" in data:
        settings.notifications_enabled = data["notifications_enabled"]
    if "export_format" in data:
        settings.export_format = data["export_format"]

    db.session.add(settings)
    db.session.commit()
    return jsonify({
        "message": "Settings updated",
        "settings": settings.to_dict()
    }), 200


@settings_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()

    if not username or not email:
        return jsonify({"error": "Username and email are required"}), 400

    # 检测邮箱格式（简单校验）
    if "@" not in email or "." not in email:
        return jsonify({"error": "Invalid email format"}), 400

    # 检查是否与其他用户重复（排除自己）
    existing_user = User.query.filter(User.id != user_id, User.username == username).first()
    existing_email = User.query.filter(User.id != user_id, User.email == email).first()

    if existing_user:
        return jsonify({"error": "Username already taken"}), 409
    if existing_email:
        return jsonify({"error": "Email already in use"}), 409

    user.username = username
    user.email = email

    db.session.commit()
    return jsonify({
        "message": "Profile updated",
        "username": user.username,
        "email": user.email
    }), 200



@settings_bp.route("/delete", methods=["DELETE"])
@jwt_required()
def delete_account():
    user_id = get_jwt_identity()

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    from research_assistant.reference.models import Reference
    from research_assistant.tag.models import Tag, DocumentTag
    from research_assistant.user_settings.models import UserSettings
    from sqlalchemy import text

    try:
        # 删除 phase_statuses 表中数据
        db.session.execute(text("DELETE FROM phase_statuses WHERE user_id = :uid"), {"uid": user_id})

        # 删除 DocumentTag 中间表记录
        db.session.query(DocumentTag).filter(
            DocumentTag.document_id.in_(
                db.session.query(Reference.id).filter_by(user_id=user_id)
            )
        ).delete(synchronize_session=False)

        Task.query.filter_by(user_id=user_id).delete()
        Phase.query.filter_by(user_id=user_id).delete()

        # 删除引用数据
        Reference.query.filter_by(user_id=user_id).delete()
        Tag.query.filter_by(user_id=user_id).delete()
        UserSettings.query.filter_by(user_id=user_id).delete()

        # 删除用户本身
        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "Account deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@settings_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    data = request.get_json()

    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not current_password or not new_password:
        return jsonify({"error": "Missing required fields"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.check_password(current_password):
        return jsonify({"error": "Current password is incorrect"}), 401

    # 加密新密码
    user.password = new_password
    db.session.commit()

    return jsonify({"message": "Password updated successfully"}), 200

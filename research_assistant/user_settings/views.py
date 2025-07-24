from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from research_assistant.extensions import db
from research_assistant.user_settings.models import UserSettings
from research_assistant.user.models import User

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

    if "username" in data:
        user.username = data["username"]
    if "email" in data:
        user.email = data["email"]

    db.session.commit()
    return jsonify({
        "message": "Profile updated",
        "username": user.username,
        "email": user.email
    }), 200

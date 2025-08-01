# research_assistant/user_settings/views.py

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from research_assistant.extensions import db, mail
from research_assistant.user_settings.models import UserSettings
from research_assistant.user.models import User
from research_assistant.reference.models import Reference
from research_assistant.tag.models import Tag
from research_assistant.planning.models import Phase, Task
from flask_mail import Message

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


def send_email(subject, recipients, body):
    """
    Utility function to send email notifications.
    Returns True if sent successfully, False otherwise.
    """
    try:
        msg = Message(subject=subject, recipients=recipients, body=body)
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Email sending failed: {e}")
        return False


@settings_bp.route("/", methods=["GET"])
@jwt_required()
def get_settings():
    """
    Get the user's settings and profile information.
    Create default settings if none exist.
    """
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
    """
    Update general user settings (language, theme, notifications, export format).
    """
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
    """
    Update the user's profile (username & email).
    If notifications are enabled, send an email alert.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    user = User.query.get(user_id)
    settings = UserSettings.query.filter_by(user_id=user_id).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    old_username = user.username
    old_email = user.email

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()

    if not username or not email:
        return jsonify({"error": "Username and email are required"}), 400

    # Simple email format validation
    if "@" not in email or "." not in email:
        return jsonify({"error": "Invalid email format"}), 400

    # Check for duplicates
    existing_user = User.query.filter(User.id != user_id, User.username == username).first()
    existing_email = User.query.filter(User.id != user_id, User.email == email).first()

    if existing_user:
        return jsonify({"error": "Username already taken"}), 409
    if existing_email:
        return jsonify({"error": "Email already in use"}), 409

    # Update username and email
    user.username = username
    user.email = email
    db.session.commit()

    # Send email notification if enabled
    if settings and settings.notifications_enabled:
        send_email(
            "Profile Updated",
            [user.email],
            f"Your profile has been updated.\n"
            f"Old username: {old_username}, new username: {username}\n"
            f"Old email: {old_email}, new email: {email}"
        )

    return jsonify({
        "message": "Profile updated",
        "username": user.username,
        "email": user.email
    }), 200


@settings_bp.route("/delete", methods=["DELETE"])
@jwt_required()
def delete_account():
    """
    Delete the user's account and all related data.
    If notifications are enabled, send a final account deletion email.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    settings = UserSettings.query.filter_by(user_id=user_id).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Save necessary email info BEFORE deletion
    user_email = user.email
    send_deletion_email = settings.notifications_enabled if settings else False

    from research_assistant.tag.models import DocumentTag
    from research_assistant.brain.models import BrainEntry
    from research_assistant.sections.models import Section  # Import Section model
    from sqlalchemy import text

    try:
        # ---------------------------------------------------------
        # 1. Remove data from sections first to avoid NOT NULL errors
        # ---------------------------------------------------------
        Section.query.filter_by(user_id=user_id).delete()

        # ---------------------------------------------------------
        # 2. Delete other related data
        # ---------------------------------------------------------
        db.session.execute(text("DELETE FROM phase_statuses WHERE user_id = :uid"), {"uid": user_id})

        db.session.query(DocumentTag).filter(
            DocumentTag.document_id.in_(
                db.session.query(Reference.id).filter_by(user_id=user_id)
            )
        ).delete(synchronize_session=False)

        Task.query.filter_by(user_id=user_id).delete()
        Phase.query.filter_by(user_id=user_id).delete()
        BrainEntry.query.filter_by(user_id=user_id).delete()
        Reference.query.filter_by(user_id=user_id).delete()
        Tag.query.filter_by(user_id=user_id).delete()
        UserSettings.query.filter_by(user_id=user_id).delete()

        # ---------------------------------------------------------
        # 3. Finally, delete the user record
        # ---------------------------------------------------------
        db.session.delete(user)
        db.session.commit()

        # ---------------------------------------------------------
        # 4. Send email notification AFTER deletion
        # ---------------------------------------------------------
        if send_deletion_email:
            send_email(
                "Account Deleted",
                [user_email],
                "Your account has been permanently deleted. We're sorry to see you go."
            )

        return jsonify({"message": "Account deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Account deletion failed: {e}")
        return jsonify({"error": str(e)}), 500


@settings_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    """
    Change the user's password.
    If notifications are enabled, send an email alert.
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not current_password or not new_password:
        return jsonify({"error": "Missing required fields"}), 400

    user = User.query.get(user_id)
    settings = UserSettings.query.filter_by(user_id=user_id).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.check_password(current_password):
        return jsonify({"error": "Current password is incorrect"}), 401

    # Update password
    user.password = new_password
    db.session.commit()

    # Send email notification if enabled
    if settings and settings.notifications_enabled:
        send_email(
            "Password Changed",
            [user.email],
            "Your password has been successfully changed."
        )

    return jsonify({"message": "Password updated successfully"}), 200
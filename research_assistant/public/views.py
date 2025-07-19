# -*- coding: utf-8 -*-
"""Public section, including homepage and signup (API version)."""

import random
import string

from flask import Blueprint, current_app, jsonify, request
from flask_login import login_required, login_user, logout_user
from flask_mail import Message
from flask_jwt_extended import create_access_token

from research_assistant.extensions import bcrypt, csrf_protect, db, login_manager, mail
from research_assistant.public.forms import LoginForm
from research_assistant.user.forms import RegisterForm
from research_assistant.user.models import EmailCaptcha, User

blueprint = Blueprint("public", __name__, static_folder="../static")


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route("/", methods=["GET"])
def home():
    """
    API endpoint for service health check or greeting.
    """
    current_app.logger.info("Hello from the home page (API)!")
    return jsonify({
        "code": 0,
        "msg": "API service is running",
        "data": {}
    })


@blueprint.route("/login/", methods=["POST"])
def login():
    """
    API endpoint for user login.
    Accepts JSON body: { "email": "", "password": "" }
    Returns authentication status plus JWT token.
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"code": 400, "msg": "Missing JSON data"}), 400

    form = LoginForm(data=json_data)
    if form.validate():
        login_user(form.user)
        # generate JWT
        access_token = create_access_token(identity=str(form.user.id))
        return jsonify({
            "code": 0,
            "msg": "Login successful",
            "data": {
                "user_id": form.user.id,
                "username": form.user.username,
                "access_token": access_token
            }
        })
    else:
        errors = [f"{field}: {','.join(errs)}" for field, errs in form.errors.items()]
        return jsonify({
            "code": 401,
            "msg": "Login failed",
            "errors": errors
        }), 401


@blueprint.route("/logout/", methods=["POST"])
@login_required
def logout():
    """
    API endpoint for logging out the current user.
    """
    logout_user()
    return jsonify({
        "code": 0,
        "msg": "Logout successful"
    })


@blueprint.route("/register/", methods=["POST"])
def register():
    """
    API endpoint for new user registration.
    Accepts JSON body: { "username": "", "email": "", "password": "" }
    Returns registration result and initializes default PhaseStatus entries.
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"code": 400, "msg": "Missing JSON data"}), 400

    form = RegisterForm(data=json_data)
    if form.validate():
        # create user
        user = User.create(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            active=True,
        )
        # add to session so we can use user.id
        db.session.add(user)
        db.session.flush()

        # deferred import to avoid circular dependency
        from research_assistant.dashboard.models import PhaseStatus

        # initialize default phases
        titles = ["选题", "文献阅读", "研究设计", "撰写报告", "提交成果"]
        for i, title in enumerate(titles, start=1):
            phase = PhaseStatus(
                user_id=user.id,
                phase_number=i,
                title=title,
                status="NotCompleted"
            )
            db.session.add(phase)

        db.session.commit()
        return jsonify({
            "code": 0,
            "msg": "Registration successful, you can now log in."
        })
    else:
        errors = [f"{field}: {','.join(errs)}" for field, errs in form.errors.items()]
        return jsonify({
            "code": 400,
            "msg": "Registration failed",
            "errors": errors
        }), 400


@blueprint.route("/about/", methods=["GET"])
def about():
    """
    API endpoint for service/about information.
    """
    return jsonify({
        "code": 0,
        "msg": "About this API service",
        "data": {
            "version": "1.0.0",
            "description": "Research Assistant API"
        }
    })


@csrf_protect.exempt
@blueprint.route("/captcha/email/", methods=["GET", "POST"])
def send_email_captcha():
    """
    Request an email verification code.
    Expected JSON body or query: {"email": "user@example.com"}
    """
    email = (request.args.get("email")
             if request.method == "GET"
             else (request.get_json() or {}).get("email"))
    if not email:
        return jsonify({"code": 400, "message": "Email is required"}), 400

    code = "".join(random.choices(string.digits, k=6))
    try:
        msg = Message(
            subject="[Research Assistant] Verification Code",
            recipients=[email],
            body=f"Your code is: {code}. Valid for 10 minutes."
        )
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {e}")
        return jsonify({"code": 500, "message": "Failed to send email"}), 500

    cap = EmailCaptcha(email=email, captcha=code)
    db.session.add(cap)
    db.session.commit()
    return jsonify({"code": 200, "message": "Verification code sent successfully"})


@csrf_protect.exempt
@blueprint.route("/password/reset/", methods=["POST"])
def reset_password():
    """
    Reset user password.
    Expected JSON body:
    {
      "email": "...",
      "captcha": "...",
      "new_password": "..."
    }
    """
    data = request.get_json() or {}
    email = data.get("email")
    captcha = data.get("captcha")
    new_password = data.get("new_password")

    if not all([email, captcha, new_password]):
        return jsonify({
            "code": 400,
            "message": "Email, captcha, and new_password are all required"
        }), 400

    record = (
        EmailCaptcha.query
                    .filter_by(email=email, captcha=captcha)
                    .order_by(EmailCaptcha.created_at.desc())
                    .first()
    )
    if not record:
        return jsonify({"code": 400, "message": "Invalid or expired captcha"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"code": 404, "message": "Email not registered"}), 404

    user.password = new_password  # or bcrypt.generate_password_hash(...)
    db.session.commit()
    return jsonify({"code": 200, "message": "Password reset successfully"})

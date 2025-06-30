from flask import Blueprint, jsonify, request
from flask_login import login_user, logout_user, login_required
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

    user = User(username=username, email=email, password=password, active=True)
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "Registration successful"}), 200


@blueprint.route("/login", methods=["POST"])
def login():
    """
    登录用户
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)  # Flask-Login 登录
        return jsonify({"msg": "Login successful"}), 200
    return jsonify({"msg": "Invalid username or password"}), 401


@blueprint.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"msg": "Logged out"}), 200


@blueprint.route("/")
@login_required
def members():
    """
    API endpoint to list members.
    """
    # Replace with real database query if needed
    members_list = [
        {"id": 1, "username": "Alice"},
        {"id": 2, "username": "Bob"}
    ]
    return jsonify({
        "code": 0,
        "msg": "success",
        "data": members_list
    })


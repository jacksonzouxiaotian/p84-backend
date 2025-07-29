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



from flask import Blueprint, jsonify
from flask_login import login_required

blueprint = Blueprint("user", __name__, url_prefix="/users", static_folder="../static")

@blueprint.route("/")
@login_required
def members():
    """
    API endpoint to list members.
    Returns a JSON object with member information.
    """
    # Example data; replace with your actual database query
    # users = User.query.all()
    # members_list = [{"id": u.id, "username": u.username} for u in users]
    members_list = [
        {"id": 1, "username": "Alice"},
        {"id": 2, "username": "Bob"}
    ]
    return jsonify({
        "code": 0,             # 0 indicates success
        "msg": "success",      # Message for frontend
        "data": members_list   # The actual member list data
    })

# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from research_assistant.dashboard.forms import PhaseStatusForm
from research_assistant.dashboard.models import PhaseStatus
from research_assistant.extensions import db

dashboard = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard.route("/phases", methods=["GET"])
@jwt_required()
def get_my_phases():
    user_id = get_jwt_identity()
    phases = PhaseStatus.query.filter_by(user_id=user_id).order_by(PhaseStatus.phase_number).all()
    data = [
        {
            "id": p.id,
            "phase_number": p.phase_number,
            "title": p.title,
            "status": p.status
        } for p in phases
    ]
    return jsonify({"code": 0, "data": data})


@dashboard.route("/phases", methods=["POST"])
@jwt_required()
def create_phase():
    user_id = get_jwt_identity()
    json_data = request.get_json()
    form = PhaseStatusForm(data=json_data)

    if form.validate():
        ps = PhaseStatus(
            user_id=user_id,
            phase_number=form.phase_number.data,
            title=form.title.data,
            status=form.status.data
        )
        db.session.add(ps)
        db.session.commit()
        return jsonify({"code": 0, "msg": "Phase status created successfully"})
    else:
        return jsonify({"code": 1, "msg": "Validation failed", "errors": form.errors}), 400


@dashboard.route("/phases/number/<int:phase_number>/status", methods=["PUT"])
@jwt_required()
def update_my_phase_by_number(phase_number):
    user_id = get_jwt_identity()
    json_data = request.get_json()
    new_status = json_data.get("status")

    if new_status not in ["Completed", "NotCompleted"]:
        return jsonify({"code": 1, "msg": "Failed to update phase status"}), 400

    phase = PhaseStatus.query.filter_by(user_id=user_id, phase_number=phase_number).first_or_404()

    phase.status = new_status
    db.session.commit()

    return jsonify({"code": 0, "msg": "Status updated"})


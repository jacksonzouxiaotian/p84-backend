from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from research_assistant.reference.models import Reference
from research_assistant.extensions import db
from research_assistant.reference.citation_styles import generate_citation

bp = Blueprint("reference", __name__, url_prefix="/api/references")

@bp.route("/", methods=["POST"])
@jwt_required()
def add_reference():
    data = request.get_json()
    title = data.get("title")
    authors = data.get("authors")
    year = data.get("year")
    source = data.get("source")
    user_id = get_jwt_identity()

    if not title or not authors or not year:
        return jsonify({"error": "Missing fields"}), 400

    ref = Reference(
        title=title,
        authors=authors,
        year=year,
        source=source,
        user_id=user_id
    )
    db.session.add(ref)
    db.session.commit()
    return jsonify(ref.to_dict()), 201

@bp.route("/", methods=["GET"])
@jwt_required()
def list_references():
    user_id = get_jwt_identity()
    sort_by = request.args.get("sort_by", "created_at")
    refs = Reference.query.filter_by(user_id=user_id).order_by(getattr(Reference, sort_by)).all()
    return jsonify([ref.to_dict() for ref in refs])

@bp.route("/<int:ref_id>", methods=["PUT"])
@jwt_required()
def update_reference(ref_id):
    ref = Reference.query.get_or_404(ref_id)
    if ref.user_id != get_jwt_identity():
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    for field in ["title", "authors", "year", "source"]:
        if field in data:
            setattr(ref, field, data[field])

    db.session.commit()
    return jsonify(ref.to_dict())

@bp.route("/<int:ref_id>", methods=["DELETE"])
@jwt_required()
def delete_reference(ref_id):
    ref = Reference.query.get_or_404(ref_id)
    if ref.user_id != get_jwt_identity():
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(ref)
    db.session.commit()
    return jsonify({"msg": "Deleted successfully"})

@bp.route("/<int:ref_id>/cite", methods=["GET"])
@jwt_required()
def generate_citation_api(ref_id):
    style = request.args.get("style", "APA")  # APA / MLA / Chicago
    ref = Reference.query.get_or_404(ref_id)
    if ref.user_id != get_jwt_identity():
        return jsonify({"error": "Unauthorized"}), 403

    citation = generate_citation(ref, style)
    return jsonify({"citation": citation})

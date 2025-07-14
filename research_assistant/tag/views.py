from flask import Blueprint, request, jsonify
from research_assistant.extensions import db
from research_assistant.tag.models import Tag, Document, DocumentTag

blueprint = Blueprint("tag", __name__, url_prefix="/tags")

@blueprint.route("/", methods=["POST"])
def add_tag():
    data = request.get_json()
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Tag name required"}), 400

    tag = Tag.query.filter_by(name=name).first()
    if not tag:
        tag = Tag(name=name)
        db.session.add(tag)
        db.session.commit()

    return jsonify({"id": tag.id, "name": tag.name}), 200

@blueprint.route("/list", methods=["GET"])
def list_tags():
    tags = Tag.query.all()
    return jsonify([{"id": t.id, "name": t.name} for t in tags])

@blueprint.route("/stats", methods=["GET"])
def tag_stats():
    result = db.session.query(
        Tag.name, db.func.count(DocumentTag.id).label("count")
    ).join(DocumentTag, Tag.id == DocumentTag.tag_id) \
     .group_by(Tag.name).all()

    return jsonify([{"tag": name, "count": count} for name, count in result])

@blueprint.route("/assign", methods=["POST"])
def assign_tag():
    data = request.get_json()
    doc_id = data.get("document_id")
    tag_name = data.get("tag")

    if not doc_id or not tag_name:
        return jsonify({"error": "Missing document_id or tag"}), 400

    document = Document.query.get(doc_id)
    if not document:
        return jsonify({"error": "Document not found"}), 404

    tag = Tag.query.filter_by(name=tag_name).first()
    if not tag:
        tag = Tag(name=tag_name)
        db.session.add(tag)
        db.session.flush()

    if tag not in document.tags:
        document.tags.append(tag)

    db.session.commit()
    return jsonify({"msg": f"Tag '{tag.name}' assigned to Document '{document.title}'"}), 200

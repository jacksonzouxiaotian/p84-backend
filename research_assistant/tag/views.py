from flask import Blueprint, jsonify, request 
from research_assistant.extensions import db
from research_assistant.reference.models import Reference as Document 
from research_assistant.tag.models import DocumentTag, Tag
from flask_jwt_extended import jwt_required, get_jwt_identity

blueprint = Blueprint("tag", __name__, url_prefix="/tags")

# 创建标签（如果已存在则返回）
@blueprint.route("/", methods=["POST"])
@jwt_required()
def add_tag():
    user_id = get_jwt_identity()
    data = request.get_json()
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Tag name required"}), 400

    tag = Tag.query.filter_by(name=name, user_id=user_id).first()
    if not tag:
        tag = Tag(name=name, user_id=user_id)
        db.session.add(tag)
        db.session.commit()

    return jsonify({"id": tag.id, "name": tag.name}), 200


# 获取所有标签
@blueprint.route("/list", methods=["GET"])
@jwt_required()
def list_tags():
    user_id = get_jwt_identity()
    tags = Tag.query.filter_by(user_id=user_id).all()
    return jsonify([{"id": t.id, "name": t.name} for t in tags])


# 获取标签统计信息（每个标签使用次数）
@blueprint.route("/stats", methods=["GET"])
@jwt_required()
def tag_stats():
    user_id = get_jwt_identity()
    result = db.session.query(
        Tag.name, db.func.count(DocumentTag.id).label("count")
    ).join(DocumentTag, Tag.id == DocumentTag.tag_id) \
     .filter(Tag.user_id == user_id) \
     .group_by(Tag.name).all()

    return jsonify([{"tag": name, "count": count} for name, count in result])


# 为文档添加标签（如果标签不存在则创建）
@blueprint.route("/assign", methods=["POST"])
@jwt_required()
def assign_tag():
    user_id = get_jwt_identity()
    data = request.get_json()
    doc_id = data.get("document_id")
    tag_name = data.get("tag")

    if not doc_id or not tag_name:
        return jsonify({"error": "Missing document_id or tag"}), 400

    document = Document.query.get(doc_id)
    if not document or document.user_id != user_id:
        return jsonify({"error": "Document not found or unauthorized"}), 404

    tag = Tag.query.filter_by(name=tag_name, user_id=user_id).first()
    if not tag:
        tag = Tag(name=tag_name, user_id=user_id)
        db.session.add(tag)
        db.session.flush()

    if tag not in document.tags:
        document.tags.append(tag)

    db.session.commit()
    return jsonify({"msg": f"Tag '{tag.name}' assigned to Document '{document.title}'"}), 200


# 获取所有文档及其标签
@blueprint.route("/all-docs-with-tags", methods=["GET"])
@jwt_required()
def get_all_docs_with_tags():
    user_id = get_jwt_identity()
    docs = Document.query.filter_by(user_id=user_id).all()
    result = []
    for doc in docs:
        result.append({
            "id": doc.id,
            "title": doc.title,
            "completed": doc.completed,
            "tags": [{"id": tag.id, "name": tag.name} for tag in doc.tags if tag.user_id == user_id]
        })
    return jsonify(result), 200


# 删除某文档上的某个标签
@blueprint.route("/remove", methods=["DELETE"])
@jwt_required()
def remove_tag_from_document():
    user_id = get_jwt_identity()
    data = request.get_json()
    doc_id = data.get("document_id")
    tag_id = data.get("tag_id")

    document = Document.query.get(doc_id)
    tag = Tag.query.get(tag_id)

    if not document or document.user_id != user_id or not tag or tag.user_id != user_id:
        return jsonify({"error": "Unauthorized or not found"}), 404

    if tag in document.tags:
        document.tags.remove(tag)
        db.session.commit()
        return jsonify({"msg": f"Tag '{tag.name}' removed from document '{document.title}'"}), 200

    return jsonify({"error": "Tag was not assigned to the document"}), 400


# 设置文档完成或未完成状态
@blueprint.route("/mark-complete", methods=["POST"])
@jwt_required()
def mark_document_complete():
    user_id = get_jwt_identity()
    data = request.get_json()
    doc_id = data.get("document_id")
    completed = data.get("completed")

    document = Document.query.get(doc_id)
    if not document or document.user_id != user_id:
        return jsonify({"error": "Document not found or unauthorized"}), 404

    document.completed = completed
    db.session.commit()
    return jsonify({"msg": f"Document marked as {'completed' if completed else 'incomplete'}"}), 200


# 修改标签名称
@blueprint.route("/update", methods=["PUT"])
@jwt_required()
def update_tag_name():
    user_id = get_jwt_identity()
    data = request.get_json()
    tag_id = data.get("tag_id")
    new_name = data.get("new_name", "").strip()

    if not tag_id or not new_name:
        return jsonify({"error": "Tag ID and new name required"}), 400

    tag = Tag.query.get(tag_id)
    if not tag or tag.user_id != user_id:
        return jsonify({"error": "Tag not found or unauthorized"}), 404

    tag.name = new_name
    db.session.commit()
    return jsonify({"msg": f"Tag renamed to '{new_name}'"}), 200


# 删除标签（整个标签及其关联）
@blueprint.route("/delete", methods=["DELETE"])
@jwt_required()
def delete_tag():
    user_id = get_jwt_identity()
    data = request.get_json()
    tag_id = data.get("tag_id")

    tag = Tag.query.get(tag_id)
    if not tag or tag.user_id != user_id:
        return jsonify({"error": "Tag not found or unauthorized"}), 404

    for doc in tag.documents:
        if tag in doc.tags:
            doc.tags.remove(tag)

    db.session.delete(tag)
    db.session.commit()
    return jsonify({"msg": f"Tag '{tag.name}' deleted"}), 200

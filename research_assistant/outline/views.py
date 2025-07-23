from datetime import datetime
from flask import Blueprint, jsonify, request, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import cross_origin

from research_assistant.extensions import db, csrf_protect
from research_assistant.outline.models import Section

outline_bp = Blueprint('outline', __name__)

def _recreate_sections(items, user_id, parent_id=None):
    """
    递归重建当前用户的 Section 树。
    items 是 [{ title, summary?, subsections: [...] }, …]
    """
    for idx, item in enumerate(items):
        sec = Section(
            title      = item['title'],
            summary    = item.get('summary'),
            parent_id  = parent_id,
            order      = idx,
            created_at = datetime.utcnow(),
            user_id    = user_id,
        )
        db.session.add(sec)
        db.session.flush()
        for child in item.get('subsections', []):
            _recreate_sections([child], user_id, parent_id=sec.id)

@outline_bp.route('/outline/get', methods=['GET'])
@outline_bp.route('/outline/get/<int:sec_id>', methods=['GET'])
@jwt_required()
def get_outline(sec_id=None):
    uid = get_jwt_identity()

    if sec_id is None:
        roots = (
            Section.query
            .filter_by(parent_id=None, user_id=uid)
            .order_by(Section.order)
            .all()
        )
        data = [sec.to_dict() for sec in roots]
    else:
        sec = (
            Section.query
            .filter_by(id=sec_id, user_id=uid)
            .first_or_404()
        )
        data = sec.to_dict()

    return jsonify({'success': True, 'data': data}), 200

@outline_bp.route('/outline/save', methods=['OPTIONS', 'POST'])
@cross_origin(origins='http://localhost:5173', methods=['POST','OPTIONS'])
@csrf_protect.exempt
@jwt_required()
def save_outline():
    if request.method == 'OPTIONS':
        return make_response('', 200)

    payload = request.get_json() or {}
    outline = payload.get('outline', [])
    if not outline:
        return jsonify({'success': False, 'message': '不能保存空的大纲！'}), 400

    uid = get_jwt_identity()
    # 只删除当前用户的
    Section.query.filter_by(user_id=uid).delete()
    db.session.commit()

    # 重建
    _recreate_sections(outline, user_id=uid)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Outline saved'}), 201

@outline_bp.route('/update/<int:sec_id>', methods=['PUT'])
@jwt_required()
def update_outline(sec_id):
    uid = get_jwt_identity()
    sec = Section.query.filter_by(id=sec_id, user_id=uid).first_or_404()

    data = (request.get_json() or {}).get('outline', {})
    for field in ('title', 'summary', 'order'):
        if field in data:
            setattr(sec, field, data[field])
    db.session.commit()

    return jsonify({'success': True, 'message': 'Updated', 'data': sec.to_dict()}), 200

@outline_bp.route('/delete/<int:sec_id>', methods=['DELETE'])
@jwt_required()
def delete_outline(sec_id):
    uid = get_jwt_identity()
    sec = Section.query.filter_by(id=sec_id, user_id=uid).first_or_404()
    db.session.delete(sec)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Deleted'}), 204

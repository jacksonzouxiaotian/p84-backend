# research_assistant/outline/views.py

from datetime import datetime
from flask import Blueprint, jsonify, request, make_response
from flask_cors import cross_origin

from research_assistant.extensions import db, csrf_protect
from research_assistant.outline.models import Section

outline_bp = Blueprint('outline', __name__)


def _recreate_sections(items, parent_id=None):
    """
    递归重建 Section 树结构。
    items 是 [{ id?, title, summary?, subsections: [...] }, …]
    """
    for idx, item in enumerate(items):
        sec = Section(
            title      = item['title'],
            summary    = item.get('summary'),
            parent_id  = parent_id,
            order      = idx,
            created_at = datetime.utcnow()
        )
        db.session.add(sec)
        db.session.flush()  # sec.id 可用
        # 递归创建子节点
        subsecs = item.get('subsections') or []
        _recreate_sections(subsecs, parent_id=sec.id)


@outline_bp.route('/outline/get', methods=['GET'])
@outline_bp.route('/outline/get/<int:sec_id>', methods=['GET'])
def get_outline(sec_id=None):
    """
    GET /api/outline/get      → 返回整个大纲树
    GET /api/outline/get/123  → 返回单个 Section
    """
    if sec_id is None:
        roots = Section.query.filter_by(parent_id=None).order_by(Section.order).all()
        data = [sec.to_dict() for sec in roots]
    else:
        sec = Section.query.get_or_404(sec_id)
        data = sec.to_dict()
    return jsonify({'success': True, 'data': data}), 200


@outline_bp.route('/outline/save', methods=['OPTIONS', 'POST'])
@cross_origin(origins='http://localhost:5173', methods=['POST','OPTIONS'])
@csrf_protect.exempt
def save_outline():
    """
    同时处理 CORS 预检（OPTIONS）和保存 POST。
    POST /api/outline/save
    Body: { outline: […], timestamp: “…ISO time…” }
    清空旧数据，重建 Section 树。
    """
    # 预检请求直接返回空响应，flask-cors 会自动加上 Access-Control-Allow-* 头
    if request.method == 'OPTIONS':
        return make_response('', 200)

    payload = request.get_json() or {}
    outline = payload.get('outline', [])
    if not outline:  # 如果为空，可以选择不覆盖
        return jsonify({'success': False, 'message': '不能保存空的大纲！'}), 400
    # 删除所有旧的 Section
    Section.query.delete()
    db.session.commit()
    print("收到保存请求：", request.json)
    print('收到的 outline:', outline)

    # 重新创建树形结构
    _recreate_sections(outline)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Outline saved'}), 201


@outline_bp.route('/outline/update/<int:sec_id>', methods=['PUT'])
def update_outline(sec_id):
    """
    PUT /api/outline/update/<sec_id>
    Body: { outline: { title?, summary?, order? } }
    """
    sec = Section.query.get_or_404(sec_id)
    data = request.get_json() or {}
    for field in ('title', 'summary', 'order'):
        if field in data.get('outline', {}):
            setattr(sec, field, data['outline'][field])
    db.session.commit()
    return jsonify({'success': True, 'message': 'Updated', 'data': sec.to_dict()}), 200


@outline_bp.route('/outline/delete/<int:sec_id>', methods=['DELETE'])
def delete_outline(sec_id):
    """
    DELETE /api/outline/delete/<sec_id>
    """
    sec = Section.query.get_or_404(sec_id)
    db.session.delete(sec)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Deleted'}), 204

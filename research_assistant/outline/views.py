# research_assistant/outline/views.py

from datetime import datetime

from flask import Blueprint, Response, jsonify, request

from research_assistant.extensions import db
from research_assistant.outline.models import Section
from research_assistant.planning.models import Phase, Task

outline_bp = Blueprint('outline', __name__, url_prefix='/api/outline')

@outline_bp.route('/', methods=['GET'])
def list_sections():
    """GET /api/outline/ → [ {id,title,summary,order,subsections: [...]}, ... ]"""
    roots = (
        Section.query
        .filter_by(parent_id=None)
        .order_by(Section.order)
        .all()
    )
    return jsonify([sec.to_dict() for sec in roots]), 200


@outline_bp.route('/', methods=['POST'])
def create_section():
    """
    POST /api/outline/ { title, summary?, parent_id?, order? }
      → 创建一个 Section，返回其 to_dict()
    """
    data = request.get_json() or {}
    sec = Section(
        title     = data['title'],
        summary   = data.get('summary'),
        parent_id = data.get('parent_id'),
        order     = data.get('order', 0),
        created_at= datetime.utcnow()
    )
    db.session.add(sec)
    db.session.commit()
    return jsonify(sec.to_dict()), 201


@outline_bp.route('/<int:sec_id>', methods=['PUT'])
def update_section(sec_id):
    """
    PUT /api/outline/<sec_id> { title?, summary?, parent_id?, order? }
      → 更新字段，返回更新后的 to_dict()
    """
    sec = Section.query.get_or_404(sec_id)
    data = request.get_json() or {}

    # 只更新前端传过来的字段
    for field in ('title', 'summary', 'parent_id', 'order'):
        if field in data:
            setattr(sec, field, data[field])

    db.session.commit()
    return jsonify(sec.to_dict()), 200


@outline_bp.route('/<int:sec_id>', methods=['DELETE'])
def delete_section(sec_id):
    """
    DELETE /api/outline/<sec_id> → 删除该 Section（及其所有子节点，因 cascade）
    """
    sec = Section.query.get_or_404(sec_id)
    db.session.delete(sec)
    db.session.commit()
    return '', 204


@outline_bp.route('/export/plain', methods=['GET'])
def export_plain():
    """
    GET /api/outline/export/plain → text/plain
    将整个大纲按缩进文本格式导出
    """
    roots = (
        Section.query
        .filter_by(parent_id=None)
        .order_by(Section.order)
        .all()
    )

    def to_plain(sections, level=0):
        lines = []
        for sec in sorted(sections, key=lambda x: x.order):
            indent = '  ' * level
            lines.append(f"{indent}- {sec.title}")
            if sec.summary:
                lines.append(f"{indent}  {sec.summary}")
            if sec.subsections:
                lines.extend(to_plain(sec.subsections, level+1))
        return lines

    text = "\n".join(to_plain(roots))
    return Response(text, mimetype='text/plain'), 200


@outline_bp.route('/export', methods=['GET'])
def export_markdown():
    """
    GET /api/outline/export → text/markdown
    将整个大纲导出为 Markdown（#、##、###...）
    """
    roots = (
        Section.query
        .filter_by(parent_id=None)
        .order_by(Section.order)
        .all()
    )

    def to_md(sections, level=1):
        md = []
        for sec in sorted(sections, key=lambda x: x.order):
            md.append(f"{'#' * level} {sec.title}")
            if sec.summary:
                md.append(f"{sec.summary}")
            if sec.subsections:
                md.extend(to_md(sec.subsections, level+1))
        return md

    md_lines = to_md(roots)
    md_text = "\n\n".join(md_lines)
    return Response(md_text, mimetype='text/markdown'), 200


@outline_bp.route('/complete', methods=['POST'])
def complete_outline():
    """
    POST /api/outline/complete → 手动标记
    将 “Methodology / Structural Planning” 阶段下，
    自动添加一个已完成的 Task，并 commit
    """
    phase = Phase.query.filter_by(title='Methodology / Structural Planning').first()
    if phase:
        # 避免重复添加
        exists = any(t.description == 'Outline Complete' for t in phase.tasks)
        if not exists:
            phase.tasks.append(Task(description='Outline Complete', completed=True))
            db.session.commit()
    return '', 204


@outline_bp.route('/chat', methods=['POST'])
def outline_chat():
    """
    POST /api/outline/chat { content: '用户输入...' }
      → Mock AI 接口，仅回 echo
    """
    data = request.get_json() or {}
    user_q = data.get('content', '')
    # TODO: 接入真正的 LLM 服务
    reply = f"[模拟回答] 收到 Outline 阶段的问题：{user_q}"
    return jsonify({'reply': reply}), 200

from flask import Blueprint, request, jsonify
from research_assistant.extensions import db
from research_assistant.outline.models import Section
from flask import Response
from research_assistant.planning.models import Phase, Task

outline_bp = Blueprint('outline', __name__, url_prefix='/api/outline')

@outline_bp.route('/', methods=['GET'])
def get_outline():
    roots = Section.query.filter_by(parent_id=None).order_by(Section.order).all()
    return jsonify([sec.to_dict() for sec in roots]), 200
@outline_bp.route('/export/plain', methods=['GET'])
def export_outline_plain():
    roots = Section.query.filter_by(parent_id=None).order_by(Section.order).all()
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
def export_outline():
    """导出整个大纲为 Markdown 文本"""
    roots = Section.query.filter_by(parent_id=None).order_by(Section.order).all()

    def to_md(sections, level=1):
        lines = []
        for sec in sorted(sections, key=lambda x: x.order):
            # 一级标题用 '# '，二级用 '## '，以此类推
            lines.append(f"{'#' * level} {sec.title}")
            if sec.summary:
                lines.append(sec.summary)
            # 递归处理子章节
            if sec.subsections:
                lines.extend(to_md(sec.subsections, level + 1))
        return lines

    md_lines = to_md(roots)
    md_text = "\n\n".join(md_lines)
    return Response(md_text, mimetype='text/markdown'), 200
@outline_bp.route('/', methods=['POST'])
def create_section():
    data = request.get_json() or {}
    sec = Section(
        title=data['title'],
        summary=data.get('summary'),
        parent_id=data.get('parent_id'),
        order=data.get('order', 0),
    )
    db.session.add(sec)
    db.session.commit()
    return jsonify(sec.to_dict()), 201

@outline_bp.route('/<int:sec_id>', methods=['PUT'])
def update_section(sec_id):
    sec = Section.query.get_or_404(sec_id)
    data = request.get_json() or {}
    for field in ('title','summary','parent_id','order'):
        if field in data:
            setattr(sec, field, data[field])
    db.session.commit()
    return jsonify(sec.to_dict()), 200

@outline_bp.route('/<int:sec_id>', methods=['DELETE'])
def delete_section(sec_id):
    sec = Section.query.get_or_404(sec_id)
    db.session.delete(sec)
    db.session.commit()
    return '', 204
@outline_bp.route('/complete', methods=['POST'])
def complete_outline():
    """手动标记 Structural Planning 阶段完成"""
    phase = Phase.query.filter_by(title='Methodology / Structural Planning').first()
    if phase:
        phase.tasks.append(Task(description='Outline Complete', completed=True))
        db.session.commit()
    return '', 204

@outline_bp.route('/chat', methods=['POST'])
def outline_chat():
    """Mock AI 聊天接口"""
    data = request.get_json() or {}
    return jsonify({
        'reply': f"[模拟回答] 收到 Outline 阶段的问题：{data.get('content')}"
    }), 200
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from research_assistant.reference.models import Reference
from research_assistant.extensions import db

from io import BytesIO
from docx import Document
from docx.shared import Pt

bp = Blueprint("reference", __name__, url_prefix="/references")

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
    user_id = int(get_jwt_identity())
    sort_by = request.args.get("sort_by", "created_at")
    refs = Reference.query.filter_by(user_id=user_id).order_by(getattr(Reference, sort_by)).all()
    return jsonify([ref.to_dict() for ref in refs])

@bp.route("/<int:ref_id>", methods=["PUT"])
@jwt_required()
def update_reference(ref_id):
    ref = Reference.query.get_or_404(ref_id)
  
    if ref.user_id != int(get_jwt_identity()):
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
    if ref.user_id != int(get_jwt_identity()):
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(ref)
    db.session.commit()
    return jsonify({"msg": "Deleted successfully"})

@bp.route("/<int:ref_id>/cite", methods=["GET"])
@jwt_required()
def generate_citation_api(ref_id):
    """
    生成 .docx 引文文件并触发浏览器下载。
    目前示例实现 APA（期刊）；style 参数保留用于扩展（MLA/Chicago）。
    """
    style = request.args.get("style", "APA").upper()
    ref = Reference.query.get_or_404(ref_id)
    if ref.user_id != int(get_jwt_identity()):
        return jsonify({"error": "Unauthorized"}), 403

    # 如果需要将 source 标准化为 journal，请在落库（.bib 解析处）完成；
    # 这里仅按期刊条目生成（不强行改库）。
    if style == "APA":
        file_bytes, download_name = build_docx_apa_journal(ref)
    else:
        # 其他样式未实现时可先退回 APA
        file_bytes, download_name = build_docx_apa_journal(ref)

    return send_file(
        file_bytes,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        as_attachment=True,
        download_name=download_name,
        max_age=0,
    )


# ========= 生成 docx 的辅助函数 =========

def build_docx_apa_journal(ref):
    """
    依据 ref 生成一条 APA 期刊文献到 .docx。
    需要字段（按你模型实际字段名调整）：
      ref.authors: "Smith, J.; Wang, L." 或列表
      ref.year: "2021"
      ref.title: 文章标题（不斜体）
      ref.journal: 期刊名（斜体）
      ref.volume: 卷（斜体）
      ref.issue: 期（不斜体，括号）
      ref.pages: 页码（不斜体）
      ref.doi / ref.url: 可选
    """
    doc = Document()
    normal = doc.styles["Normal"]
    normal.font.size = Pt(11)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)

    # Authors
    authors_text = format_authors_apa(getattr(ref, "authors", ""))
    if authors_text:
        add_run(p, authors_text + " ")

    # (Year).
    year = getattr(ref, "year", None)
    if year:
        add_run(p, f"({year}). ")

    # Title.
    title = getattr(ref, "title", "")
    if title:
        add_run(p, f"{title}. ")

    # Journal, Volume(Issue), pages.
    journal = getattr(ref, "journal", "")
    volume  = getattr(ref, "volume", "")
    issue   = getattr(ref, "issue", "")
    pages   = getattr(ref, "pages", "")

    if journal:
        add_run(p, journal, italic=True)   # 期刊名斜体
        add_run(p, ", ")
    if volume:
        add_run(p, str(volume), italic=True)  # 卷斜体
    if issue:
        add_run(p, f"({issue})")              # 期不斜体
    if pages:
        add_run(p, f", {pages}")
    add_run(p, ".")

    # DOI/URL
    doi = getattr(ref, "doi", "") or getattr(ref, "url", "")
    if doi:
        add_run(p, f" https://doi.org/{strip_doi_prefix(doi)}")

    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)

    # 下载名：FirstAuthor_Year_APA.docx
    first_author = extract_first_author(authors_text)
    year_str = str(year or "")
    name = f"{first_author}_{year_str}_APA.docx".strip("_").replace("__", "_")
    safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in name)
    return bio, (safe or "citation_APA.docx")


def add_run(paragraph, text, italic=False):
    r = paragraph.add_run(text)
    if italic:
        r.italic = True
    return r


def format_authors_apa(authors):
    """
    将作者格式化为 APA 串：
      1人：A
      2人：A & B
      ≥3人：A, B, & C
    这里假设 authors 是 ';' 分隔的 'Lastname, F.'，或一个列表。
    """
    if not authors:
        return ""
    if isinstance(authors, str):
        items = [a.strip() for a in authors.split(";") if a.strip()]
    elif isinstance(authors, (list, tuple)):
        items = [str(a).strip() for a in authors if str(a).strip()]
    else:
        return str(authors)

    n = len(items)
    if n == 0:
        return ""
    if n == 1:
        return items[0]
    if n == 2:
        return f"{items[0]} & {items[1]}"
    return f"{', '.join(items[:-1])}, & {items[-1]}"


def strip_doi_prefix(doi: str) -> str:
    doi = (doi or "").strip()
    for pref in ("https://doi.org/", "http://doi.org/", "doi:", "DOI:"):
        if doi.lower().startswith(pref):
            return doi[len(pref):]
    return doi


def extract_first_author(authors_text: str) -> str:
    if not authors_text:
        return "citation"
    # 取第一个作者的姓（以逗号前为姓）
    first = authors_text.split("&")[0].split(",")[0].split(",")[0].strip()
    # 去掉可能的尾部逗号
    return first or "citation"
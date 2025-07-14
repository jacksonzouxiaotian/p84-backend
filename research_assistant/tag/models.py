from research_assistant.database import Column, PkModel, db, reference_col, relationship

class Tag(PkModel):
    __tablename__ = "tags"

    name = Column(db.String(64), unique=True, nullable=False)

    def __repr__(self):
        return f"<Tag({self.name})>"

class Document(PkModel):
    """
    示例文献模型，可与 BibTeX 导入结合使用。
    你可以根据项目需要扩展字段（如 author, year, bibkey）
    """
    __tablename__ = "documents"

    title = Column(db.String(256), nullable=False)
    user_id = reference_col("users")  # 和现有 User 模型对接
    created_at = Column(db.DateTime, default=db.func.now())

    tags = relationship("Tag", secondary="document_tags", backref="documents")

    def __repr__(self):
        return f"<Document({self.title})>"

class DocumentTag(db.Model):
    __tablename__ = "document_tags"

    id = db.Column(db.Integer, primary_key=True)
    document_id = reference_col("documents")
    tag_id = reference_col("tags")

from research_assistant.database import Column, PkModel, db, reference_col, relationship
from research_assistant.reference.models import Reference

class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

    documents = relationship(
        "Reference",
        secondary="document_tags", 
        backref="tags"            
    )

    def __repr__(self):
        return f"<Tag({self.name})>"

# 多对多中间表，指向 reference 表而非本地 document 表
class DocumentTag(db.Model):
    __tablename__ = "document_tags"

    id = db.Column(db.Integer, primary_key=True)
    document_id = reference_col("reference")  # 指向 reference.id
    tag_id = reference_col("tags")
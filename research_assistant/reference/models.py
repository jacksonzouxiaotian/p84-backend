from research_assistant.extensions import db
from datetime import datetime

class Reference(db.Model):
    __tablename__ = "reference"  # 显式指定表名

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    authors = db.Column(db.String(255), nullable=False)
    year = db.Column(db.String(10), nullable=False)
    source = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 用于 Tag 页的完成标记
    completed = db.Column(db.Boolean, default=False)

    # 建立标签多对多关联（Tag <-> Reference）
    tags = db.relationship("Tag", secondary="document_tags", backref="documents")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "source": self.source,
            "completed": self.completed,
            "tags": [{"id": t.id, "name": t.name} for t in self.tags]
        }
    
    def add_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)

from research_assistant.database import PkModel
from datetime import datetime, timezone
from research_assistant.user.models import User
from research_assistant.extensions import db

class Document(PkModel):
    __tablename__ = 'documents'

    title = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Document({self.id}, {self.title})>"

class DocumentVersion(PkModel):
    __tablename__ = 'document_versions'

    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)

    major_version = db.Column(db.Integer, nullable=False, default=1)
    minor_version = db.Column(db.Integer, nullable=False, default=0)

    file_key = db.Column(db.String, nullable=False)
    file_url = db.Column(db.String, nullable=False)
    storage_provider = db.Column(db.String, default='s3')

    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    file_size = db.Column(db.Float)
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    is_current = db.Column(db.Boolean, default=True)

    document = db.relationship('Document', backref='versions')
    uploader = db.relationship('User', backref='uploaded_versions')

    def __repr__(self):
        return f"<DocumentVersion({self.document_id}, v{self.major_version}.{self.minor_version}, {self.file_key})>"

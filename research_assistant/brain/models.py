# research_assistant/brain/models.py

from datetime import datetime
from research_assistant.extensions import db

class BrainEntry(db.Model):
    __tablename__ = 'brain_entries'
    id = db.Column(db.Integer, primary_key=True)
    why = db.Column(db.String(512))
    what = db.Column(db.String(512))
    where = db.Column(db.String(512))
    when = db.Column(db.String(128))
    who = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'why': self.why,
            'what': self.what,
            'where': self.where,
            'when': self.when,
            'who': self.who,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

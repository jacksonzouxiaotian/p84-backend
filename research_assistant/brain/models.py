# research_assistant/brain/models.py

from datetime import datetime
from research_assistant.extensions import db
from research_assistant.user.models import User  # 假设你已经有 User 模型

class BrainEntry(db.Model):
    __tablename__ = 'brain_entries'

    id = db.Column(db.Integer, primary_key=True)
    why = db.Column(db.String(512))
    what = db.Column(db.String(512))
    where = db.Column(db.String(512))
    when = db.Column(db.String(128))
    who = db.Column(db.String(256))

    # User关联，确保每个BrainEntry记录都与特定用户关联
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='brain_entries')  # 用来反向查询用户所有的BrainEntries

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
            'user_id': self.user_id,  # 添加 user_id 到返回字典中
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

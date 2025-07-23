# research_assistant/planning/models.py
from datetime import date, datetime
from research_assistant.extensions import db
from research_assistant.user.models import User  # 一定要导入 User

class Phase(db.Model):
    __tablename__ = 'phases'

    id       = db.Column(db.Integer, primary_key=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user     = db.relationship('User', backref='phases')

    title       = db.Column(db.String(256), nullable=False)
    order       = db.Column(db.Integer, nullable=False, default=0)
    start_date  = db.Column(db.Date)
    end_date    = db.Column(db.Date)
    deadline    = db.Column(db.Date)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks = db.relationship(
        'Task',
        backref='phase',
        cascade='all, delete-orphan',
        order_by='Task.id'
    )

    def to_dict(self):
        # —— 省略和你原来几乎一模一样的“计算进度”逻辑 ——
        return {
            'id': self.id,
            'title': self.title,
            # ...
            'tasks': [t.to_dict() for t in self.tasks],
        }

class Task(db.Model):
    __tablename__ = 'tasks'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user        = db.relationship('User', backref='tasks')

    description = db.Column(db.String(512), nullable=False)
    completed   = db.Column(db.Boolean, default=False)
    phase_id    = db.Column(db.Integer, db.ForeignKey('phases.id'))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id':          self.id,
            'description': self.description,
            'completed':   self.completed,
        }

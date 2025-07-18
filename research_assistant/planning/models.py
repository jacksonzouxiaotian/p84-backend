from datetime import date, datetime
from research_assistant.extensions import db

class Phase(db.Model):
    __tablename__ = 'phases'
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(256), nullable=False)
    order       = db.Column(db.Integer, nullable=False, default=0)
    start_date  = db.Column(db.Date)
    end_date    = db.Column(db.Date)
    deadline    = db.Column(db.Date)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow)

    # 关联 tasks
    tasks = db.relationship(
        'Task',
        backref='phase',
        cascade='all, delete-orphan',
        order_by='Task.id'
    )

    def to_dict(self):
        total_tasks     = len(self.tasks)
        completed_tasks = sum(1 for t in self.tasks if t.completed)
        pct_complete    = (completed_tasks / total_tasks * 100) if total_tasks else 0

        # 计算状态（示例，可按需微调）
        from datetime import date
        today = date.today()
        if self.deadline:
            days_left = (self.deadline - today).days
            if days_left < 0:
                status = 'Overdue'
            elif pct_complete == 100 and today <= self.deadline:
                status = 'Completed'
            elif self.start_date:
                total_duration = (self.deadline - self.start_date).days or 1
                time_ratio     = 1 - days_left / total_duration
                progress_ratio = pct_complete / 100
                status         = 'AtRisk' if progress_ratio < time_ratio else 'OnTrack'
            else:
                status = 'OnTrack'
        else:
            days_left = None
            status    = 'Completed' if pct_complete == 100 else 'OnTrack'

        return {
            'id':               self.id,
            'title':            self.title,
            'order':            self.order,
            'start_date':       self.start_date.isoformat() if self.start_date else None,
            'end_date':         self.end_date.isoformat()   if self.end_date   else None,
            'deadline':         self.deadline.isoformat()   if self.deadline   else None,
            'total_tasks':      total_tasks,
            'completed_tasks':  completed_tasks,
            'pct_complete':     round(pct_complete, 1),
            'days_left':        days_left,
            'status':           status,
            'tasks':            [t.to_dict() for t in self.tasks],
        }

class Task(db.Model):
    __tablename__ = 'tasks'
    id          = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(512), nullable=False)
    completed   = db.Column(db.Boolean, default=False)
    phase_id    = db.Column(db.Integer, db.ForeignKey('phases.id'))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow,
                            onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id':          self.id,
            'description': self.description,
            'completed':   self.completed,
        }

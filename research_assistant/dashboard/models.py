# -*- coding: utf-8 -*-
"""PhaseStatus model for tracking user research phases."""

import datetime as dt

from research_assistant.database import Column, PkModel, db
# 不需要 reference_col，因为 username 不是整数外键

class PhaseStatus(PkModel):
    """Research phase status for each user."""

    __tablename__ = "phase_statuses"

    user_id = Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    phase_number = Column(db.Integer, nullable=False)  # 阶段编号：1~6
    title = Column(db.String(255), nullable=False)
    status = Column(
        db.String(20),
        nullable=False,
        default="NotCompleted"
    )

    updated_at = Column(
        db.DateTime,
        nullable=False,
        default=lambda: dt.datetime.now(dt.timezone.utc),
        onupdate=lambda: dt.datetime.now(dt.timezone.utc)
    )

    user = db.relationship("User", backref="phase_statuses")

    def __repr__(self):
        return f"<PhaseStatus(user_id={self.user_id}, phase={self.phase_number}, status={self.status})>"


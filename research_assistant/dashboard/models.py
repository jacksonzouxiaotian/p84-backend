# -*- coding: utf-8 -*-
"""PhaseStatus model for tracking user research phases."""

import datetime as dt

from research_assistant.database import Column, PkModel, db

class PhaseStatus(PkModel):
    """Research phase status for each user."""

    __tablename__ = "phase_statuses"
    # Foreign key referencing the 'users' table, linking the phase status to a specific user
    user_id = Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    # Phase number (1 to 6)
    phase_number = Column(db.Integer, nullable=False)
    # Title of the phase
    title = Column(db.String(255), nullable=False)
    # Current status of the phase (e.g., NotCompleted, Completed)
    status = Column(
        db.String(20),
        nullable=False,
        default="NotCompleted"
    )
    # Timestamp of the last update; automatically set to UTC time
    updated_at = Column(
        db.DateTime,
        nullable=False,
        default=lambda: dt.datetime.now(dt.timezone.utc),
        onupdate=lambda: dt.datetime.now(dt.timezone.utc)
    )
    # Relationship to the User model (one-to-many)
    user = db.relationship("User", backref="phase_statuses")

    def __repr__(self):
        """String representation of the PhaseStatus object."""
        return f"<PhaseStatus(user_id={self.user_id}, phase={self.phase_number}, status={self.status})>"


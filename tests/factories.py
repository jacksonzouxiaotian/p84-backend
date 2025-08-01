# -*- coding: utf-8 -*-
"""Factories to help in tests."""
from factory.alchemy import SQLAlchemyModelFactory

from research_assistant.database import db

class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = db.session
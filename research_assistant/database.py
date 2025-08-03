# -*- coding: utf-8 -*-
"""
Database module.

This module initializes the SQLAlchemy database object and provides
base models and utilities for common database operations.

Contents:
    - CRUDMixin: Convenience methods for create, read, update, delete
    - Model: Base model class with CRUD
    - PkModel: Base model with primary key (id) column
    - reference_col: Helper for foreign key column creation
"""

from typing import Optional, Type, TypeVar
from .extensions import db

# Generic type variable for PkModel subclasses
T = TypeVar("T", bound="PkModel")

# Aliases for common SQLAlchemy objects
Column = db.Column
relationship = db.relationship


class CRUDMixin(object):
    """
    Mixin providing convenience methods for CRUD operations.

    Methods:
        - create(**kwargs): Create and save a new record
        - update(**kwargs): Update fields of an existing record
        - save(commit=True): Save (insert/update) the record
        - delete(commit=True): Delete the record
    """

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it to the database."""
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record and optionally commit."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        if commit:
            return self.save()
        return self

    def save(self, commit=True):
        """Save (insert or update) the record in the database."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit: bool = True) -> None:
        """Remove the record from the database and optionally commit."""
        db.session.delete(self)
        if commit:
            return db.session.commit()
        return


class Model(CRUDMixin, db.Model):
    """
    Abstract base model class.

    Inherits from SQLAlchemy's db.Model and includes CRUDMixin for
    common database operations.
    """
    __abstract__ = True


class PkModel(Model):
    """
    Abstract base model class with a primary key.

    Adds:
        - id (int): Primary key column.

    Methods:
        - get_by_id(record_id): Retrieve record by primary key ID.
    """
    __abstract__ = True
    id = Column(db.Integer, primary_key=True)

    @classmethod
    def get_by_id(cls: Type[T], record_id) -> Optional[T]:
        """
        Retrieve a record by its ID.

        Args:
            record_id (int | str | float): The record ID.

        Returns:
            Optional[PkModel]: The record instance if found, otherwise None.
        """
        if any((
            isinstance(record_id, str) and record_id.isdigit(),
            isinstance(record_id, (int, float)),
        )):
            return cls.query.session.get(cls, int(record_id))
        return None


def reference_col(
    tablename, nullable=False, pk_name="id", foreign_key_kwargs=None, column_kwargs=None
):
    """
    Create a foreign key column referencing a primary key in another table.

    Args:
        tablename (str): Target table name.
        nullable (bool): Whether the foreign key can be null.
        pk_name (str): Primary key column name of the referenced table.
        foreign_key_kwargs (dict): Additional kwargs for ForeignKey.
        column_kwargs (dict): Additional kwargs for Column.

    Usage:
        ```python
        category_id = reference_col('category')
        category = relationship('Category', backref='categories')
        ```

    Returns:
        sqlalchemy.Column: A foreign key column definition.
    """
    foreign_key_kwargs = foreign_key_kwargs or {}
    column_kwargs = column_kwargs or {}

    return Column(
        db.ForeignKey(f"{tablename}.{pk_name}", **foreign_key_kwargs),
        nullable=nullable,
        **column_kwargs,
    )

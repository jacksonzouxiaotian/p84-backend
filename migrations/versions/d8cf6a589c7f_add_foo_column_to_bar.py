"""Add user_id FK to sections

Revision ID: d8cf6a589c7f
Revises:
Create Date: 2025-07-23 10:08:20.361480
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd8cf6a589c7f'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # 直接加列再建外键
    op.add_column(
        'sections',
        sa.Column('user_id', sa.Integer(), nullable=False)
    )
    op.create_foreign_key(
        'fk_sections_user_id_users',  # 约束名
        'sections',
        'users',
        ['user_id'],
        ['id']
    )

def downgrade():
    op.drop_constraint(
        'fk_sections_user_id_users',
        'sections',
        type_='foreignkey'
    )
    op.drop_column('sections', 'user_id')

"""Add tag_status to posts

Revision ID: xxxx
Revises: d3a4d2d5bad9
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    op.add_column('posts', sa.Column('tag_status', sa.String(), nullable=True, server_default='pending'))

def downgrade() -> None:
    op.drop_column('posts', 'tag_status') 
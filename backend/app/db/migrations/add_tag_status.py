"""Add tag_status column to posts table

Revision ID: add_tag_status
Revises: 
Create Date: 2024-05-09 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('posts', sa.Column('tag_status', sa.String(), nullable=True, server_default='pending'))

def downgrade():
    op.drop_column('posts', 'tag_status') 
"""Add source and run_type columns to rss_scrape_runs table

Revision ID: add_source_and_run_type
Revises: add_tag_status
Create Date: 2024-05-09 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('rss_scrape_runs', sa.Column('source', sa.String(), nullable=True))
    op.add_column('rss_scrape_runs', sa.Column('run_type', sa.String(), nullable=True))

def downgrade():
    op.drop_column('rss_scrape_runs', 'source')
    op.drop_column('rss_scrape_runs', 'run_type') 
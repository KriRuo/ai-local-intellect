from sqlalchemy import Column, Integer, String, Text, DateTime, MetaData, Table
from sqlalchemy.sql import func

def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    notes = Table(
        'notes', meta,
        Column('id', Integer, primary_key=True, index=True),
        Column('title', String(200), nullable=False),
        Column('description', Text, nullable=True),
        Column('created_at', DateTime(timezone=True), server_default=func.now()),
        Column('updated_at', DateTime(timezone=True), onupdate=func.now()),
    )
    notes.create()

def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    notes = Table('notes', meta, autoload_with=migrate_engine)
    notes.drop() 
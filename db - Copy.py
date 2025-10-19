# db.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, MetaData, Table, select
import datetime

# Create a local SQLite database
engine = create_engine('sqlite:///market.db', echo=False)
metadata = MetaData()

# Define the table for stock ticks
ticks = Table(
    'ticks', metadata,
    Column('id', Integer, primary_key=True),
    Column('symbol', String),
    Column('timestamp', DateTime),
    Column('open', Float),
    Column('high', Float),
    Column('low', Float),
    Column('close', Float),
    Column('volume', Float)
)

# Define a table for the AI learning log
learning_log = Table(
    'learning_log', metadata,
    Column('id', Integer, primary_key=True),
    Column('date', DateTime),
    Column('note', String)
)

# Create all tables
metadata.create_all(engine)

# Insert a single market tick (row)
def insert_tick(row):
    with engine.connect() as conn:
        conn.execute(ticks.insert().values(**row))

# Get recent market ticks for a symbol
def get_recent_ticks(symbol, limit=500):
    with engine.connect() as conn:
        q = select(ticks).where(ticks.c.symbol == symbol).order_by(ticks.c.timestamp.desc()).limit(limit)
        res = conn.execute(q).fetchall()
        return [dict(r._mapping) for r in res]  # _mapping ensures compatibility with SQLAlchemy 2.x

# Add a learning log note
def add_log(note):
    with engine.connect() as conn:
        conn.execute(learning_log.insert().values(date=datetime.datetime.utcnow(), note=note))

# Retrieve recent learning logs
def get_logs(limit=50):
    with engine.connect() as conn:
        q = select(learning_log).order_by(learning_log.c.date.desc()).limit(limit)
        res = conn.execute(q).fetchall()
        return [dict(r._mapping) for r in res]

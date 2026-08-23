"""
GovFlow AI — Database Core
Manages the SQLAlchemy Engine, Session factory, and Declarative Base.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# 1. Load environment variables from .env file
load_dotenv()
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://govflow:govflow_secret@localhost:5460/govflow_dev",
)

# 2. Create the Database Engine
# pool_pre_ping=True tells SQLAlchemy to check if the database connection is alive
# before executing queries (prevents "MySQL server has gone away" / dead connection errors)
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)

# 3. Create a Session Factory
# autocommit=False & autoflush=False give us explicit control over when data is saved
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Define the Base class for all ORM models
class Base(DeclarativeBase):
    pass

# 5. Dependency for FastAPI routes (we will use this on Day 4)
def get_db():
    """
    Yields a database session and ensures it closes after the request ends,
    even if an exception occurred.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
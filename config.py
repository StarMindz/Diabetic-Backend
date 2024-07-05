# config.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Use the appropriate URL for PostgreSQL or SQLite
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"  # PostgreSQL
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # SQLite

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

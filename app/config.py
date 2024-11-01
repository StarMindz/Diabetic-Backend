# config.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get the DATABASE_URL from environment variables
LIVE_DATABASE_URL = "[Datebase url]"
# If using PostgreSQL
# engine = create_engine(DATABASE_URL, echo=True, pool_size=5, max_overflow=20)
engine = create_engine(LIVE_DATABASE_URL, echo=True, pool_size=5, max_overflow=20)
# If using SQLite and want to support multiple threads
# engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})

# SessionLocal class is used to create session objects bound to the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class used as a declarative base for all ORM models
Base = declarative_base()

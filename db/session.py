from __future__ import annotations

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/shiks_db")


def get_engine():
    return create_engine(
        DATABASE_URL,
        future=True,
        pool_pre_ping=True,      # Validate connections before use
        pool_timeout=5,          # Fail fast (5 s) when DB is unavailable
        connect_args={"connect_timeout": 5},
    )


def get_session_factory():
    engine = get_engine()
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def create_all_tables():
    from db.models import Base

    engine = get_engine()
    Base.metadata.create_all(engine)

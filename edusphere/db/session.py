from __future__ import annotations

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/shiks_db")


def get_engine():
    return create_engine(
        DATABASE_URL,
        future=True,
        pool_pre_ping=True,
        pool_timeout=5,
        connect_args={"connect_timeout": 5},
    )


def get_session_factory():
    engine = get_engine()
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


SessionLocal = get_session_factory()


def create_all_tables():
    from .models import Base

    engine = get_engine()
    Base.metadata.create_all(engine)

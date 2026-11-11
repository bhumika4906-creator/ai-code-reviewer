from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DB_PATH = Path(__file__).resolve().parent.parent / "app.db"
DatabaseURL = f"sqlite:///{DB_PATH}"

Base = declarative_base()
engine = create_engine(DatabaseURL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    from app.models import ReviewResult  # noqa: F401

    Base.metadata.create_all(bind=engine)


init_db()

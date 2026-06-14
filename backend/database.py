from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(project_root, 'data', 'processed', 'cars.db')}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

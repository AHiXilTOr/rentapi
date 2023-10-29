from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv.main import load_dotenv
from sqlalchemy.orm import Session
from fastapi import Depends
from typing import Annotated
import os

load_dotenv()
SQLALCHEMY_URL = os.getenv("SQLALCHEMY_URL")

engine = create_engine(SQLALCHEMY_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
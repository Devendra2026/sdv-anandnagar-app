
from sqlalchemy import  create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.settings.config import settings

Base = declarative_base()

db_url = settings.DATABASE_URL
engine = create_engine(db_url, pool_pre_ping=True)
session = sessionmaker(bind= engine, autoflush=False, autocommit= False)

def get_db():
    try:
        db = session()
        yield db
    finally:
        db.close()


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Supabase (PostgreSQL) tarmog'iga ulanish siri:
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Azizbek0085%40@db.agmsxhesjtvkdjhysqni.supabase.co:5432/postgres"

# PostgreSQL ga ulanuvchi Engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

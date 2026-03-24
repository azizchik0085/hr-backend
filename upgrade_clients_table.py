from database import engine, Base
import models
from sqlalchemy import text

def upgrade_db():
    print("Creating new tables (if any)...")
    Base.metadata.create_all(bind=engine)
    print("New tables created.")

    print("Adding columns to clients table...")
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE clients ADD COLUMN stage VARCHAR DEFAULT 'yangi';"))
            print("Added 'stage' column to clients.")
        except Exception as e:
            print(f"Column 'stage' might already exist: {e}")
            
        try:
            conn.execute(text("ALTER TABLE clients ADD COLUMN source VARCHAR;"))
            print("Added 'source' column to clients.")
        except Exception as e:
            print(f"Column 'source' might already exist: {e}")

if __name__ == "__main__":
    upgrade_db()

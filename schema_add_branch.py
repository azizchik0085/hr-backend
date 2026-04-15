import sys
import os
from sqlalchemy import text

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from database import SessionLocal, engine
from models import Base, SalesBranch

def migrate():
    # Bu model kiritilganida uni bazaga Table qilib qo'yadi.
    Base.metadata.create_all(bind=engine)
    print("SalesBranch table created or verified.")

    db = SessionLocal()
    try:
        # supply_requests pageda eski columnlarga branchId qoshish
        db.execute(text("ALTER TABLE supply_requests ADD COLUMN branchId VARCHAR;"))
        print("branchId column added.")
    except Exception as e:
        print("branchId already exists or error:", e)

    try:
        db.execute(text("ALTER TABLE supply_requests ADD COLUMN branchName VARCHAR;"))
        print("branchName column added.")
    except Exception as e:
        print("branchName already exists or error:", e)

    db.commit()
    db.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()

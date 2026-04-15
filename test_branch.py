import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from database import SessionLocal
from models import SalesBranch
from schemas import SalesBranchCreate
import crud

def test_create():
    db = SessionLocal()
    try:
        branch_data = SalesBranchCreate(name="Test Branch", address="Test Address")
        branch = crud.create_branch(db, branch_data)
        print("Success:", branch.id)
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_create()

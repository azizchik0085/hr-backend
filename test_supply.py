from database import SessionLocal
import crud
import schemas

db = SessionLocal()
reqs = crud.get_supply_requests(db)

try:
    for r in reqs:
        emp = crud.get_employee(db, r.requesterId)
        if emp:
            r.requesterName = f"{emp.name} {emp.surname}".strip()
            r.requesterPhone = emp.phone
        else:
            print(f"Employee not found for {r.requesterId}")
            
        resp = schemas.SupplyRequestResponse.model_validate(r)
        print("Success for:", resp.id)
except Exception as e:
    import traceback
    traceback.print_exc()

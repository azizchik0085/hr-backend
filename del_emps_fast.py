from sqlalchemy.sql import text
from database import SessionLocal

db = SessionLocal()
try:
    print("Executing exact database cleanses...")
    res = db.execute(text("SELECT id FROM employees WHERE \"roleTitle\" NOT ILIKE '%direktor%' OR \"roleTitle\" IS NULL"))
    ids = [r[0] for r in res.fetchall()]
    
    if not ids:
        print("No non-director employees to delete.")
    else:
        for emp_id in ids:
            def try_sql(q):
                try: 
                    db.execute(text(q), {"id": emp_id})
                    db.commit()
                except Exception: 
                    db.rollback()

            try_sql("DELETE FROM attendances WHERE \"employeeId\" = :id")
            try_sql("DELETE FROM action_logs WHERE \"employeeId\" = :id")
            try_sql("DELETE FROM crm_tasks WHERE employee_id = :id")
            try_sql("DELETE FROM expenses WHERE \"receiverId\" = :id OR \"cashierId\" = :id")
            try_sql("DELETE FROM expenses WHERE \"receiverId\" = :id OR \"cashier_id\" = :id")
            try_sql("DELETE FROM shift_schedules WHERE employee_id = :id")
            try_sql("DELETE FROM app_notifications WHERE employee_id = :id")
            try_sql("DELETE FROM live_locations WHERE employee_id = :id")
            try_sql("DELETE FROM meeting_participants WHERE meeting_id IN (SELECT id FROM meetings WHERE created_by = :id)")
            try_sql("DELETE FROM meeting_participants WHERE employee_id = :id")
            try_sql("DELETE FROM meetings WHERE created_by = :id")
            try_sql("DELETE FROM call_logs WHERE employee_id = :id")
            try_sql("DELETE FROM cash_shifts WHERE \"cashierId\" = :id")
            try_sql("UPDATE orders SET assigned_seller_id = NULL WHERE assigned_seller_id = :id")
            try_sql("UPDATE orders SET \"creatorId\" = NULL WHERE \"creatorId\" = :id")
            try_sql("UPDATE orders SET \"assignedDeliveryId\" = NULL WHERE \"assignedDeliveryId\" = :id")
            
            try_sql("DELETE FROM employees WHERE id = :id")
            
        print(f"Deleted {len(ids)} employees via exact SQL.")
finally:
    db.close()

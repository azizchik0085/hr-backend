from database import SessionLocal
from models import (
    Employee, Attendance, ActionLog, CRMTask, Expense, 
    ShiftSchedule, AppNotification, LiveLocation, 
    MeetingParticipant, Meeting, CallLog, Order
)

db = SessionLocal()
try:
    emps = db.query(Employee).all()
    deleted_count = 0
    for e in emps:
        if e.roleTitle and "direktor" in e.roleTitle.lower():
            continue
        
        # Helper to execute safe deletes
        def safe_delete(model_class, column):
            try:
                db.query(model_class).filter(column == e.id).delete(synchronize_session=False)
                db.commit()
            except Exception:
                db.rollback()

        safe_delete(Attendance, Attendance.employeeId)
        safe_delete(ActionLog, ActionLog.employeeId)
        safe_delete(CRMTask, CRMTask.employee_id)
        
        # Expense
        try:
            db.query(Expense).filter((Expense.receiverId == e.id)).delete(synchronize_session=False)
            db.commit()
        except: db.rollback()

        try:
            db.query(Expense).filter((Expense.cashier_id == e.id)).delete(synchronize_session=False)
            db.commit()
        except: db.rollback()
        
        safe_delete(ShiftSchedule, ShiftSchedule.employee_id)
        safe_delete(AppNotification, AppNotification.employee_id)
        safe_delete(LiveLocation, LiveLocation.employee_id)
        safe_delete(MeetingParticipant, MeetingParticipant.employee_id)
        safe_delete(Meeting, Meeting.created_by)
        safe_delete(CallLog, CallLog.employee_id)
        
        # Order assigned_seller_id nullification
        try:
            orders = db.query(Order).filter(Order.assigned_seller_id == e.id).all()
            for o in orders: o.assigned_seller_id = None
            db.commit()
        except Exception: db.rollback()
        
        # Order creatorId nullification
        try:
            orders2 = db.query(Order).filter(Order.creatorId == e.id).all()
            for o in orders2: o.creatorId = None
            db.commit()
        except Exception: db.rollback()

        # Delete Employee
        try:
            db.delete(e)
            db.commit()
            deleted_count += 1
        except Exception as exc:
            db.rollback()
            print(f"Failed to delete {e.id}: {exc}")

    print(f"Deleted {deleted_count} employees successfully.")
finally:
    db.close()

from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from typing import Optional

import models
import schemas
from auth import get_password_hash

# ================= EMPLOYEE =================
def get_employee(db: Session, employee_id: str):
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()

def get_employee_by_login(db: Session, login: str):
    return db.query(models.Employee).filter(models.Employee.login == login).first()

from sqlalchemy.orm import defer

def get_employees(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Employee).options(defer(models.Employee.faceIdImage)).offset(skip).limit(limit).all()

def create_employee(db: Session, employee: schemas.EmployeeCreate):
    hashed_password = get_password_hash(employee.password)
    db_employee = models.Employee(
        id=f"EMP-{uuid.uuid4().hex[:8].upper()}",
        name=employee.name,
        surname=employee.surname,
        roleTitle=employee.roleTitle,
        login=employee.login,
        hashed_password=hashed_password,
        isApproved=employee.isApproved,
        isActive=employee.isActive,
        requireGPS=employee.requireGPS,
        requireFaceID=employee.requireFaceID,
        phone=employee.phone,
        passportSeries=employee.passportSeries,
        faceIdImage=employee.faceIdImage,
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def update_employee(db: Session, employee_id: str, employee_data: dict):
    db_employee = get_employee(db, employee_id)
    if db_employee:
        for key, value in employee_data.items():
            if value is not None:
                if key == "password" and value.strip() != "":
                    db_employee.hashed_password = get_password_hash(value)
                elif hasattr(db_employee, key) and key != "password":
                    setattr(db_employee, key, value)
        db.commit()
        db.refresh(db_employee)
    return db_employee

def update_employee_face_id(db: Session, employee_id: str, face_image_path: str):
    db_employee = get_employee(db, employee_id)
    if db_employee:
        db_employee.faceIdImage = face_image_path
        db.commit()
        db.refresh(db_employee)
    return db_employee

# ================= ATTENDANCE =================
def create_attendance(db: Session, attendance: schemas.AttendanceCreate):
    db_attendance = models.Attendance(
        id=f"ATT-{uuid.uuid4().hex[:8].upper()}",
        employeeId=attendance.employeeId,
        date=attendance.date,
        checkInTime=attendance.checkInTime,
        checkOutTime=attendance.checkOutTime,
        faceAccuracy=attendance.faceAccuracy,
        locationLat=attendance.locationLat,
        locationLng=attendance.locationLng
    )
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

def get_attendances_by_date(db: Session, date: str):
    return db.query(models.Attendance).filter(models.Attendance.date == date).all()

# ================= PRODUCTS =================
def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(
        id=f"PRD-{uuid.uuid4().hex[:8].upper()}",
        **product.model_dump()
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# ================= SUPPLY REQUEST =================
def get_supply_requests(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.SupplyRequest).order_by(models.SupplyRequest.requestDate.desc()).offset(skip).limit(limit).all()

def create_supply_request(db: Session, request: schemas.SupplyRequestCreate):
    db_request = models.SupplyRequest(
        id=f"REQ-{uuid.uuid4().hex[:8].upper()}",
        requesterId=request.requesterId,
        status="Kutilmoqda"
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    # Ichidagi mahsulotlarni kiritish
    for item in request.items:
        db_item = models.SupplyRequestItem(
            id=f"SIT-{uuid.uuid4().hex[:8].upper()}",
            requestId=db_request.id,
            productName=item.productName,
            quantity=item.quantity
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_request)
    return db_request

def update_supply_request_status(db: Session, request_id: str, new_status: str, receipt_b64: str = None, product_b64: str = None):
    req = db.query(models.SupplyRequest).filter(models.SupplyRequest.id == request_id).first()
    if req:
        req.status = new_status
        # SLA timing checks
        if new_status == "Jarayonda":
            req.acceptedTime = datetime.utcnow()
        elif new_status == "Prixod kutilmoqda":
            req.readyTime = datetime.utcnow()
            if receipt_b64:
                req.receiptImage = receipt_b64
            if product_b64:
                req.productImage = product_b64
                
        db.commit()
        db.refresh(req)
    return req

def delete_supply_request(db: Session, request_id: str):
    req = db.query(models.SupplyRequest).filter(models.SupplyRequest.id == request_id).first()
    if req:
        db.query(models.SupplyRequestItem).filter(models.SupplyRequestItem.requestId == request_id).delete()
        db.delete(req)
        db.commit()
        return True
    return False

# ================= ORDERS =================
def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).offset(skip).limit(limit).all()

def create_order(db: Session, order: schemas.OrderCreate):
    db_order = models.Order(
        id=f"ORD-{uuid.uuid4().hex[:8].upper()}",
        customerName=order.customerName,
        customerPhone=order.customerPhone,
        deliveryAddress=order.deliveryAddress,
        latitude=order.latitude,
        longitude=order.longitude,
        totalAmount=order.totalAmount,
        status=order.status,
        creatorId=order.creatorId,
        assignedDeliveryId=order.assignedDeliveryId,
        productImage=order.productImage,
        receiptImage=order.receiptImage,
        is_delivery=order.is_delivery,
        assigned_seller_id=order.assigned_seller_id,
        needs_collect_money=order.needs_collect_money,
        amount_to_collect=order.amount_to_collect,
        operator_notes=order.operator_notes
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Add items
    for item in order.items:
        db_item = models.OrderItem(
            id=f"ITM-{uuid.uuid4().hex[:8].upper()}",
            orderId=db_order.id,
            productId=item.productId,
            productName=item.productName,
            quantity=item.quantity,
            price=item.price
        )
        db.add(db_item)
    
    db.commit()
    return db_order

def update_order(db: Session, order_id: str, order_data: dict):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order:
        for key, value in order_data.items():
            if value is not None and hasattr(db_order, key):
                setattr(db_order, key, value)
        db.commit()
        db.refresh(db_order)
    return db_order

def delete_order(db: Session, order_id: str):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order:
        # Avval ichidagi qismlarni (items) o'chiramiz
        db.query(models.OrderItem).filter(models.OrderItem.orderId == order_id).delete()
        # Endi o'zini
        db.delete(db_order)
        db.commit()
        return True
    return False

# ================= ACTION LOGS =================
def create_action_log(db: Session, employee_id: str, action_type: str, description: str):
    if not employee_id: return None
    new_log = models.ActionLog(
        id=f"LOG-{uuid.uuid4().hex[:8].upper()}",
        employeeId=employee_id,
        actionType=action_type,
        description=description
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

def get_action_logs(db: Session, employee_id: Optional[str] = None, skip: int = 0, limit: int = 100):
    query = db.query(models.ActionLog)
    if employee_id:
        query = query.filter(models.ActionLog.employeeId == employee_id)
    return query.order_by(models.ActionLog.timestamp.desc()).offset(skip).limit(limit).all()

# ================= EXPENSE (Xarajatlar) =================
def create_expense(db: Session, expense: schemas.ExpenseCreate, cashierId: str):
    db_expense = models.Expense(
        id=f"EXP-{uuid.uuid4().hex[:8].upper()}",
        amount=expense.amount,
        receiverId=expense.receiverId,
        purpose=expense.purpose,
        cashierId=cashierId,
        date=datetime.utcnow()
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def get_expenses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Expense).order_by(models.Expense.date.desc()).offset(skip).limit(limit).all()

# ================= CASH SHIFT (Z-Hisobot) =================
def create_cash_shift(db: Session, shift: schemas.CashShiftCreate, cashierId: str):
    db_shift = models.CashShift(
        id=f"SHF-{uuid.uuid4().hex[:8].upper()}",
        cashAmount=shift.cashAmount,
        terminalAmount=shift.terminalAmount,
        zReportImage=shift.zReportImage,
        cashierId=cashierId,
        date=datetime.utcnow()
    )
    db.add(db_shift)
    db.commit()
    db.refresh(db_shift)
    return db_shift

def get_cash_shifts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.CashShift).order_by(models.CashShift.date.desc()).offset(skip).limit(limit).all()

# ================= CALL LOGS & OPERATOR STATS =================
def create_call_log(db: Session, call_log: schemas.CallLogCreate):
    db_call = models.CallLog(
        id=f"CAL-{uuid.uuid4().hex[:8].upper()}",
        employee_id=call_log.employee_id,
        client_phone=call_log.client_phone,
        call_type=call_log.call_type,
        duration_seconds=call_log.duration_seconds,
        record_url=call_log.record_url,
        timestamp=datetime.utcnow()
    )
    db.add(db_call)
    db.commit()
    db.refresh(db_call)
    return db_call

def save_call_audio(db: Session, employee_id: str, client_phone: str, record_url: str):
    db_call = models.CallLog(
        id=f"CAL-{uuid.uuid4().hex[:8].upper()}",
        employee_id=employee_id,
        client_phone=client_phone,
        call_type="Yozib Olingan",
        duration_seconds=0,
        record_url=record_url,
        timestamp=datetime.utcnow()
    )
    db.add(db_call)
    db.commit()
    db.refresh(db_call)
    return db_call

def get_call_logs(db: Session, limit: int = 1000):
    return db.query(models.CallLog).order_by(models.CallLog.timestamp.desc()).limit(limit).all()

def get_operator_stats(db: Session, start_date: str = None, end_date: str = None):
    # Operator yoki Sotuvchi rollaridagi xodimlarni olamiz
    operators = db.query(models.Employee).filter(
        (models.Employee.roleTitle.ilike('%operator%')) | 
        (models.Employee.roleTitle.ilike('%sotuv%'))
    ).all()
    
    stats = []
    for op in operators:
        # Calls
        calls_query = db.query(models.CallLog).filter(models.CallLog.employee_id == op.id)
        if start_date:
            try:
                dt_start = datetime.fromisoformat(start_date)
                calls_query = calls_query.filter(models.CallLog.timestamp >= dt_start)
            except: pass
        if end_date:
            try:
                dt_end = datetime.fromisoformat(end_date)
                calls_query = calls_query.filter(models.CallLog.timestamp <= dt_end)
            except: pass
        
        total_calls = calls_query.count()
        
        # Orders created
        orders_query = db.query(models.Order).filter(models.Order.creatorId == op.id)
        if start_date:
            try:
                dt_start = datetime.fromisoformat(start_date)
                orders_query = orders_query.filter(models.Order.orderDate >= dt_start)
            except: pass
        if end_date:
            try:
                dt_end = datetime.fromisoformat(end_date)
                orders_query = orders_query.filter(models.Order.orderDate <= dt_end)
            except: pass
            
        total_orders = orders_query.count()
        
        conversion = 0
        if total_calls > 0:
            conversion = (total_orders / total_calls) * 100
            
        stats.append({
            "employeeId": op.id,
            "name": op.name,
            "surname": op.surname,
            "roleTitle": op.roleTitle,
            "totalCalls": total_calls,
            "totalOrders": total_orders,
            "conversionRate": round(conversion, 1)
        })
    return stats


def pay_order(db: Session, order_id: str):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order:
        db_order.isPaid = True
        db.commit()
        db.refresh(db_order)
        return True
    return False

# ================= SHIFT SCHEDULE AND NOTIFICATIONS =================

def create_shift_schedule(db: Session, schedule: schemas.ShiftScheduleCreate):
    db_schedule = models.ShiftSchedule(**schedule.dict())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def get_shift_schedules(db: Session, date: str = None):
    query = db.query(models.ShiftSchedule)
    if date:
        query = query.filter(models.ShiftSchedule.date == date)
    return query.all()

def create_notification(db: Session, employee_id: int, message: str):
    db_notif = models.AppNotification(employee_id=employee_id, message=message)
    db.add(db_notif)
    db.commit()
    db.refresh(db_notif)
    return db_notif

def get_unread_notifications(db: Session, employee_id: int):
    return db.query(models.AppNotification).filter(
        models.AppNotification.employee_id == employee_id,
        models.AppNotification.is_read == False
    ).all()

def mark_notification_read(db: Session, notif_id: int):
    notif = db.query(models.AppNotification).filter(models.AppNotification.id == notif_id).first()
    if notif:
        notif.is_read = True
        db.commit()
        return True
    return False

# ================= LIVE GPS TRACKING =================

def update_live_location(db: Session, employee_id: int, lat: float, lng: float):
    loc = db.query(models.LiveLocation).filter(models.LiveLocation.employee_id == employee_id).first()
    if loc:
        loc.latitude = lat
        loc.longitude = lng
        loc.last_updated = datetime.utcnow()
        db.commit()
        db.refresh(loc)
        return loc
    else:
        new_loc = models.LiveLocation(employee_id=employee_id, latitude=lat, longitude=lng)
        db.add(new_loc)
        db.commit()
        db.refresh(new_loc)
        return new_loc

def get_live_locations(db: Session):
    locations = db.query(
        models.LiveLocation.employee_id,
        models.LiveLocation.latitude,
        models.LiveLocation.longitude,
        models.LiveLocation.last_updated,
        models.Employee.name,
        models.Employee.surname,
        models.Employee.roleTitle
    ).join(models.Employee, models.LiveLocation.employee_id == models.Employee.id).all()
    
    res = []
    for loc in locations:
        res.append({
            "employee_id": loc.employee_id,
            "name": loc.name,
            "surname": loc.surname,
            "role_title": loc.roleTitle,
            "lat": loc.latitude,
            "lng": loc.longitude,
            "last_updated": loc.last_updated
        })
    return res

# ================= VIDEO MEETINGS =================

def create_meeting(db: Session, meeting_data: schemas.MeetingCreate, creator_id: int):
    import uuid
    room_name = f"mobil_{uuid.uuid4().hex[:8]}"
    db_meeting = models.Meeting(
        title=meeting_data.title,
        room_name=room_name,
        scheduled_time=meeting_data.scheduled_time,
        created_by=creator_id
    )
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)

    for emp_id in meeting_data.participant_ids:
        db_part = models.MeetingParticipant(meeting_id=db_meeting.id, employee_id=emp_id)
        db.add(db_part)
        
        # Maxsus formatli xabarnoma (Flutter ushbu textni ko'rib URL ga aylantiradi)
        msg_text = f"VIDEO_MEETING|{db_meeting.title}|{room_name}"
        create_notification(db, emp_id, msg_text)

    db.commit()
    return db_meeting

def get_my_meetings(db: Session, employee_id: int):
    participant_meeting_ids = db.query(models.MeetingParticipant.meeting_id).filter(
        models.MeetingParticipant.employee_id == employee_id
    ).subquery()
    
    return db.query(models.Meeting).filter(
        (models.Meeting.id.in_(participant_meeting_ids)) | (models.Meeting.created_by == employee_id)
    ).order_by(models.Meeting.scheduled_time.desc()).all()

# ================= CLIENT & CRM =================

def get_clients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Client).offset(skip).limit(limit).all()

def create_client(db: Session, client: schemas.ClientCreate):
    db_client = models.Client(
        id=f"CLI-{uuid.uuid4().hex[:8].upper()}",
        **client.model_dump()
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def update_client_stage(db: Session, client_id: str, new_stage: str):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if db_client:
        db_client.stage = new_stage
        db.commit()
        db.refresh(db_client)
    return db_client

def get_crm_tasks(db: Session, employee_id: Optional[str] = None, date_str: Optional[str] = None):
    query = db.query(models.CRMTask)
    if employee_id:
        query = query.filter(models.CRMTask.employee_id == employee_id)
    
    tasks = query.order_by(models.CRMTask.scheduled_time.asc()).all()
    
    # Kunga ko'ra filterlash (agar kelsa)
    if date_str:
        return [t for t in tasks if t.scheduled_time.strftime("%Y-%m-%d") == date_str]
    return tasks

def create_crm_task(db: Session, task: schemas.CRMTaskCreate, employee_id: str):
    db_task = models.CRMTask(
        id=f"TSK-{uuid.uuid4().hex[:8].upper()}",
        employee_id=employee_id,
        client_id=task.client_id,
        scheduled_time=task.scheduled_time,
        expected_product=task.expected_product,
        notes=task.notes,
        status=task.status
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_crm_task(db: Session, task_id: str, task_data: schemas.CRMTaskUpdate):
    db_task = db.query(models.CRMTask).filter(models.CRMTask.id == task_id).first()
    if db_task:
        update_dict = task_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(db_task, key, value)
        db.commit()
        db.refresh(db_task)
    return db_task

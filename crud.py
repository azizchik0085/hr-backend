from sqlalchemy.orm import Session
from datetime import datetime
import uuid

import models
import schemas
from auth import get_password_hash

# ================= EMPLOYEE =================
def get_employee(db: Session, employee_id: str):
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()

def get_employee_by_login(db: Session, login: str):
    return db.query(models.Employee).filter(models.Employee.login == login).first()

def get_employees(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Employee).offset(skip).limit(limit).all()

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
    )
    db.add(db_employee)
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
    return db.query(models.SupplyRequest).offset(skip).limit(limit).all()

def create_supply_request(db: Session, request: schemas.SupplyRequestCreate):
    db_request = models.SupplyRequest(
        id=f"REQ-{uuid.uuid4().hex[:8].upper()}",
        **request.model_dump()
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

def mark_supply_request_completed(db: Session, request_id: str):
    req = db.query(models.SupplyRequest).filter(models.SupplyRequest.id == request_id).first()
    if req:
        req.isCompleted = True
        
        # Ochiqchasiga tovar miqdorini oshirish:
        if req.productId:
            prd = db.query(models.Product).filter(models.Product.id == req.productId).first()
            if prd:
                prd.currentStock += req.requestedQuantity
                
        db.commit()
        db.refresh(req)
    return req

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
        assignedDeliveryId=order.assignedDeliveryId
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

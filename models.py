from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, default="")
    surname = Column(String, default="")
    roleTitle = Column(String, default="")
    dateJoined = Column(DateTime, default=datetime.utcnow)
    login = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    isApproved = Column(Boolean, default=True)
    phone = Column(String, nullable=True) # YANGI
    passportSeries = Column(String, nullable=True) # YANGI
    faceIdImage = Column(String, nullable=True) # YANGI
    
    # Yangi boshqaruv parametrlari
    isActive = Column(Boolean, default=True)
    requireGPS = Column(Boolean, default=True)
    requireFaceID = Column(Boolean, default=True)

    attendances = relationship("Attendance", back_populates="employee")
    action_logs = relationship("ActionLog", back_populates="employee")

class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(String, primary_key=True, index=True)
    employeeId = Column(String, ForeignKey("employees.id"))
    date = Column(String) # YYYY-MM-DD
    checkInTime = Column(DateTime, nullable=True)
    checkOutTime = Column(DateTime, nullable=True)
    faceAccuracy = Column(Float, nullable=True)
    locationLat = Column(Float, nullable=True)
    locationLng = Column(Float, nullable=True)

    employee = relationship("Employee", back_populates="attendances")

class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    description = Column(String, nullable=True)
    price = Column(Float)
    currency = Column(String, default="UZS")
    currentStock = Column(Integer, default=0)
    minRequiredStock = Column(Integer, default=10)
    brand = Column(String, nullable=True)

class SupplyRequest(Base):
    __tablename__ = "supply_requests"

    id = Column(String, primary_key=True, index=True)
    requesterId = Column(String)  # Sotuvchi ID
    requestDate = Column(DateTime, default=datetime.utcnow)
    
    # SLA vaqt nazorati
    acceptedTime = Column(DateTime, nullable=True)  # Qachon qabul qilindi
    readyTime = Column(DateTime, nullable=True)     # Qachon tayyor bo'ldi
    
    # Kutilmoqda, Jarayonda, Prixod kutilmoqda, Tayyor
    status = Column(String, default="Kutilmoqda") 
    
    # Snabjens tomonidan kiritiladigan rasmlar (Base64)
    receiptImage = Column(String, nullable=True) 
    productImage = Column(String, nullable=True)

    items = relationship("SupplyRequestItem", back_populates="request", cascade="all, delete")

class SupplyRequestItem(Base):
    __tablename__ = "supply_request_items"
    
    id = Column(String, primary_key=True, index=True)
    requestId = Column(String, ForeignKey("supply_requests.id"))
    productName = Column(String)
    quantity = Column(Integer)
    
    request = relationship("SupplyRequest", back_populates="items")

class Client(Base):
    __tablename__ = "clients"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    companyName = Column(String, nullable=True)
    defaultAddress = Column(String, nullable=True)

class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True)
    customerName = Column(String)
    customerPhone = Column(String)
    deliveryAddress = Column(String)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    totalAmount = Column(Float)
    orderDate = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")
    creatorId = Column(String)
    assignedDeliveryId = Column(String, nullable=True)
    assignedTime = Column(DateTime, nullable=True)
    productImage = Column(String, nullable=True)
    receiptImage = Column(String, nullable=True)
    isPaid = Column(Boolean, default=False)

    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String, primary_key=True, index=True)
    orderId = Column(String, ForeignKey("orders.id"))
    productId = Column(String)
    productName = Column(String)
    quantity = Column(Integer)
    price = Column(Float)

    order = relationship("Order", back_populates="items")

class ActionLog(Base):
    __tablename__ = "action_logs"

    id = Column(String, primary_key=True, index=True)
    employeeId = Column(String, ForeignKey("employees.id"))
    actionType = Column(String)  # Masalan: "DAVOMAT", "BUYURTMA_YARATILDI", "BUYURTMA_BEKOR"
    description = Column(String) # "Ishga keldi (09:00)" yoki "ORD-123 ni yaratdi"
    timestamp = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="action_logs")

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(String, primary_key=True, index=True)
    amount = Column(Float)
    receiverId = Column(String, nullable=True) # Kimga berildi (Employee ID)
    purpose = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    cashier_id = Column(String, ForeignKey('employees.id'))

class ShiftSchedule(Base):
    __tablename__ = "shift_schedules"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey('employees.id'))
    date = Column(String)  # ISO format "YYYY-MM-DD" Date of shift
    shift_type = Column(String)  # "1-smena", "2-smena"
    created_at = Column(DateTime, default=datetime.utcnow)

class AppNotification(Base):
    __tablename__ = "app_notifications"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey('employees.id'))
    message = Column(String)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class LiveLocation(Base):
    __tablename__ = "live_locations"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey('employees.id'), unique=True)
    latitude = Column(Float)
    longitude = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Meeting(Base):
    __tablename__ = "meetings"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    room_name = Column(String) # Jitsi dagi xona nomi
    scheduled_time = Column(DateTime)
    created_by = Column(String, ForeignKey('employees.id'))
    created_at = Column(DateTime, default=datetime.utcnow)

class MeetingParticipant(Base):
    __tablename__ = "meeting_participants"
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id'))
    employee_id = Column(String, ForeignKey('employees.id'))

class CashShift(Base):
    __tablename__ = "cash_shifts"

    id = Column(String, primary_key=True, index=True)
    cashAmount = Column(Float)
    terminalAmount = Column(Float)
    zReportImage = Column(String) # Base64
    date = Column(DateTime, default=datetime.utcnow)
    cashierId = Column(String)

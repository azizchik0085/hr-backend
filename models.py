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
    
    # Yangi boshqaruv parametrlari
    isActive = Column(Boolean, default=True)
    requireGPS = Column(Boolean, default=True)
    requireFaceID = Column(Boolean, default=True)

    attendances = relationship("Attendance", back_populates="employee")

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
    productId = Column(String, nullable=True)
    productName = Column(String)
    requesterId = Column(String)
    requestedQuantity = Column(Integer)
    requestDate = Column(DateTime, default=datetime.utcnow)
    isCompleted = Column(Boolean, default=False)
    imageUrl = Column(String, nullable=True)

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

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# ================= EMPLOYEE =================
class EmployeeBase(BaseModel):
    name: str
    surname: str
    roleTitle: str
    login: str
    isApproved: bool = True
    isActive: bool = True
    requireGPS: bool = True
    requireFaceID: bool = True

class EmployeeCreate(EmployeeBase):
    password: str

class EmployeeResponse(EmployeeBase):
    id: str
    dateJoined: datetime
    
    class Config:
        from_attributes = True

# ================= ATTENDANCE =================
class AttendanceBase(BaseModel):
    employeeId: str
    date: str
    checkInTime: Optional[datetime] = None
    checkOutTime: Optional[datetime] = None
    faceAccuracy: Optional[float] = None
    locationLat: Optional[float] = None
    locationLng: Optional[float] = None

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceResponse(AttendanceBase):
    id: str

    class Config:
        from_attributes = True

# ================= PRODUCT =================
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    currency: str = "UZS"
    currentStock: int = 0
    minRequiredStock: int = 10
    brand: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: str

    class Config:
        from_attributes = True

# ================= SUPPLY REQUEST =================
class SupplyRequestBase(BaseModel):
    productId: Optional[str] = None
    productName: str
    requesterId: str
    requestedQuantity: int
    imageUrl: Optional[str] = None

class SupplyRequestCreate(SupplyRequestBase):
    pass

class SupplyRequestResponse(SupplyRequestBase):
    id: str
    requestDate: datetime
    isCompleted: bool

    class Config:
        from_attributes = True

# ================= ORDER =================
class OrderItemBase(BaseModel):
    productId: str
    productName: str
    quantity: int
    price: float

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: str
    orderId: str

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    customerName: str
    customerPhone: str
    deliveryAddress: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    totalAmount: float
    status: str = "pending"
    creatorId: str
    assignedDeliveryId: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderResponse(OrderBase):
    id: str
    orderDate: datetime
    assignedTime: Optional[datetime] = None
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True

# Token
class Token(BaseModel):
    access_token: str
    token_type: str

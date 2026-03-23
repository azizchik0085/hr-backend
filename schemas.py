from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# ================= EMPLOYEE =================
class EmployeeBase(BaseModel):
    name: str
    surname: str
    roleTitle: str
    login: str
    phone: Optional[str] = None
    passportSeries: Optional[str] = None
    faceIdImage: Optional[str] = None
    isApproved: bool = True
    isActive: bool = True
    requireGPS: bool = True
    requireFaceID: bool = True

class EmployeeCreate(EmployeeBase):
    password: str

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    roleTitle: Optional[str] = None
    login: Optional[str] = None
    passportSeries: Optional[str] = None
    faceIdImage: Optional[str] = None
    isActive: Optional[bool] = None
    isApproved: Optional[bool] = None
    requireGPS: Optional[bool] = None
    requireFaceID: Optional[bool] = None
    password: Optional[str] = None

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

# ================= SUPPLY REQUEST ITEM =================
class SupplyRequestItemBase(BaseModel):
    productName: str
    quantity: int

class SupplyRequestItemCreate(SupplyRequestItemBase):
    pass

class SupplyRequestItemResponse(SupplyRequestItemBase):
    id: str
    requestId: str

    class Config:
        from_attributes = True

# ================= SUPPLY REQUEST =================
class SupplyRequestBase(BaseModel):
    requesterId: str
    status: str = "Kutilmoqda"
    receiptImage: Optional[str] = None
    productImage: Optional[str] = None

class SupplyRequestCreate(SupplyRequestBase):
    items: List[SupplyRequestItemCreate]

class SupplyRequestResponse(SupplyRequestBase):
    id: str
    requestDate: datetime
    acceptedTime: Optional[datetime] = None
    readyTime: Optional[datetime] = None
    
    # Qulaylik uchun yuboruvchi haqida ma'lumot qoshamiz (Join orqali keladi)
    requesterName: Optional[str] = None
    requesterPhone: Optional[str] = None
    
    items: List[SupplyRequestItemResponse] = []

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
    productImage: Optional[str] = None
    receiptImage: Optional[str] = None
    isPaid: bool = False

    is_delivery: bool = False
    assigned_seller_id: Optional[str] = None
    needs_collect_money: bool = False
    amount_to_collect: Optional[float] = None
    operator_notes: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    assignedDeliveryId: Optional[str] = None
    productImage: Optional[str] = None
    receiptImage: Optional[str] = None

class OrderResponse(OrderBase):
    id: str
    orderDate: datetime
    assignedTime: Optional[datetime] = None
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True

# ================= ACTION LOG =================
class ActionLogBase(BaseModel):
    employeeId: str
    actionType: str
    description: str

class ActionLogCreate(ActionLogBase):
    pass

class ActionLogResponse(ActionLogBase):
    id: str
    timestamp: datetime

    class Config:
        from_attributes = True

# ================= CALL LOG =================
class CallLogBase(BaseModel):
    employee_id: str
    client_phone: str
    call_type: str
    duration_seconds: int = 0
    record_url: Optional[str] = None

class CallLogCreate(CallLogBase):
    pass

class CallLogResponse(CallLogBase):
    id: str
    timestamp: datetime

    class Config:
        from_attributes = True

# ================= OPERATOR STAT =================
class OperatorStatResponse(BaseModel):
    employeeId: str
    name: str
    surname: str
    roleTitle: str
    totalCalls: int
    totalOrders: int
    conversionRate: float

# Token
class Token(BaseModel):
    access_token: str
    token_type: str

# ================= EXPENSE =================
class ExpenseBase(BaseModel):
    amount: float
    receiverId: Optional[str] = None
    purpose: str

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    id: str
    date: datetime
    cashierId: str

    class Config:
        from_attributes = True

# ================= CASH SHIFT =================
class CashShiftBase(BaseModel):
    cashAmount: float
    terminalAmount: float
    zReportImage: str

class CashShiftCreate(CashShiftBase):
    pass

class CashShiftResponse(CashShiftBase):
    id: str
    date: datetime
    cashierId: str

    class Config:
        from_attributes = True

class CashShiftOut(CashShiftBase):
    id: str
    date: datetime
    cashier_id: str

    class Config:
        from_attributes = True

class ShiftScheduleBase(BaseModel):
    employee_id: str
    date: str
    shift_type: str

class ShiftScheduleCreate(ShiftScheduleBase):
    pass

class ShiftScheduleOut(ShiftScheduleBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AppNotificationBase(BaseModel):
    employee_id: str
    message: str

class AppNotificationCreate(AppNotificationBase):
    pass

class AppNotificationOut(AppNotificationBase):
    id: int
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class LocationUpdate(BaseModel):
    lat: float
    lng: float

class LiveLocationOut(BaseModel):
    employee_id: str
    name: str
    surname: str
    role_title: str
    lat: float
    lng: float
    last_updated: datetime

    class Config:
        from_attributes = True

class MeetingCreate(BaseModel):
    title: str
    scheduled_time: datetime
    participant_ids: List[str]

class MeetingOut(BaseModel):
    id: int
    title: str
    room_name: str
    scheduled_time: datetime
    created_by: str
    
    class Config:
        from_attributes = True

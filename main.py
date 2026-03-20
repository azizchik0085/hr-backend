from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse, Response
import base64
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import List, Optional
import os
import shutil   
import asyncio

import models
import schemas
import crud
import auth
from database import SessionLocal, engine, get_db

# Baza jadvalarini yaratish (Migratsiya o'rniga avtomat yaratiladi, agar SQLite bo'lsa darxol tushadi)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="MOBIL App Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ================= AUTHENTICATION =================
@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_employee_by_login(db, login=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Noto'g'ri login yoki parol",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.isApproved:
        if user.roleTitle and user.roleTitle.startswith("Rad:"):
            raise HTTPException(status_code=400, detail=f"Arizangiz rad etildi! Sabab: {user.roleTitle.split('Rad:')[1]}")
        raise HTTPException(status_code=400, detail="Direktor tasdiqini kutyapsiz")
    if not user.isActive:
        raise HTTPException(status_code=400, detail="Akauntingiz bloklangan")

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.login, "role": user.roleTitle, "id": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    from jose import JWTError, jwt
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token yaroqsiz",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_employee_by_login(db, login=username)
    if user is None:
        raise credentials_exception
    return user

# ================= EMPLOYEES =================
@app.post("/employees/", response_model=schemas.EmployeeResponse)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    db_emp = crud.get_employee_by_login(db, login=employee.login)
    if db_emp:
        raise HTTPException(status_code=400, detail="Bu login allaqachon mavjud")
    return crud.create_employee(db=db, employee=employee)

@app.put("/employees/{employee_id}", response_model=schemas.EmployeeResponse)
def update_employee(employee_id: str, employee: schemas.EmployeeUpdate, db: Session = Depends(get_db)):
    db_emp = crud.get_employee(db, employee_id)
    if not db_emp:
        raise HTTPException(status_code=404, detail="Xodim topilmadi")
    return crud.update_employee(db=db, employee_id=employee_id, employee_data=employee.model_dump(exclude_unset=True))

@app.post("/employees/{employee_id}/upload-face")
async def upload_employee_face(employee_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    db_emp = crud.get_employee(db, employee_id)
    if not db_emp:
        raise HTTPException(status_code=404, detail="Xodim topilmadi")
    
    import face_service
    incoming_bytes = await file.read()
    base64_str = "data:image/jpeg;base64," + base64.b64encode(incoming_bytes).decode('utf-8')
        
    crud.update_employee_face_id(db, employee_id, base64_str)
    return {"detail": "Yuz muvaffaqiyatli saqlandi", "faceIdImage": "Base64 saqlandi"}

@app.get("/face/{employee_id}")
def get_employee_face(employee_id: str, db: Session = Depends(get_db)):
    db_emp = crud.get_employee(db, employee_id)
    if not db_emp or not db_emp.faceIdImage:
        raise HTTPException(status_code=404, detail="Rasm topilmadi")
    
    img_data = db_emp.faceIdImage
    if img_data.startswith("data:image"):
        # Base64 dan decode qilish
        header, encoded = img_data.split(",", 1)
        img_bytes = base64.b64decode(encoded)
        return Response(content=img_bytes, media_type="image/jpeg")
    
    # Eskicha fayl tizimidan o'qish
    if not os.path.exists(img_data):
        raise HTTPException(status_code=404, detail="Rasm topilmadi")
    return FileResponse(img_data)

@app.get("/employees/", response_model=List[schemas.EmployeeResponse])
def read_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    return crud.get_employees(db, skip=skip, limit=limit)

@app.get("/employees/me/", response_model=schemas.EmployeeResponse)
def read_users_me(current_user: models.Employee = Depends(get_current_user)):
    return current_user

# ================= ATTENDANCE =================
@app.post("/attendances/", response_model=schemas.AttendanceResponse)
def create_attendance(attendance: schemas.AttendanceCreate, db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    res = crud.create_attendance(db=db, attendance=attendance)
    state = "Kirdi" if attendance.checkInTime else "Ketdi"
    crud.create_action_log(db, current_user.id, "DAVOMAT", f"Ishga {state} qayd etildi")
    return res

@app.get("/attendances/", response_model=List[schemas.AttendanceResponse])
def read_attendances(date: str, db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    return crud.get_attendances_by_date(db, date=date)

@app.post("/attendances/verify-face")
async def verify_attendance_face(employee_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    db_emp = crud.get_employee(db, employee_id)
    if not db_emp:
        raise HTTPException(status_code=404, detail="Xodim topilmadi")
    if not db_emp.faceIdImage:
        raise HTTPException(status_code=400, detail="Xodimning bazada yuzi yo'q. Avval yuzingizni saqlang.")
    
    import face_service
    import base64
    incoming_bytes = await file.read()
    
    # Agar rostdan ham bazada mutlaqo rasm yo'q bo'lsa, o'zini o'zi shu rasm bilan yaratib oladi.
    if not db_emp.faceIdImage or db_emp.faceIdImage.strip() == "":
        base64_str = "data:image/jpeg;base64," + base64.b64encode(incoming_bytes).decode('utf-8')
        crud.update_employee_face_id(db, employee_id, base64_str)
        return {"verified": True, "note": "Yuz bazaga abadiy saqlandi"}
        
    try:
        is_verified = face_service.verify_face(db_emp.faceIdImage, incoming_bytes)
        return {"verified": is_verified}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ================= PRODUCTS & SUPPLY =================
@app.get("/products/", response_model=List[schemas.ProductResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_products(db, skip=skip, limit=limit)

@app.post("/products/", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    return crud.create_product(db=db, product=product)

from pydantic import BaseModel

class SupplyStatusUpdate(BaseModel):
    status: str
    receiptImage: Optional[str] = None
    productImage: Optional[str] = None

@app.get("/supply-requests/", response_model=List[schemas.SupplyRequestResponse])
def read_supply_requests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Barcha zayavkalarni ro'yxati, jo'natuvchi ma'lumotlari bilan
    reqs = crud.get_supply_requests(db, skip=skip, limit=limit)
    for r in reqs:
        emp = crud.get_employee(db, r.requesterId)
        if emp:
            r.requesterName = f"{emp.name} {emp.surname}".strip()
            r.requesterPhone = emp.phone
    return reqs

@app.post("/supply-requests/", response_model=schemas.SupplyRequestResponse)
def create_supply_request(req: schemas.SupplyRequestCreate, db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    new_req = crud.create_supply_request(db=db, request=req)
    emp = crud.get_employee(db, new_req.requesterId)
    if emp:
        new_req.requesterName = f"{emp.name} {emp.surname}".strip()
        new_req.requesterPhone = emp.phone
    return new_req

@app.put("/supply-requests/{request_id}/status", response_model=schemas.SupplyRequestResponse)
def update_supply_status(request_id: str, update_data: SupplyStatusUpdate, db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    res = crud.update_supply_request_status(
        db, 
        request_id, 
        update_data.status, 
        update_data.receiptImage, 
        update_data.productImage
    )
    if not res:
        raise HTTPException(status_code=404, detail="Zayavka topilmadi")
        
    emp = crud.get_employee(db, res.requesterId)
    if emp:
        res.requesterName = f"{emp.name} {emp.surname}".strip()
        res.requesterPhone = emp.phone
    return res

# ================= ORDERS =================
@app.get("/orders/", response_model=List[schemas.OrderResponse])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    return crud.get_orders(db, skip=skip, limit=limit)

@app.post("/orders/", response_model=schemas.OrderResponse)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    res = crud.create_order(db=db, order=order)
    crud.create_action_log(db, current_user.id, "YANGI_BUYURTMA", f"Mijoz {order.customerName} uchun buyurtma yaratildi")
    return res

@app.put("/orders/{order_id}", response_model=schemas.OrderResponse)
def update_order(order_id: str, order: schemas.OrderUpdate, db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    db_order = crud.update_order(db=db, order_id=order_id, order_data=order.model_dump(exclude_unset=True))
    if not db_order:
        raise HTTPException(status_code=404, detail="Order topilmadi")
    status_label = order.status if order.status else "Mavjud O'zgarish"
    crud.create_action_log(db, current_user.id, "BUYURTMA_YANGILANDI", f"Buyurtma xolati o'zgardi/Tahrirlandi")
    return db_order

@app.delete("/orders/{order_id}")
def delete_order(order_id: str, db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    # Qo'shimcha xavfsizlik (O'chiruvchi uni yaratgan bo'lishi yoki Direktor bo'lishi kerak):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
        
    if db_order.creatorId != current_user.id and current_user.roleTitle.lower() != "direktor":
        raise HTTPException(status_code=403, detail="Siz faqat o'zingiz yaratgan buyurtmani o'chira olasiz!")
        
    if db_order.status != "readyForDelivery":
        raise HTTPException(status_code=400, detail="Faqat kutilayotgan buyurtmalarni o'chirish mumkin!")

    deleted = crud.delete_order(db=db, order_id=order_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Xatolik yuz berdi")
    crud.create_action_log(db, current_user.id, "BUYURTMA_BEKOR", f"{db_order.customerName} ning zakazi umuman o'chirib tashlandi")
    return {"detail": "Muvaffaqiyatli o'chirildi"}

# ================= ACTION LOGS =================
@app.get("/actions/", response_model=List[schemas.ActionLogResponse])
def read_actions(employee_id: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    return crud.get_action_logs(db, employee_id=employee_id, skip=skip, limit=limit)

# ================= FINANCE (MOLIYA) =================
@app.get("/expenses/", response_model=List[schemas.ExpenseResponse])
def get_expenses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_expenses(db, skip=skip, limit=limit)

@app.post("/expenses/", response_model=schemas.ExpenseResponse)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    return crud.create_expense(db, expense=expense, cashierId=current_user.id)

@app.get("/shifts/", response_model=List[schemas.CashShiftResponse])
def get_shifts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_cash_shifts(db, skip=skip, limit=limit)

@app.post("/shifts/", response_model=schemas.CashShiftResponse)
def create_shift(shift: schemas.CashShiftCreate, db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    return crud.create_cash_shift(db, shift=shift, cashierId=current_user.id)

@app.put("/orders/{order_id}/pay", response_model=schemas.OrderResponse)
def pay_order(order_id: str, db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    res = crud.update_order_is_paid(db, order_id=order_id)
    if not res:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    return res

@app.get("/")
def read_root():
    return {"message": "Dastur ishga tushdi", "docs": "/docs", "status": "online"}

# ================= SHIFTS SCHEDULE =================
@app.post("/shifts/schedule/", response_model=schemas.ShiftScheduleOut)
def assign_shift(schedule: schemas.ShiftScheduleCreate, db: Session = Depends(get_db)):
    return crud.create_shift_schedule(db, schedule)

@app.get("/shifts/schedule/{date}", response_model=List[schemas.ShiftScheduleOut])
def get_schedules_by_date(date: str, db: Session = Depends(get_db)):
    return crud.get_shift_schedules(db, date=date)

# ================= NOTIFICATIONS =================
@app.get("/notifications/", response_model=List[schemas.AppNotificationOut])
def get_my_notifications(db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    return crud.get_unread_notifications(db, current_user.id)

@app.put("/notifications/{notif_id}/read")
def read_notification(notif_id: int, db: Session = Depends(get_db)):
    success = crud.mark_notification_read(db, notif_id)
    return {"success": success}

# ================= LIVE GPS TRACKING =================
@app.post("/location/update")
def update_my_location(loc: schemas.LocationUpdate, db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    crud.update_live_location(db, current_user.id, loc.lat, loc.lng)
    return {"status": "ok"}

@app.get("/location/live", response_model=List[schemas.LiveLocationOut])
def get_all_live_locations(db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    return crud.get_live_locations(db)

# ================= VIDEO MEETINGS =================
@app.post("/meetings/", response_model=schemas.MeetingOut)
def create_new_meeting(meeting: schemas.MeetingCreate, db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    if current_user.roleTitle.lower() not in ["direktor", "hr"]:
        raise HTTPException(status_code=403, detail="Faqat Direktor yoki HR majlis yarata oladi!")
    return crud.create_meeting(db, meeting, current_user.id)

@app.get("/meetings/my", response_model=List[schemas.MeetingOut])
def retrieve_my_meetings(db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    return crud.get_my_meetings(db, current_user.id)

# ================= BACKGROUND TASKS =================
async def check_shifts_bg_task():
    while True:
        now = datetime.now()
        if now.hour == 16 and now.minute == 0:
            db = SessionLocal()
            try:
                today_str = now.strftime("%Y-%m-%d")
                shifts = crud.get_shift_schedules(db, date=today_str)
                for s in shifts:
                    if s.shift_type == "2-smena":
                        exists = db.query(models.AppNotification).filter(
                            models.AppNotification.employee_id == s.employee_id,
                            models.AppNotification.message.like("%Siz bugun 2-smenada%"),
                            models.AppNotification.created_at >= now.replace(hour=0, minute=0, second=0)
                        ).first()
                        if not exists:
                            crud.create_notification(db, s.employee_id, "Siz bugun 2-smenada ishlaysiz. Smenangiz boshlanmoqda!")
            except Exception as e:
                print("Error in bg task:", e)
            finally:
                db.close()
            await asyncio.sleep(60)
        else:
            await asyncio.sleep(20)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(check_shifts_bg_task())

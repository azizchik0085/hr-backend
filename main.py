from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

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

@app.get("/employees/", response_model=List[schemas.EmployeeResponse])
def read_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    return crud.get_employees(db, skip=skip, limit=limit)

@app.get("/employees/me/", response_model=schemas.EmployeeResponse)
def read_users_me(current_user: models.Employee = Depends(get_current_user)):
    return current_user

# ================= ATTENDANCE =================
@app.post("/attendances/", response_model=schemas.AttendanceResponse)
def create_attendance(attendance: schemas.AttendanceCreate, db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    return crud.create_attendance(db=db, attendance=attendance)

@app.get("/attendances/", response_model=List[schemas.AttendanceResponse])
def read_attendances(date: str, db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    return crud.get_attendances_by_date(db, date=date)

# ================= PRODUCTS & SUPPLY =================
@app.get("/products/", response_model=List[schemas.ProductResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_products(db, skip=skip, limit=limit)

@app.post("/products/", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    return crud.create_product(db=db, product=product)

@app.get("/supply-requests/", response_model=List[schemas.SupplyRequestResponse])
def read_supply_requests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_supply_requests(db, skip=skip, limit=limit)

@app.post("/supply-requests/", response_model=schemas.SupplyRequestResponse)
def create_supply_request(req: schemas.SupplyRequestCreate, db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    # Tekshiramiz: Hozirgi foydalanuvchi bilan so'rov egasi birhilmi yoki director?
    if req.requesterId != current_user.id and current_user.roleTitle.lower() != "direktor":
        raise HTTPException(status_code=403, detail="Ruxsat yo'q. Faqat o'zingiz nomingizdan yoki Direktor nomidan chizishingiz mumkin.")
    return crud.create_supply_request(db=db, request=req)

@app.post("/supply-requests/{request_id}/complete")
def complete_supply_request(request_id: str, db: Session = Depends(get_db), current_user: models.Employee = Depends(get_current_user)):
    if current_user.roleTitle.lower() not in ["direktor", "ombor mudiri"]:
        raise HTTPException(status_code=403, detail="Faqat Ombor Mudiri yoki Direktor bajarishi mumkin.")
    res = crud.mark_supply_request_completed(db, request_id)
    if not res:
        raise HTTPException(status_code=404, detail="Zayavka topilmadi")
    return {"detail": "Muvaffaqiyatli", "status": "completed"}

@app.get("/")
def read_root():
    return {"message": "Dastur ishga tushdi", "docs": "/docs", "status": "online"}

import uuid
from database import SessionLocal, engine
import models
from auth import get_password_hash

def seed_data():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Director bor yoki yo'qligini tekshiramiz
    admin = db.query(models.Employee).filter(models.Employee.login == "admin").first()
    if not admin:
        print("Director (admin) yaratilmoqda...")
        new_admin = models.Employee(
            id=f"EMP-{uuid.uuid4().hex[:8].upper()}",
            name="Asosiy",
            surname="Boshqaruvchi",
            roleTitle="Direktor",
            login="admin",
            hashed_password=get_password_hash("123"),
            isApproved=True,
            isActive=True,
            requireGPS=False,
            requireFaceID=False
        )
        db.add(new_admin)
        db.commit()
        print("Muvaffaqiyatli: login = admin, parol = 123")
    else:
        print("Admin allaqachon mavjud.")
    db.close()

if __name__ == "__main__":
    seed_data()

from database import SessionLocal, engine
from sqlalchemy import text
import models

def fix_columns():
    db = SessionLocal()
    try:
        # Yangi jadvallarni yaratish (Yangi Kassir jadvallari: Expense, CashShift)
        models.Base.metadata.create_all(bind=engine)
        
        # Order jadvaliga yangi isPaid ustunini qo'shish (Xatoliksiz ishlashi uchun)
        try:
            db.execute(text('ALTER TABLE orders ADD COLUMN "isPaid" BOOLEAN DEFAULT FALSE;'))
            db.commit()
            print("orders jadvaliga isPaid ustuni qo'shildi!")
        except Exception as add_e:
            db.rollback()
            print("isPaid ustuni allaqachon mavjud yoki xatolik:", add_e)
        
        print("Barcha Kassa (Moliya) jadvallari yangi Arxitektura bo'yicha muvaffaqiyatli tiklandi!")
    except Exception as e:
        db.rollback()
        print("Katta xatolik:", e)
    finally:
        db.close()

if __name__ == "__main__":
    fix_columns()

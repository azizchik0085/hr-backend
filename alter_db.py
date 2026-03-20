from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE orders ADD COLUMN productImage VARCHAR;"))
        conn.execute(text("ALTER TABLE orders ADD COLUMN receiptImage VARCHAR;"))
        conn.commit()
        print("Success")
    except Exception as e:
        print("Error:", e)

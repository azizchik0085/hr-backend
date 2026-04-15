import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from database import SessionLocal
from models import Product

def populate():
    db = SessionLocal()

    products = [
        Product(
            id="P-001",
            name="Premium Qora Kraska",
            brand="Bo'yoqlar",
            description="Tashqi va ichki fasad uchun qora bo'yoq 5L.",
            price=45000,
            currentStock=15,
            minRequiredStock=20
        ),
        Product(
            id="P-002",
            name="Beton uchun Shpatlevka",
            brand="Quruq Qorishmalar",
            description="Devorlarni tekislash uchun mustahkam vosita 20kg",
            price=20000,
            currentStock=120,
            minRequiredStock=50
        ),
        Product(
            id="P-003",
            name="Oq Emulsiya 10kg",
            brand="Bo'yoqlar",
            description="Tez quriydigan hidsiz Oq emulsiya.",
            price=120000,
            currentStock=8,
            minRequiredStock=10
        ),
        Product(
            id="P-004",
            name="Rolik kisti (Kattasi)",
            brand="Asboblar",
            description="Katta yuza bo'yash asboblari",
            price=15000,
            currentStock=200,
            minRequiredStock=30
        )
    ]

    for p in products:
        existing = db.query(Product).filter(Product.id == p.id).first()
        if not existing:
            db.add(p)
            print(f"Added {p.name}")
        else:
            print(f"Already exists {p.name}")

    db.commit()
    db.close()
    print("Database data updated!")

if __name__ == "__main__":
    populate()

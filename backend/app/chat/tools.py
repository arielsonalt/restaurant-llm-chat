from sqlalchemy.orm import Session
from app.db import models

def get_hours() -> str:
    return "Mon-Sun 11:00-23:00"

def get_location() -> str:
    return "123 Main St, Downtown"

def search_menu(db: Session, query: str) -> list[dict]:
    q = db.query(models.MenuItem).filter(models.MenuItem.active.is_(True))
    if query:
        q = q.filter(models.MenuItem.name.ilike(f"%{query}%"))
    items = q.limit(10).all()
    return [{"id": i.id, "name": i.name, "price": float(i.price), "category": i.category} for i in items]

def get_item(db: Session, item_id: int) -> dict | None:
    i = db.query(models.MenuItem).filter(models.MenuItem.id == item_id, models.MenuItem.active.is_(True)).first()
    if not i:
        return None
    return {"id": i.id, "name": i.name, "description": i.description, "allergens": i.allergens, "price": float(i.price)}

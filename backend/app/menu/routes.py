from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from app.menu.schemas import MenuItemOut

router = APIRouter(prefix="/menu", tags=["menu"])

@router.get("", response_model=list[MenuItemOut])
def list_menu(db: Session = Depends(get_db)):
    items = db.query(models.MenuItem).filter(models.MenuItem.active.is_(True)).order_by(models.MenuItem.category).all()
    return [
        MenuItemOut(
            id=i.id, category=i.category, name=i.name,
            description=i.description, allergens=i.allergens, price=float(i.price)
        )
        for i in items
    ]

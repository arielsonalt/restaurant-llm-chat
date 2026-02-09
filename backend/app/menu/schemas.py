from pydantic import BaseModel

class MenuItemOut(BaseModel):
    id: int
    category: str
    name: str
    description: str | None
    allergens: str | None
    price: float

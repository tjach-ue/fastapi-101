from datetime import datetime
from typing import Any

from passlib.context import CryptContext
from pydantic import BaseModel
from pydantic import validator

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


class Food(BaseModel):
    """Bite 02"""

    id: int
    name: str
    serving_size: str
    kcal_per_serving: int
    protein_grams: float
    fibre_grams: float = 0


# Write the User and FoodEntry models here ...

class User(BaseModel):
    id: int
    username: str
    password: str

    @validator('password')
    def hash_password(cls, passw: str):
        return get_password_hash(password=passw)


class User2(BaseModel):
    id: int
    username: str
    password: str

    def __init__(self, **data: Any):
        data["password"] = get_password_hash(data["password"])
        super().__init__(**data)


class FoodEntry(BaseModel):
    """Bite 02"""

    id: int
    user: User
    food: Food
    date_added: datetime = datetime.now()
    number_servings: float

    @property
    def total_calories(self) -> float:
        return self.number_servings * self.food.kcal_per_serving

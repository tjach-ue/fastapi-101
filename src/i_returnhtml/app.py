from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates

# https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
# We'll export authentication further in a later Bite
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


class Food(BaseModel):
    id: int
    name: str
    serving_size: str
    kcal_per_serving: int
    protein_grams: float
    fibre_grams: float = 0


class User(BaseModel):
    id: int
    username: str
    password: str

    def __init__(self, **data: Any):
        data["password"] = get_password_hash(data["password"])
        super().__init__(**data)


class FoodEntry(BaseModel):
    id: int
    user: User
    food: Food
    date_added: datetime = datetime.now()
    number_servings: float

    @property
    def total_calories(self):
        return self.food.kcal_per_serving * self.number_servings


app = FastAPI()

food_log: Dict[int, FoodEntry] = {}

templates = Jinja2Templates(directory="templates")



@app.post("/", status_code=201)
async def create_food_entry(entry: FoodEntry):
    """Previous Bite and used in test"""
    food_log[entry.id] = entry
    return entry


@app.get("/{username}", response_class=HTMLResponse)
async def show_foods_for_user(request: Request, username: str):
    # 1. extract foods for user using the food_log dict
    # 2. build up the embedded html string
    # 3. return an HTMLResponse (with the html content and status code 200)
    food_entries = [{"food_name": f.food.name, "date_added": f.date_added,
                     "number_servings": f.number_servings, "serving_size": f.food.serving_size,
                     "total_calories": f.total_calories
                     } for f in food_log.values() if f.user.username == username]
    return templates.TemplateResponse("index.html", {"request": request, "username": username, "food_entries": food_entries})
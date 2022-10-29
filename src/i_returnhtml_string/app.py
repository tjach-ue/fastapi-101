from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, BaseLoader
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates

# https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
# We'll export authentication further in a later Bite
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

HTML_TEMPLATE = '''
<!doctype html>

<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Food log for {{ username }}</title>
</head>

<body>
    <table>
        <thead>
            <th>Food</th>
            <th>Added</th>
            <th>Servings</th>
            <th>Calories (kcal)</th>
        </thead>
        <tbody>
    {% for item in food_entries %}
            <tr>
                <td>{{ item.food_name }}</td>
                <td>{{ item.date_added }}</td>
                <td>{{ item.number_servings }} x {{ item.serving_size }}</td>
                <td>{{ item.total_calories }}</td>
            </tr>
    {% endfor %}
        </tbody>
    </table>

</body>
</html>
'''

template = Environment(loader=BaseLoader()).from_string(HTML_TEMPLATE)


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
    return template.render({"request": request, "username": username, "food_entries": food_entries})
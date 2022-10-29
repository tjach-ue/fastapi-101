from typing import Dict, Union

from fastapi import FastAPI
from pydantic import BaseModel


class Food(BaseModel):
    id: int
    name: str
    serving_size: str
    kcal_per_serving: int
    protein_grams: float
    fibre_grams: Union[float, None] = 0.0


app = FastAPI()
foods: Dict[int, Food] = {}


@app.post("/", status_code=201)
async def create_food(food: Food):
    foods[food.id] = food
    return food


@app.get("/", status_code=200)
async def read_foods():
    return list(foods.values())


@app.get("/{food_id}", status_code=200)
async def read_foods(food_id: int):
    return foods[food_id]

# write the two Read endpoints
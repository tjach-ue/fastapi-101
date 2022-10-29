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

# write the Create endpoint

@app.post("/", status_code=201)
def post_food(food: Food):
    foods[food.id] = food
    return food

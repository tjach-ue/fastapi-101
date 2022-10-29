from typing import Dict, List

from fastapi import Depends, FastAPI, HTTPException

from k_proper_dir_structure.app.internal.user_db import get_current_active_user
from k_proper_dir_structure.app.models.FoodModels import FoodEntry
from k_proper_dir_structure.app.models.UserModels import User
from routers.auth import auth_router

food_log: Dict[int, FoodEntry] = {}

app = FastAPI()
app.include_router(auth_router)

@app.post("/", status_code=201)
async def create_food_entry(entry: FoodEntry, current_user: User = Depends(get_current_active_user)):
    if current_user.id != entry.user.id:
        raise HTTPException(status_code=400, detail="Can only add food for current user")
    food_log[entry.id] = entry
    return entry


@app.get("/", response_model=List[FoodEntry])
async def get_foods_for_user(current_user: User = Depends(get_current_active_user)):
    return [
        food_entry
        for food_entry in food_log.values()
        if food_entry.user.id == current_user.id
    ]


@app.put("/{entry_id}", response_model=FoodEntry)
async def update_food_entry(entry_id: int, new_entry: FoodEntry, current_user: User = Depends(get_current_active_user)):
    if entry_id not in food_log:
        raise HTTPException(status_code=404, detail="Food entry not found")
    if current_user.id != food_log.get(entry_id).user.id:
        raise HTTPException(status_code=400, detail="Food entry not owned by you")
    food_log[entry_id] = new_entry

    return new_entry


@app.delete("/{entry_id}", response_model=Dict[str, bool])
async def delete_food_entry(entry_id: int, current_user: User = Depends(get_current_active_user)):
    if entry_id not in food_log:
        raise HTTPException(status_code=404, detail="Food entry not found")
    if current_user.id != food_log.get(entry_id).user.id:
        raise HTTPException(status_code=400, detail="Food entry not owned by you")

    del food_log[entry_id]

    return {"ok": True}

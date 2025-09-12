from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class WorkoutCreate(BaseModel):
    workout_date: date
    exercise: str
    variant: Optional[str] = None
    reps: int = Field(gt=0)
    weight: Optional[float] = None
    rpe: Optional[float] = None
    notes: Optional[str] = None
    team_id: Optional[str] = None  # uuid

class WorkoutOut(WorkoutCreate):
    id: int

class TeamCreate(BaseModel):
    name: str

class TeamOut(BaseModel):
    id: str
    name: str
    invite_code: str

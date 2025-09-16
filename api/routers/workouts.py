from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from ..deps import get_supabase, get_current_user_id
from ..models import WorkoutCreate, WorkoutOut

router = APIRouter(prefix="/api/py/workouts", tags=["workouts"])

@router.post("", response_model=WorkoutOut)
def create_workout(
    payload: WorkoutCreate,
    user_id: str = Depends(get_current_user_id),
    supa: Client = Depends(get_supabase),
):
    data = {**payload.model_dump(), "user_id": user_id}
    # Kirim JWT user agar RLS menilai auth.uid() = user
    res = supa.table("workout_entries").insert(data).execute()
    if not res.data:
        raise HTTPException(400, "Insert failed")
    row = res.data[0]
    return WorkoutOut(**row)

@router.get("", response_model=list[WorkoutOut])
def list_my_workouts(
    from_date: str | None = None,
    to_date: str | None = None,
    user_id: str = Depends(get_current_user_id),
    supa: Client = Depends(get_supabase),
):
    q = supa.table("workout_entries").select("*").eq("user_id", user_id)
    if from_date:
        q = q.gte("workout_date", from_date)
    if to_date:
        q = q.lte("workout_date", to_date)
    res = q.order("workout_date", desc=False).limit(500).execute()
    return res.data or []

@router.delete("/{entry_id}")
def delete_workout(
    entry_id: int,
    user_id: str = Depends(get_current_user_id),
    supa: Client = Depends(get_supabase),
):
    res = supa.table("workout_entries").delete().eq("id", entry_id).eq("user_id", user_id).execute()
    return {"deleted": len(res.data or [])}

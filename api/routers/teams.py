import secrets, string
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from ..deps import get_supabase, get_current_user_id
from ..models import TeamCreate, TeamOut

router = APIRouter(prefix="/api/py/teams", tags=["teams"])

def _gen_code(n=8):
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(n))

@router.post("", response_model=TeamOut)
def create_team(
    payload: TeamCreate,
    user_id: str = Depends(get_current_user_id),
    supa: Client = Depends(get_supabase),
):
    code = _gen_code()
    team_res = supa.table("teams").insert({
        "name": payload.name, "owner_id": user_id, "invite_code": code
    }).select("*").single().execute()
    team = team_res.data
    # auto-add owner as member
    supa.table("team_members").insert({
        "team_id": team["id"], "user_id": user_id, "role": "owner"
    }).execute()
    return {"id": team["id"], "name": team["name"], "invite_code": team["invite_code"]}

@router.post("/join/{invite_code}")
def join_team(
    invite_code: str,
    user_id: str = Depends(get_current_user_id),
    supa: Client = Depends(get_supabase),
):
    team = supa.table("teams").select("*").eq("invite_code", invite_code).single().execute().data
    if not team:
        raise HTTPException(404, "Invalid invite code")
    # upsert membership
    supa.table("team_members").upsert({
        "team_id": team["id"], "user_id": user_id, "role": "member"
    }, on_conflict="team_id,user_id").execute()
    return {"joined_team_id": team["id"]}

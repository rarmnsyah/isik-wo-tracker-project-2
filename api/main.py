from fastapi import FastAPI, APIRouter
from .routers import workouts, teams, webhook

app = FastAPI(title="isik-wo-project API")

@app.get("")
async def read_category_by_query():
    role_to_return ="mantap"
    return role_to_return

@app.get("/health")
def health():
    return {"ok": True}

app.include_router(webhook.router)
app.include_router(workouts.router)
app.include_router(teams.router)

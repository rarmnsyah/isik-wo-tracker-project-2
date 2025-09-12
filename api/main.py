from fastapi import FastAPI
from .routers import workouts, teams

app = FastAPI(title="isik-wo-project API")

@app.get("/health")
def health():
    return {"ok": True}

app.include_router(workouts.router)
app.include_router(teams.router)

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from app.schemas import TripRequest, TripPlan, POI
from app.planner.heuristic import plan_trip
from app.utils.ics import format_as_ics

app = FastAPI(title="Smart AI Trip Planner", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


DATA_PATH = Path(__file__).resolve().parent / "data" / "pois.json"
STATIC_DIR = Path(__file__).resolve().parent / "static"


@app.get("/health")
async def health() -> dict:
    return {"ok": True}


def load_pois() -> List[POI]:
    if not DATA_PATH.exists():
        raise RuntimeError(f"POI dataset not found at {DATA_PATH}")
    payload = json.loads(DATA_PATH.read_text())
    return [POI(**p) for p in payload]


@app.post("/api/plan", response_model=TripPlan)
async def api_plan(req: TripRequest) -> TripPlan:
    try:
        pois = load_pois()
        plan = plan_trip(req, pois)
        return plan
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/plan.ics")
async def api_plan_ics(req: TripRequest):
    pois = load_pois()
    plan = plan_trip(req, pois)
    ics = format_as_ics(plan)
    return PlainTextResponse(content=ics, media_type="text/calendar")


@app.get("/")
async def index() -> FileResponse:
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(index_path)

# Mount static directory for assets
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

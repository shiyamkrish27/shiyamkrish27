from __future__ import annotations

from datetime import date

from app.planner.heuristic import plan_trip
from app.schemas import TripRequest, Preferences
from app.main import load_pois


def test_plan_generates_days():
    req = TripRequest(city="Paris", start_date=date(2025, 5, 1), end_date=date(2025, 5, 2))
    pois = load_pois()
    plan = plan_trip(req, pois)
    assert len(plan.days) == 2
    assert sum(len(d.items) for d in plan.days) >= 1

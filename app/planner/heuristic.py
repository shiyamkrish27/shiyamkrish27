from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, date, time
from typing import Iterable, List, Tuple, Optional

from app.schemas import TripRequest, TripPlan, DayPlan, ItineraryItem, POI


@dataclass
class Candidate:
    poi: POI
    score: float


def haversine_minutes(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
    # Rough driving/walking time proxy; 1 deg ~ 111km, average 30km/h -> minutes
    from math import radians, cos, sin, asin, sqrt

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    minutes = int(km / 3.0 * 60)  # ~3km per 60 min walking, very rough
    return max(5, min(120, minutes))


def score_poi(poi: POI, preferred_categories: List[str]) -> float:
    base = 1.0 if poi.category in preferred_categories else 0.6
    length_penalty = max(0.5, min(1.0, 120 / max(30, poi.typical_duration_mins)))
    return base * length_penalty


def generate_day_slots(req: TripRequest) -> List[Tuple[date, datetime, datetime]]:
    current = req.start_date
    slots: List[Tuple[date, datetime, datetime]] = []
    while current <= req.end_date:
        start_dt = datetime.combine(current, req.preferences.start_time)
        end_dt = datetime.combine(current, req.preferences.end_time)
        if end_dt > start_dt:
            slots.append((current, start_dt, end_dt))
        current += timedelta(days=1)
    return slots


def plan_trip(req: TripRequest, pois: Iterable[POI]) -> TripPlan:
    day_slots = generate_day_slots(req)

    duration_factor = {"relaxed": 0.6, "balanced": 0.8, "packed": 1.0}[req.preferences.pace]

    remaining = [Candidate(poi=p, score=score_poi(p, req.preferences.categories)) for p in pois if p.city.lower() == req.city.lower()]
    remaining.sort(key=lambda c: c.score, reverse=True)

    days: List[DayPlan] = []
    last_location: Optional[Tuple[float, float]] = None

    for day, start_dt, end_dt in day_slots:
        time_cursor = start_dt
        items: List[ItineraryItem] = []
        total_travel = 0

        origin = last_location
        if req.starting_location and origin is None:
            origin = (req.starting_location.lat, req.starting_location.lon)

        while time_cursor < end_dt and remaining:
            # Choose next by a mix of score and proximity
            best_idx = -1
            best_value = -1e9
            for idx, cand in enumerate(remaining[:20]):  # only consider top 20 to keep it fast
                travel = 15
                if origin is not None:
                    travel = haversine_minutes(origin[0], origin[1], cand.poi.lat, cand.poi.lon)
                value = cand.score - 0.01 * travel
                if value > best_value:
                    best_value = value
                    best_idx = idx

            if best_idx < 0:
                break

            cand = remaining.pop(best_idx)
            travel = 15
            if origin is not None:
                travel = haversine_minutes(origin[0], origin[1], cand.poi.lat, cand.poi.lon)

            visit_minutes = int(cand.poi.typical_duration_mins * duration_factor)
            if time_cursor + timedelta(minutes=travel + visit_minutes) > end_dt:
                # not enough time remaining this day; try next day
                remaining.insert(best_idx, cand)
                break

            start_visit = time_cursor + timedelta(minutes=travel)
            end_visit = start_visit + timedelta(minutes=visit_minutes)

            items.append(
                ItineraryItem(
                    day=day,
                    start=start_visit,
                    end=end_visit,
                    poi_id=cand.poi.id,
                    poi_name=cand.poi.name,
                    lat=cand.poi.lat,
                    lon=cand.poi.lon,
                    travel_minutes=travel,
                )
            )

            total_travel += travel
            time_cursor = end_visit
            origin = (cand.poi.lat, cand.poi.lon)

        last_location = origin
        days.append(DayPlan(date=day, items=items, total_travel_minutes=total_travel))

    summary = f"Planned {sum(len(d.items) for d in days)} stops across {len(days)} day(s) in {req.city}."
    return TripPlan(request=req, days=days, summary=summary)

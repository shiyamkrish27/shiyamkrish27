from __future__ import annotations

from datetime import date, time, datetime
from typing import List, Optional, Literal

from pydantic import BaseModel, Field


class Location(BaseModel):
    name: str
    lat: float
    lon: float


class Preferences(BaseModel):
    categories: List[str] = Field(default_factory=lambda: ["landmark", "museum", "park"])  # preferred categories
    pace: Literal["relaxed", "balanced", "packed"] = "balanced"
    start_time: time = time(hour=9, minute=0)
    end_time: time = time(hour=18, minute=0)


class TripRequest(BaseModel):
    city: str
    start_date: date
    end_date: date
    preferences: Preferences = Field(default_factory=Preferences)
    starting_location: Optional[Location] = None


class POI(BaseModel):
    id: str
    city: str
    name: str
    lat: float
    lon: float
    category: str
    typical_duration_mins: int = 90


class ItineraryItem(BaseModel):
    day: date
    start: datetime
    end: datetime
    poi_id: str
    poi_name: str
    lat: float
    lon: float
    travel_minutes: int = 0
    notes: Optional[str] = None


class DayPlan(BaseModel):
    date: date
    items: List[ItineraryItem] = Field(default_factory=list)
    total_travel_minutes: int = 0


class TripPlan(BaseModel):
    request: TripRequest
    days: List[DayPlan]
    summary: Optional[str] = None

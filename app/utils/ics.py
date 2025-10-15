from __future__ import annotations

from datetime import datetime
from typing import Iterable

from app.schemas import TripPlan, ItineraryItem


def format_as_ics(plan: TripPlan) -> str:
    def fmt_dt(dt: datetime) -> str:
        return dt.strftime("%Y%m%dT%H%M%S")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//SmartTripPlanner//EN",
    ]

    for day in plan.days:
        for item in day.items:
            lines += [
                "BEGIN:VEVENT",
                f"UID:{item.poi_id}-{fmt_dt(item.start)}",
                f"DTSTART:{fmt_dt(item.start)}",
                f"DTEND:{fmt_dt(item.end)}",
                f"SUMMARY:{item.poi_name}",
                f"DESCRIPTION:Visit {item.poi_name}",
                "END:VEVENT",
            ]

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"

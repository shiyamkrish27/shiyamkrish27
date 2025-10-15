## Smart AI Trip Planner

A simple FastAPI-based project that creates day-by-day itineraries from a sample Points-of-Interest dataset with adjustable preferences, plus ICS calendar export and a lightweight static UI.

### Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000/` to use the UI.

### API

- `GET /health` – health check
- `POST /api/plan` – body is `TripRequest`, returns `TripPlan`
- `POST /api/plan.ics` – body is `TripRequest`, returns ICS text

Minimal `TripRequest` example:

```json
{
  "city": "Paris",
  "start_date": "2025-05-01",
  "end_date": "2025-05-02",
  "preferences": { "pace": "balanced", "categories": ["landmark","museum","park"], "start_time": "09:00", "end_time": "18:00" }
}
```

### Tests

```bash
pip install -r requirements.txt
pytest
```

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
import datetime
from app.database import get_db_cursor
from app.schemas import EventResponse, EventCreate

router = APIRouter(prefix="/api/events", tags=["Events"])

@router.get("", response_model=List[EventResponse])
def list_events(
    date: Optional[datetime.date] = Query(None, description="Filter events by date"),
    search: Optional[str] = Query(None, description="Search event name")
):
    """Retrieves recorded events, optionally filtered by date or name."""
    query = "SELECT event_id, event_name, event_date, duration_hours, COALESCE(start_time, '') as start_time FROM events WHERE 1=1"
    params = []

    if date:
        query += " AND event_date = %s"
        params.append(date)

    if search:
        query += " AND LOWER(event_name) LIKE %s"
        params.append(f"%{search.strip().lower()}%")

    query += " ORDER BY event_date DESC, event_id DESC"

    with get_db_cursor(dict_cursor=True) as cur:
        cur.execute(query, tuple(params))
        rows = cur.fetchall()

    return rows

@router.get("/dates", response_model=List[str])
def list_event_dates():
    """Returns list of distinct dates that have recorded events."""
    query = "SELECT DISTINCT event_date FROM events ORDER BY event_date DESC"
    with get_db_cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
    return [r[0].strftime("%Y-%m-%d") for r in rows if r[0]]

@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: int):
    """Retrieves an event by its ID."""
    with get_db_cursor(dict_cursor=True) as cur:
        cur.execute("SELECT event_id, event_name, event_date, duration_hours, COALESCE(start_time, '') as start_time FROM events WHERE event_id = %s", (event_id,))
        event = cur.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found.")
        return event

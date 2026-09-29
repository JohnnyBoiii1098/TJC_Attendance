from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from app.database import get_db_cursor
from app.schemas import (
    SaveAttendanceRequest,
    AttendanceRosterResponse,
    AttendanceRosterItem,
    EventResponse
)
from app.routers.auth import require_admin_pin

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])

@router.post("/save", status_code=status.HTTP_201_CREATED)
def save_attendance(
    payload: SaveAttendanceRequest,
    _auth: bool = Depends(require_admin_pin)
):
    """
    Saves an attendance session:
    1. Creates a new event record in 'events'
    2. Batch inserts attendance statuses in 'attendance_logs'
    Protected by Admin PIN.
    """
    clean_name = payload.event_name.strip()
    if not clean_name:
        raise HTTPException(status_code=400, detail="Event name is required.")

    if not payload.records:
        raise HTTPException(status_code=400, detail="Attendance list cannot be empty.")

    try:
        with get_db_cursor(commit=True) as cur:
            # Insert the event
            cur.execute(
                """
                INSERT INTO events (event_name, event_date, duration_hours, start_time)
                VALUES (%s, %s, %s, %s)
                RETURNING event_id;
                """,
                (clean_name, payload.event_date, payload.duration_hours, (payload.start_time or "").strip())
            )
            event_id = cur.fetchone()[0]

            # Batch insert attendance logs
            insert_log_sql = """
            INSERT INTO attendance_logs (event_id, reg_no, is_present)
            VALUES (%s, %s, %s);
            """
            log_tuples = [(event_id, r.reg_no, r.is_present) for r in payload.records]
            cur.executemany(insert_log_sql, log_tuples)

            present_count = sum(1 for r in payload.records if r.is_present)
            absent_count = len(payload.records) - present_count

            return {
                "success": True,
                "event_id": event_id,
                "event_name": clean_name,
                "event_date": str(payload.event_date),
                "duration_hours": payload.duration_hours,
                "start_time": (payload.start_time or "").strip(),
                "total_records": len(payload.records),
                "present_count": present_count,
                "absent_count": absent_count,
                "message": f"Attendance successfully saved for '{clean_name}'."
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save attendance: {str(e)}")

@router.get("/event/{event_id}", response_model=AttendanceRosterResponse)
def get_event_attendance(event_id: int):
    """
    Retrieves the complete attendance roster and event info for a specific event.
    """
    with get_db_cursor(dict_cursor=True) as cur:
        # Fetch event
        cur.execute(
            "SELECT event_id, event_name, event_date, duration_hours, COALESCE(start_time, '') as start_time FROM events WHERE event_id = %s",
            (event_id,)
        )
        event_row = cur.fetchone()
        if not event_row:
            raise HTTPException(status_code=404, detail="Event not found.")

        # Fetch roster
        cur.execute(
            """
            SELECT s.reg_no, s.student_name, s.part, a.is_present
            FROM students s
            JOIN attendance_logs a ON s.reg_no = a.reg_no
            WHERE a.event_id = %s
            ORDER BY s.part, s.student_name ASC
            """,
            (event_id,)
        )
        rows = cur.fetchall()

    roster = [AttendanceRosterItem(**r) for r in rows]
    total_present = sum(1 for r in roster if r.is_present)
    total_absent = len(roster) - total_present

    return AttendanceRosterResponse(
        event=EventResponse(**event_row),
        roster=roster,
        total_present=total_present,
        total_absent=total_absent,
        total_students=len(roster)
    )

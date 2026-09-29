from fastapi import APIRouter, Query
from typing import Optional
import math
from app.database import get_db_cursor
from app.schemas import CreditsSummaryResponse, StudentCreditsItem

router = APIRouter(prefix="/api/credits", tags=["Credits"])

@router.get("", response_model=CreditsSummaryResponse)
def get_credits_ledger(
    part: Optional[str] = Query(None, description="Strict section/part isolation filter")
):
    """
    Calculates total hours attended and credits earned for all students or filtered by part.
    Calculation formula: credits = floor(total_hours / 30)
    """
    selected_filter = part or "All Parts"

    query = """
    SELECT 
        s.reg_no,
        s.student_name,
        s.part,
        COALESCE(SUM(ev.duration_hours), 0) AS total_hours
    FROM students s
    LEFT JOIN attendance_logs a ON s.reg_no = a.reg_no AND a.is_present = TRUE
    LEFT JOIN events ev ON a.event_id = ev.event_id
    """
    params = []

    if selected_filter != "All Parts":
        query += " WHERE s.part = %s"
        params.append(selected_filter)

    query += " GROUP BY s.reg_no, s.student_name, s.part ORDER BY s.part ASC, s.student_name ASC"

    with get_db_cursor(dict_cursor=True) as cur:
        cur.execute(query, tuple(params))
        rows = cur.fetchall()

    student_items = []
    for r in rows:
        hours = float(r["total_hours"])
        credits_earned = math.floor(abs(hours / 30))
        student_items.append(
            StudentCreditsItem(
                reg_no=r["reg_no"],
                student_name=r["student_name"].upper(),
                part=r["part"],
                total_hours=round(hours, 2),
                credits=credits_earned
            )
        )

    return CreditsSummaryResponse(
        filter_part=selected_filter,
        total_records=len(student_items),
        students=student_items
    )

from fastapi import APIRouter, HTTPException, Response, Query
from fastapi.responses import HTMLResponse
import io
import csv
import math
from app.database import get_db_cursor
from app.config import BRAND_NAVY, BRAND_GOLD

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/html/{event_id}", response_class=HTMLResponse)
def get_html_report(event_id: int):
    """Generates a clean, professional, and printable HTML report for an event."""
    with get_db_cursor(dict_cursor=True) as cur:
        cur.execute("SELECT event_name, event_date, duration_hours FROM events WHERE event_id = %s", (event_id,))
        event = cur.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found.")

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
        roster = cur.fetchall()

    present_count = sum(1 for r in roster if r["is_present"])
    absent_count = len(roster) - present_count

    table_rows = ""
    for r in roster:
        status_class = "present" if r["is_present"] else "absent"
        status_text = "Present" if r["is_present"] else "Absent"
        table_rows += f"""
        <tr>
            <td class="font-bold">{r['student_name'].upper()}</td>
            <td>{r['reg_no']}</td>
            <td>{r['part']}</td>
            <td class="{status_class}">{status_text}</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Report - {event['event_name']} ({event['event_date']})</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f9fafb;
            color: #111827;
            padding: 30px 20px;
            margin: 0;
        }}
        .report-card {{
            max-width: 850px;
            margin: auto;
            background: #ffffff;
            border-radius: 12px;
            padding: 35px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border: 1px solid #e5e7eb;
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid {BRAND_GOLD};
            padding-bottom: 20px;
            margin-bottom: 25px;
        }}
        .header h1 {{
            margin: 0;
            color: {BRAND_NAVY};
            font-size: 26px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .header h3 {{
            margin: 6px 0 0 0;
            color: {BRAND_GOLD};
            font-size: 16px;
            font-weight: 600;
        }}
        .meta-grid {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
            padding: 12px 18px;
            background-color: #f3f4f6;
            border-radius: 8px;
            font-size: 14px;
        }}
        .meta-item {{
            display: flex;
            gap: 6px;
        }}
        .meta-label {{
            font-weight: bold;
            color: #4b5563;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 10px 14px;
            border: 1px solid #e5e7eb;
            text-align: left;
            font-size: 14px;
        }}
        th {{
            background-color: {BRAND_NAVY};
            color: {BRAND_GOLD};
            font-weight: 600;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.5px;
        }}
        tr:nth-child(even) {{
            background-color: #f9fafb;
        }}
        .present {{
            color: #16a34a;
            font-weight: bold;
        }}
        .absent {{
            color: #dc2626;
            font-weight: bold;
        }}
        .font-bold {{
            font-weight: 600;
        }}
        .actions {{
            margin-top: 25px;
            display: flex;
            justify-content: flex-end;
            gap: 12px;
        }}
        .btn {{
            padding: 10px 20px;
            border-radius: 6px;
            font-size: 14px;
            cursor: pointer;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
            border: none;
        }}
        .btn-print {{
            background-color: {BRAND_NAVY};
            color: {BRAND_GOLD};
        }}
        @media print {{
            body {{
                background-color: #ffffff;
                padding: 0;
            }}
            .report-card {{
                box-shadow: none;
                border: none;
                padding: 0;
            }}
            .actions {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="report-card">
        <div class="header">
            <h1>The Josephite Choir</h1>
            <h3>Event Attendance Roster: {event['event_name']}</h3>
        </div>

        <div class="meta-grid">
            <div class="meta-item"><span class="meta-label">Date:</span> <span>{event['event_date']}</span></div>
            <div class="meta-item"><span class="meta-label">Duration:</span> <span>{event['duration_hours']} Hours</span></div>
            <div class="meta-item"><span class="meta-label">Present:</span> <span class="present">{present_count}</span></div>
            <div class="meta-item"><span class="meta-label">Absent:</span> <span class="absent">{absent_count}</span></div>
            <div class="meta-item"><span class="meta-label">Total Roster:</span> <span>{len(roster)}</span></div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Student Name</th>
                    <th>Registration ID</th>
                    <th>Section</th>
                    <th>Attendance Status</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>

        <div class="actions">
            <button class="btn btn-print" onclick="window.print()">Print / Save as PDF</button>
        </div>
    </div>
</body>
</html>
"""
    return HTMLResponse(content=html)

@router.get("/csv/{event_id}")
def get_csv_report(event_id: int):
    """Exports event attendance roster as a downloadable CSV."""
    with get_db_cursor(dict_cursor=True) as cur:
        cur.execute("SELECT event_name, event_date, duration_hours FROM events WHERE event_id = %s", (event_id,))
        event = cur.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found.")

        cur.execute(
            """
            SELECT s.student_name, s.reg_no, s.part, a.is_present
            FROM students s
            JOIN attendance_logs a ON s.reg_no = a.reg_no
            WHERE a.event_id = %s
            ORDER BY s.part, s.student_name ASC
            """,
            (event_id,)
        )
        roster = cur.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Event", event["event_name"]])
    writer.writerow(["Date", str(event["event_date"])])
    writer.writerow(["Duration (Hours)", str(event["duration_hours"])])
    writer.writerow([])
    writer.writerow(["Name", "Registration ID", "Section", "Status"])

    for r in roster:
        status_text = "Present" if r["is_present"] else "Absent"
        writer.writerow([r["student_name"], r["reg_no"], r["part"], status_text])

    csv_data = output.getvalue()
    filename = f"Attendance_{event['event_date']}_{event_id}.csv"
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.get("/credits/csv")
def get_credits_csv(part: str = Query(None)):
    """Exports student credits ledger as a CSV."""
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

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["TJC Credits Ledger"])
    writer.writerow(["Filter", selected_filter])
    writer.writerow([])
    writer.writerow(["Name", "Registration ID", "Section", "Total Hours", "Credits Earned"])

    for r in rows:
        hours = float(r["total_hours"])
        credits_earned = math.floor(abs(hours / 30))
        writer.writerow([r["student_name"], r["reg_no"], r["part"], round(hours, 2), credits_earned])

    csv_data = output.getvalue()
    filename = f"TJC_Credits_{selected_filter.replace(' ', '_')}.csv"
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

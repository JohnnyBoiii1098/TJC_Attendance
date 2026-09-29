from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
import psycopg2
from app.database import get_db_cursor
from app.schemas import StudentCreate, StudentResponse
from app.routers.auth import require_admin_pin
from app.config import CATEGORIES

router = APIRouter(prefix="/api/students", tags=["Students"])

@router.get("/categories", response_model=List[str])
def get_categories():
    """Returns list of valid choir voice parts / sections."""
    return CATEGORIES

@router.get("", response_model=List[StudentResponse])
def list_students(
    part: Optional[str] = Query(None, description="Filter by section/part"),
    search: Optional[str] = Query(None, description="Search by name or reg_no")
):
    """Retrieves all students, with optional filtering by part and search query."""
    query = "SELECT reg_no, student_name, part FROM students WHERE 1=1"
    params = []

    if part and part != "All Parts":
        query += " AND part = %s"
        params.append(part)

    if search:
        query += " AND (LOWER(student_name) LIKE %s OR LOWER(reg_no) LIKE %s)"
        search_pattern = f"%{search.strip().lower()}%"
        params.extend([search_pattern, search_pattern])

    query += " ORDER BY part, student_name ASC"

    with get_db_cursor(dict_cursor=True) as cur:
        cur.execute(query, tuple(params))
        rows = cur.fetchall()

    return rows

@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    student: StudentCreate,
    _auth: bool = Depends(require_admin_pin)
):
    """Registers a new student member (Admin PIN protected)."""
    clean_reg_no = student.reg_no.strip()
    clean_name = student.student_name.strip()
    clean_part = student.part.strip()

    if not clean_reg_no or not clean_name or not clean_part:
        raise HTTPException(status_code=400, detail="All fields (Name, Registration ID, Section) are required.")

    query = """
    INSERT INTO students (reg_no, student_name, part)
    VALUES (%s, %s, %s)
    RETURNING reg_no, student_name, part;
    """
    try:
        with get_db_cursor(commit=True, dict_cursor=True) as cur:
            cur.execute(query, (clean_reg_no, clean_name, clean_part))
            new_student = cur.fetchone()
            return new_student
    except psycopg2.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A student with Registration ID '{clean_reg_no}' already exists."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.delete("/{reg_no}", status_code=status.HTTP_200_OK)
def delete_student(
    reg_no: str,
    _auth: bool = Depends(require_admin_pin)
):
    """Deletes a student and cascades to their attendance records (Admin PIN protected)."""
    with get_db_cursor(commit=True) as cur:
        cur.execute("DELETE FROM students WHERE reg_no = %s RETURNING reg_no;", (reg_no,))
        deleted = cur.fetchone()
        if not deleted:
            raise HTTPException(status_code=404, detail="Student not found.")
    return {"message": f"Student {reg_no} successfully removed."}

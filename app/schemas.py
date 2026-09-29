from pydantic import BaseModel, Field
from typing import List, Optional
import datetime

# --- Student Schemas ---
class StudentBase(BaseModel):
    reg_no: str = Field(..., description="Student registration ID (e.g. 21BCE1001)")
    student_name: str = Field(..., description="Full student name")
    part: str = Field(..., description="Section/category (Alto, Bass, Soprano, Tenor, Band, Conductors)")

class StudentCreate(StudentBase):
    pass

class StudentResponse(StudentBase):
    pass

# --- Event Schemas ---
class EventBase(BaseModel):
    event_name: str = Field(..., description="Name/title of the rehearsal or service")
    event_date: datetime.date = Field(..., description="Date of the event")
    duration_hours: float = Field(2.0, ge=0.1, le=24.0, description="Duration in hours")
    start_time: Optional[str] = Field("", description="Start time (e.g. 16:30 or 4:30 PM)")

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    event_id: int

# --- Attendance Schemas ---
class AttendanceRecord(BaseModel):
    reg_no: str
    is_present: bool = False

class SaveAttendanceRequest(BaseModel):
    event_name: str
    event_date: datetime.date
    duration_hours: float = 2.0
    start_time: Optional[str] = ""
    records: List[AttendanceRecord]

class AttendanceRosterItem(BaseModel):
    reg_no: str
    student_name: str
    part: str
    is_present: bool

class AttendanceRosterResponse(BaseModel):
    event: EventResponse
    roster: List[AttendanceRosterItem]
    total_present: int
    total_absent: int
    total_students: int

# --- Credits Schemas ---
class StudentCreditsItem(BaseModel):
    reg_no: str
    student_name: str
    part: str
    total_hours: float
    credits: int

class CreditsSummaryResponse(BaseModel):
    filter_part: str
    total_records: int
    students: List[StudentCreditsItem]

# --- Auth / PIN Schemas ---
class VerifyPinRequest(BaseModel):
    pin: str

class VerifyPinResponse(BaseModel):
    valid: bool
    message: str

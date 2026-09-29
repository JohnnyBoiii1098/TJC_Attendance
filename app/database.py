import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from app.config import DATABASE_URL
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    """Returns a raw psycopg2 connection to the database."""
    return psycopg2.connect(DATABASE_URL)

@contextmanager
def get_db_cursor(commit: bool = False, dict_cursor: bool = False):
    """
    Context manager providing a database cursor.
    Auto-commits if commit=True, auto-rollbacks on exception, and ensures connection is closed.
    """
    conn = psycopg2.connect(DATABASE_URL)
    cursor_factory = RealDictCursor if dict_cursor else None
    cur = conn.cursor(cursor_factory=cursor_factory)
    try:
        yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def init_db():
    """
    Ensures required tables and indexes exist.
    This guarantees that when connecting to a fresh cloud Supabase database,
    all tables are automatically created.
    """
    create_tables_sql = """
    CREATE TABLE IF NOT EXISTS students (
        reg_no VARCHAR(100) PRIMARY KEY,
        student_name VARCHAR(255) NOT NULL,
        part VARCHAR(50) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS events (
        event_id SERIAL PRIMARY KEY,
        event_name VARCHAR(255) NOT NULL,
        event_date DATE NOT NULL,
        duration_hours NUMERIC(4, 2) NOT NULL DEFAULT 2.0,
        start_time VARCHAR(50) DEFAULT '',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS attendance_logs (
        log_id SERIAL PRIMARY KEY,
        event_id INTEGER NOT NULL REFERENCES events(event_id) ON DELETE CASCADE,
        reg_no VARCHAR(100) NOT NULL REFERENCES students(reg_no) ON DELETE CASCADE,
        is_present BOOLEAN NOT NULL DEFAULT FALSE,
        CONSTRAINT unique_event_student UNIQUE (event_id, reg_no)
    );

    CREATE INDEX IF NOT EXISTS idx_events_date ON events(event_date);
    CREATE INDEX IF NOT EXISTS idx_attendance_event ON attendance_logs(event_id);
    CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance_logs(reg_no);
    CREATE INDEX IF NOT EXISTS idx_students_part ON students(part);

    DO $$ 
    BEGIN 
        IF NOT EXISTS (
            SELECT 1 FROM pg_constraint WHERE conname = 'unique_event_student'
        ) THEN 
            ALTER TABLE attendance_logs ADD CONSTRAINT unique_event_student UNIQUE (event_id, reg_no);
        END IF; 
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_name = 'events' AND column_name = 'start_time'
        ) THEN 
            ALTER TABLE events ADD COLUMN start_time VARCHAR(50) DEFAULT '';
        END IF;
    END $$;
    """
    try:
        with get_db_cursor(commit=True) as cur:
            cur.execute(create_tables_sql)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        # Re-raise so the developer/user is immediately aware of connection/permission issues
        raise

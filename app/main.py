import os
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db
from app.routers import auth, students, events, attendance, credits, reports

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    try:
        init_db()
    except Exception as e:
        print(f"Warning: Database initialization encountered an error: {e}")
    yield

app = FastAPI(
    title="TJC Attendance API",
    description="Backend API and Attendance Management Portal for The Josephite Choir",
    version="2.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(events.router)
app.include_router(attendance.router)
app.include_router(credits.router)
app.include_router(reports.router)

# Health check
@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "TJC Attendance Portal",
        "version": "2.0.0"
    }

# Static Files & Frontend Routing
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", include_in_schema=False)
async def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"message": "TJC Attendance API is running. Static frontend not found."})

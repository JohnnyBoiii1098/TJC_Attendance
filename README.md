# The Josephite Choir (TJC) Attendance Portal 🎵

> *"For The Greater Glory Of God"*

A modern, responsive, modular full-stack web application designed for **The Josephite Choir (TJC)** to manage choir rehearsals, track student attendance, calculate academic credits, and generate printable reports and CSV exports.

---

## 🌟 Key Features

- **✍️ Live Attendance Marking**:
  - Filter by voice section (*Alto, Bass, Soprano, Tenor, Band, Conductors*).
  - Live search by student name or registration ID.
  - Quick toggle switches for Present / Absent with instant live counters.
  - Batch action shortcuts (*Mark Filtered Present / Absent*).
- **📅 Day Viewer & Official Reports**:
  - Filter past sessions by date and select any event.
  - Instant **Printable Slip / Webpage View** formatted with choir header and print styling.
  - One-click **Download CSV** export.
- **📊 Credits Ledger**:
  - Strict vocal section isolation.
  - Automatic hour accumulation and credit computation (`Credits = floor(total_hours / 30)`).
  - Export entire credit sheets to CSV.
- **👥 Members Directory**:
  - Register new choir members with section assignment.
  - Manage and search active members.
- **🔒 Admin Passcode Protection**:
  - Lightweight PIN protection (`ADMIN_PASSCODE` in `.env`) for write operations (*marking attendance, adding/deleting members*).
  - Remembers login state in the browser session with an instant unlock modal.
- **☁️ Cloud & Free-Tier Ready**:
  - Runs locally on your machine or deploys to **Vercel** serverless free tier.
  - Supports both **Local PostgreSQL** and **Supabase Free Cloud Database** with auto table initialization.

---

## 🏗️ Architecture & Project Structure

```text
TJC_Attendance/
├── app/
│   ├── config.py           # Environment variables, database URL, and admin PIN
│   ├── database.py         # Connection pooling & auto-table migrations
│   ├── schemas.py          # Pydantic data models & request/response validation
│   ├── routers/
│   │   ├── auth.py         # Admin PIN verification dependency
│   │   ├── students.py     # Student member endpoints
│   │   ├── events.py       # Event session queries
│   │   ├── attendance.py   # Attendance recording & roster retrieval
│   │   ├── credits.py      # Attendance hours & credits ledger logic
│   │   └── reports.py      # Printable HTML reports and CSV downloads
│   └── main.py             # FastAPI instance, CORS, static mounts, and lifespan
├── static/
│   ├── css/
│   │   └── custom.css      # Custom brand styling (Navy #001f3f, Gold #D4AF37)
│   ├── js/
│   │   └── app.js          # Reactive frontend application logic
│   └── index.html          # Modern Tailwind CSS single-page dashboard
├── api/
│   └── index.py            # Vercel Serverless Function entrypoint
├── run.py                  # 1-Click local launch script
├── vercel.json             # Vercel deployment configuration
├── requirements.txt        # Python package dependencies
├── .env.example            # Environment variables template
└── README.md
```

---

## 🚀 Local Quickstart

### 1. Prerequisites
- Python 3.10+
- PostgreSQL (Local or Supabase)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Ensure your `.env` contains your database connection string and desired Admin PIN:
```ini
DATABASE_URL=postgresql://postgres:Nevve80085@127.0.0.1:5432/TJC
ADMIN_PASSCODE=1234
PORT=8000
HOST=0.0.0.0
```

### 4. Run the Application
```bash
python run.py
```
Or directly with Uvicorn:
```bash
uvicorn app.main:app --reload --port 8000
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

---

## ☁️ Deploying to Vercel + Supabase (Free Tier)

### Step 1: Set Up Free PostgreSQL on Supabase
1. Create a free account at [supabase.com](https://supabase.com).
2. Create a new project (e.g., `TJC-Attendance`).
3. In project settings under **Database**, copy your **Connection String** (URI / Connection Pooling mode).
4. *(Optional)* If migrating existing local students to Supabase, export your local students table:
   ```bash
   pg_dump -U postgres -d TJC -t students --data-only > students_backup.sql
   ```
   and run it in the Supabase SQL editor. The application automatically creates all necessary tables on startup!

### Step 2: Deploy to Vercel
1. Push your repository to GitHub.
2. Go to [vercel.com](https://vercel.com) and import the repository.
3. In **Project Settings** &rarr; **Environment Variables**, add:
   - `DATABASE_URL`: `postgresql://postgres.[REF]:[PASSWORD]@...pooler.supabase.com:6543/postgres?sslmode=require`
   - `ADMIN_PASSCODE`: `YourSecretPin1234`
4. Click **Deploy**. Vercel will detect `vercel.json` and build the serverless application automatically.

---

## 🔒 Security Note
- Never commit your `.env` file to Git. `.gitignore` is pre-configured to ignore `.env` and `.env.local`.
- Use a strong `ADMIN_PASSCODE` in production to prevent unauthorized modifications to attendance logs.

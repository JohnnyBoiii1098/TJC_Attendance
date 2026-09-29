import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Nevve80085@127.0.0.1:5432/TJC"
)

# Convert postgres:// to postgresql:// if needed for standard driver compatibility
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Security - Admin PIN for write operations (marking attendance, adding/deleting members)
ADMIN_PASSCODE = os.getenv("ADMIN_PASSCODE", "1234")

# Server configuration
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Organization / Choir Categories
CATEGORIES = ["Alto", "Bass", "Soprano", "Tenor", "Band", "Conductors"]

# Branding Constants
BRAND_NAVY = "#001f3f"
BRAND_GOLD = "#D4AF37"

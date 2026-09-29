import sys
import os

# Add repository root to system path for clean imports in Vercel Serverless environment
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.main import app

# Handler for Vercel Serverless Functions
# Vercel's @vercel/python automatically uses ASGI `app`

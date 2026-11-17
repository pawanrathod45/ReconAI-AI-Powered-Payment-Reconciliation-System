import sys
import os

# Add backend directory to sys.path so both backend.app.main and app.main work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.main import app

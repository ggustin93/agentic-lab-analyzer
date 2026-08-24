"""
Test bootstrap: provide dummy configuration before any service import.

The whole suite runs against mocks — no real API key or Supabase project is
ever needed — but config.settings validates required variables at import
time, so harmless placeholders are injected here for local runs and CI alike.
"""

import os
import sys
from pathlib import Path

# Make the backend package importable when pytest runs from the repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("MISTRAL_API_KEY", "test-key")
os.environ.setdefault("CHUTES_AI_API_KEY", "test-key")
os.environ.setdefault("SUPABASE_URL", "http://localhost:54321")
os.environ.setdefault("SUPABASE_KEY", "test-key")

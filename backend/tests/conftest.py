"""
Test bootstrap: provide dummy configuration before any service import.

The whole suite runs against mocks or a throwaway local SQLite database — no
real API key or cloud project is ever needed — but config.settings validates
required variables at import time, so harmless placeholders are injected here
for local runs and CI alike. Local-mode paths point at a temp directory so
importing main.py never writes into the working tree.
"""

import os
import sys
import tempfile
from pathlib import Path

# Make the backend package importable when pytest runs from the repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("MISTRAL_API_KEY", "test-key")
os.environ.setdefault("CHUTES_AI_API_KEY", "test-key")

_tmp = tempfile.mkdtemp(prefix="lab-analyzer-tests-")
os.environ.setdefault("STORAGE_MODE", "local")
os.environ.setdefault("DB_PATH", str(Path(_tmp) / "app.db"))
os.environ.setdefault("UPLOAD_DIR", str(Path(_tmp) / "uploads"))

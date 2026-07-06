from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SEEDS_DIR = BASE_DIR / "seeds"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/shiks_db")
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "college_scraper")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "college_payloads")

SETTINGS = {
    "BASE_DIR": BASE_DIR,
    "DATA_DIR": DATA_DIR,
    "SEEDS_DIR": SEEDS_DIR,
    "DATABASE_URL": DATABASE_URL,
    "MONGODB_URI": MONGODB_URI,
    "MONGODB_DB": MONGODB_DB,
    "MONGODB_COLLECTION": MONGODB_COLLECTION,
}

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "health.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS body_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_date TEXT NOT NULL,
    weight_kg REAL,
    bmi REAL,
    body_fat_percent REAL,
    muscle_mass_kg REAL,
    basal_metabolic_rate REAL,
    source TEXT,
    confidence TEXT DEFAULT 'B'
);
CREATE TABLE IF NOT EXISTS activity_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_date TEXT NOT NULL,
    steps INTEGER,
    active_calories REAL,
    exercise_minutes INTEGER,
    distance_km REAL,
    vo2max REAL,
    resting_heart_rate REAL,
    hrv_ms REAL,
    source TEXT
);
CREATE TABLE IF NOT EXISTS sleep_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_date TEXT NOT NULL,
    total_sleep_hours REAL,
    deep_sleep_hours REAL,
    rem_sleep_hours REAL,
    awake_times INTEGER,
    source TEXT
);
CREATE TABLE IF NOT EXISTS nutrition_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_date TEXT NOT NULL,
    calories REAL,
    protein_g REAL,
    carbs_g REAL,
    fat_g REAL,
    fiber_g REAL,
    source TEXT
);
CREATE TABLE IF NOT EXISTS health_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_date TEXT NOT NULL,
    body_score REAL,
    fitness_score REAL,
    recovery_score REAL,
    nutrition_score REAL,
    total_score REAL
);
CREATE TABLE IF NOT EXISTS daily_snapshots (
    record_date TEXT PRIMARY KEY,
    payload_json TEXT NOT NULL,
    quality_json TEXT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS ingestion_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    record_count INTEGER DEFAULT 0,
    day_count INTEGER DEFAULT 0,
    status TEXT NOT NULL,
    detail TEXT
);
"""


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA)

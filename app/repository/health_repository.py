from datetime import date
from typing import Any, Dict, List, Optional

from app.database.db import get_connection, init_db


class HealthRepository:
    def __init__(self) -> None:
        init_db()

    def latest_body(self) -> Optional[Dict[str, Any]]:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM body_metrics ORDER BY record_date DESC, id DESC LIMIT 1"
            ).fetchone()
        return dict(row) if row else None

    def latest_activity(self) -> Optional[Dict[str, Any]]:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM activity_metrics ORDER BY record_date DESC, id DESC LIMIT 1"
            ).fetchone()
        return dict(row) if row else None

    def latest_sleep(self) -> Optional[Dict[str, Any]]:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM sleep_metrics ORDER BY record_date DESC, id DESC LIMIT 1"
            ).fetchone()
        return dict(row) if row else None

    def latest_nutrition(self) -> Optional[Dict[str, Any]]:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM nutrition_records ORDER BY record_date DESC, id DESC LIMIT 1"
            ).fetchone()
        return dict(row) if row else None

    def body_history(self, limit: int = 30) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM body_metrics ORDER BY record_date DESC, id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in reversed(rows)]

    def upsert_demo_snapshot(self) -> None:
        """Seed a small demo dataset only when the database is empty."""
        today = date.today().isoformat()
        with get_connection() as conn:
            exists = conn.execute("SELECT COUNT(*) AS c FROM body_metrics").fetchone()["c"]
            if exists:
                return
            conn.execute(
                "INSERT INTO body_metrics (record_date, weight_kg, bmi, body_fat_percent, muscle_mass_kg, source, confidence) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (today, 70.5, 23.0, 31.7, 48.2, "demo", "D"),
            )
            conn.execute(
                "INSERT INTO activity_metrics (record_date, steps, active_calories, exercise_minutes, distance_km, vo2max, resting_heart_rate, hrv_ms, source) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (today, 5000, 250, 30, 3.5, 31.2, 63, 28.1, "demo"),
            )
            conn.execute(
                "INSERT INTO sleep_metrics (record_date, total_sleep_hours, deep_sleep_hours, rem_sleep_hours, awake_times, source) VALUES (?, ?, ?, ?, ?, ?)",
                (today, 5.5, 0.8, 1.1, 2, "demo"),
            )
            conn.execute(
                "INSERT INTO nutrition_records (record_date, calories, protein_g, carbs_g, fat_g, fiber_g, source) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (today, 1700, 85, 180, 60, 25, "demo"),
            )

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any, Iterable

from app.analytics.data_quality import assess_completeness, detect_conflicts
from app.connectors.apple_health import normalize_records
from app.database.db import get_connection, init_db


def _latest_by_metric(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for r in records:
        key = r['metric']
        if key not in latest or str(r['timestamp']) > str(latest[key]['timestamp']):
            latest[key] = r
    return latest


def ingest_apple_health(raw_records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Normalize Apple Health records, persist daily aggregates, and build snapshots.

    Accepts the neutral record contract used by app.connectors.apple_health.normalize_records.
    This deliberately does not pretend to have direct iOS HealthKit access: an iOS Shortcut,
    HealthKit client, or exported payload must send records into this function.
    """
    init_db()
    normalized = normalize_records(raw_records)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in normalized:
        grouped[str(r['record_date'])].append(r)

    written = 0
    snapshots = []
    with get_connection() as conn:
        for day, records in sorted(grouped.items()):
            latest = _latest_by_metric(records)
            conflicts = detect_conflicts(records)

            body = {k: latest[k]['value'] for k in ('weight_kg','bmi','body_fat_percent','muscle_mass_kg') if k in latest}
            activity = {k: latest[k]['value'] for k in ('steps','active_calories','exercise_minutes','distance_km','vo2max','resting_heart_rate','hrv_ms') if k in latest}
            sleep = {k: latest[k]['value'] for k in ('total_sleep_hours',) if k in latest}

            if body:
                conn.execute('DELETE FROM body_metrics WHERE record_date=? AND source=?', (day, 'Apple Health'))
                conn.execute('''INSERT INTO body_metrics(record_date,weight_kg,bmi,body_fat_percent,muscle_mass_kg,source,confidence)
                                VALUES(?,?,?,?,?,?,?)''', (day, body.get('weight_kg'), body.get('bmi'), body.get('body_fat_percent'), body.get('muscle_mass_kg'), 'Apple Health', 'E' if conflicts else 'B'))
            if activity:
                conn.execute('DELETE FROM activity_metrics WHERE record_date=? AND source=?', (day, 'Apple Health'))
                conn.execute('''INSERT INTO activity_metrics(record_date,steps,active_calories,exercise_minutes,distance_km,vo2max,resting_heart_rate,hrv_ms,source)
                                VALUES(?,?,?,?,?,?,?,?,?)''', (day, activity.get('steps'), activity.get('active_calories'), activity.get('exercise_minutes'), activity.get('distance_km'), activity.get('vo2max'), activity.get('resting_heart_rate'), activity.get('hrv_ms'), 'Apple Health'))
            if sleep:
                conn.execute('DELETE FROM sleep_metrics WHERE record_date=? AND source=?', (day, 'Apple Health'))
                conn.execute('''INSERT INTO sleep_metrics(record_date,total_sleep_hours,source) VALUES(?,?,?)''', (day, sleep.get('total_sleep_hours'), 'Apple Health'))

            present = set(latest)
            expected = {'steps','active_calories','exercise_minutes','resting_heart_rate','hrv_ms','total_sleep_hours'}
            quality = assess_completeness(present, expected)
            snapshot = build_daily_snapshot(day, conn=conn, quality=quality, conflicts=conflicts)
            snapshots.append(snapshot)
            written += len(records)
        conn.commit()
    return {'normalized_records': len(normalized), 'written_records': written, 'days': len(grouped), 'snapshots': snapshots}


def build_daily_snapshot(record_date: str | date, conn=None, quality: dict[str, Any] | None = None, conflicts: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    day = str(record_date)
    owns_conn = conn is None
    conn = conn or get_connection()
    try:
        def one(table: str):
            row = conn.execute(f'SELECT * FROM {table} WHERE record_date=? ORDER BY id DESC LIMIT 1', (day,)).fetchone()
            return dict(row) if row else {}
        body, activity, sleep, nutrition = one('body_metrics'), one('activity_metrics'), one('sleep_metrics'), one('nutrition_records')
        snapshot = {
            'record_date': day,
            'body': body,
            'activity': activity,
            'sleep': sleep,
            'nutrition': nutrition,
            'quality': quality or {},
            'conflicts': conflicts or [],
        }
        conn.execute('''INSERT INTO daily_snapshots(record_date,payload_json,quality_json,updated_at)
                        VALUES(?,?,?,CURRENT_TIMESTAMP)
                        ON CONFLICT(record_date) DO UPDATE SET payload_json=excluded.payload_json, quality_json=excluded.quality_json, updated_at=CURRENT_TIMESTAMP''',
                     (day, __import__('json').dumps(snapshot, ensure_ascii=False), __import__('json').dumps(snapshot['quality'], ensure_ascii=False)))
        if owns_conn:
            conn.commit()
        return snapshot
    finally:
        if owns_conn:
            conn.close()

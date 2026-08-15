from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from datetime import date
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

from app.database.db import get_connection, init_db
from app.reports.daily_report import generate_daily_report
from app.services.health_pipeline import build_daily_snapshot, ingest_apple_health

app = FastAPI(title="Personal Health Digital Twin API", version="1.4.0")


class SyncPayload(BaseModel):
    records: list[dict[str, Any]]


class AppEnrollPayload(BaseModel):
    enrollment_code: str


def require_token(authorization: str | None = Header(default=None)) -> None:
    expected = os.getenv("HEALTH_SYNC_TOKEN")
    if not expected:
        raise HTTPException(status_code=503, detail="HEALTH_SYNC_TOKEN is not configured")
    if authorization != f"Bearer {expected}":
        raise HTTPException(status_code=401, detail="invalid token")


def _session_secret() -> bytes:
    secret = os.getenv("APP_SESSION_SECRET")
    if not secret:
        raise HTTPException(status_code=503, detail="APP_SESSION_SECRET is not configured")
    return secret.encode("utf-8")


def _b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _unb64url(raw: str) -> bytes:
    padding = "=" * ((4 - len(raw) % 4) % 4)
    return base64.urlsafe_b64decode(raw + padding)


def _issue_app_session() -> str:
    payload = {
        "sub": "owner",
        "exp": int(time.time()) + 30 * 24 * 60 * 60,
        "jti": secrets.token_hex(12),
    }
    encoded = _b64url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = _b64url(hmac.new(_session_secret(), encoded.encode("ascii"), hashlib.sha256).digest())
    return f"{encoded}.{signature}"


def _verify_app_session(token: str) -> dict[str, Any]:
    try:
        encoded, signature = token.split(".", 1)
        expected = _b64url(hmac.new(_session_secret(), encoded.encode("ascii"), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            raise ValueError("bad signature")
        payload = json.loads(_unb64url(encoded))
        if payload.get("sub") != "owner" or int(payload.get("exp", 0)) < int(time.time()):
            raise ValueError("expired")
        return payload
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail="invalid or expired app session") from exc


def require_app_session(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing app session")
    return _verify_app_session(authorization.removeprefix("Bearer ").strip())


def _allow_reenroll() -> bool:
    return os.getenv("APP_ALLOW_REENROLL", "false").strip().lower() in {"1", "true", "yes"}


def _latest_body_on_or_before(target_date: date) -> dict[str, Any]:
    with get_connection() as conn:
        row = conn.execute(
            """SELECT * FROM body_metrics
            WHERE record_date <= ?
            ORDER BY record_date DESC, id DESC
            LIMIT 1""",
            (target_date.isoformat(),),
        ).fetchone()
    return dict(row) if row else {}


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/app/enroll")
def app_enroll(payload: AppEnrollPayload) -> dict[str, Any]:
    expected = os.getenv("APP_ENROLLMENT_CODE")
    if not expected:
        raise HTTPException(status_code=503, detail="APP_ENROLLMENT_CODE is not configured")
    if not hmac.compare_digest(payload.enrollment_code.strip(), expected):
        raise HTTPException(status_code=401, detail="invalid enrollment code")

    # Validate session signing before consuming the one-time enrollment state.
    session_token = _issue_app_session()

    with get_connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT value FROM app_state WHERE key='owner_enrolled'").fetchone()
        already_enrolled = bool(row and row["value"] == "1")
        if already_enrolled and not _allow_reenroll():
            raise HTTPException(status_code=409, detail="owner device is already enrolled")
        conn.execute(
            """INSERT INTO app_state(key,value,updated_at) VALUES('owner_enrolled','1',CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET value='1', updated_at=CURRENT_TIMESTAMP"""
        )
        conn.commit()

    return {
        "session_token": session_token,
        "expires_in_seconds": 30 * 24 * 60 * 60,
        "enrollment_consumed": True,
    }


@app.post("/v1/app/sync/apple-health")
def app_sync_apple_health(
    payload: SyncPayload,
    _: dict[str, Any] = Depends(require_app_session),
) -> dict[str, Any]:
    if len(payload.records) > 10000:
        raise HTTPException(status_code=413, detail="too many health records in one sync")
    return ingest_apple_health(payload.records)


@app.get("/v1/app/summary")
def app_summary(
    record_date: date | None = None,
    _: dict[str, Any] = Depends(require_app_session),
) -> dict[str, Any]:
    target_date = record_date or date.today()
    snapshot = build_daily_snapshot(target_date)
    report = generate_daily_report(snapshot)
    used = report.get("used_data") or {}
    priorities = report.get("priorities") or []
    core = report.get("core_conclusion") or []

    today_body = snapshot.get("body") or {}
    body_view = today_body or _latest_body_on_or_before(target_date)

    return {
        "record_date": snapshot.get("record_date"),
        "body_measurement_date": body_view.get("record_date"),
        "readiness": {
            "level": report.get("mode"),
            "score": None,
            "summary": core[0] if core else (priorities[0] if priorities else "今日数据已同步"),
            "reasons": priorities[:3],
        },
        "metrics": {
            "sleep_hours": used.get("sleep_hours"),
            "hrv_ms": used.get("hrv_ms"),
            "resting_heart_rate": used.get("resting_heart_rate"),
            "steps": used.get("steps"),
            "weight_kg": used.get("weight_kg") if used.get("weight_kg") is not None else body_view.get("weight_kg"),
            "body_fat_percent": used.get("body_fat_percent") if used.get("body_fat_percent") is not None else body_view.get("body_fat_percent"),
            "lean_mass_kg": body_view.get("lean_body_mass_kg"),
        },
        "actions": report.get("today_actions") or [],
        "data_quality": report.get("data_quality") or {},
        "safety": report.get("safety"),
    }


@app.post("/v1/sync/apple-health", dependencies=[Depends(require_token)])
def sync_apple_health(payload: SyncPayload) -> dict[str, Any]:
    return ingest_apple_health(payload.records)


@app.get("/v1/snapshot/{record_date}", dependencies=[Depends(require_token)])
def daily_snapshot(record_date: date) -> dict[str, Any]:
    return build_daily_snapshot(record_date)


@app.get("/v1/report/{record_date}", dependencies=[Depends(require_token)])
def daily_report(record_date: date) -> dict[str, Any]:
    return generate_daily_report(build_daily_snapshot(record_date))


@app.get("/v1/snapshots", dependencies=[Depends(require_token)])
def snapshots(limit: int = 30) -> list[dict[str, Any]]:
    limit = max(1, min(limit, 365))
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT payload_json FROM daily_snapshots ORDER BY record_date DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [json.loads(row["payload_json"]) for row in rows]

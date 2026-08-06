from __future__ import annotations

import os
from datetime import date
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

from app.database.db import get_connection, init_db
from app.services.health_pipeline import build_daily_snapshot, ingest_apple_health

app = FastAPI(title="Personal Health Digital Twin API", version="1.0.0")


class SyncPayload(BaseModel):
    records: list[dict[str, Any]]


def require_token(authorization: str | None = Header(default=None)) -> None:
    expected = os.getenv("HEALTH_SYNC_TOKEN")
    if not expected:
        raise HTTPException(status_code=503, detail="HEALTH_SYNC_TOKEN is not configured")
    if authorization != f"Bearer {expected}":
        raise HTTPException(status_code=401, detail="invalid token")


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/sync/apple-health", dependencies=[Depends(require_token)])
def sync_apple_health(payload: SyncPayload) -> dict[str, Any]:
    return ingest_apple_health(payload.records)


@app.get("/v1/snapshot/{record_date}", dependencies=[Depends(require_token)])
def daily_snapshot(record_date: date) -> dict[str, Any]:
    return build_daily_snapshot(record_date)


@app.get("/v1/snapshots", dependencies=[Depends(require_token)])
def snapshots(limit: int = 30) -> list[dict[str, Any]]:
    import json
    limit = max(1, min(limit, 365))
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT payload_json FROM daily_snapshots ORDER BY record_date DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [json.loads(row["payload_json"]) for row in rows]

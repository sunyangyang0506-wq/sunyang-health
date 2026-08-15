from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import date
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

from app.database.db import get_connection, init_db
from app.reports.daily_report import generate_daily_report
from app.services.health_pipeline import build_daily_snapshot, ingest_apple_health

app = FastAPI(title="Personal Health Digital Twin API", version="1.1.0")


class SyncPayload(BaseModel):
    records: list[dict[str, Any]]


class WeChatLoginPayload(BaseModel):
    code: str


def require_token(authorization: str | None = Header(default=None)) -> None:
    expected = os.getenv("HEALTH_SYNC_TOKEN")
    if not expected:
        raise HTTPException(status_code=503, detail="HEALTH_SYNC_TOKEN is not configured")
    if authorization != f"Bearer {expected}":
        raise HTTPException(status_code=401, detail="invalid token")


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def _session_secret() -> bytes:
    secret = os.getenv("HEALTH_SESSION_SECRET")
    if not secret:
        raise HTTPException(status_code=503, detail="HEALTH_SESSION_SECRET is not configured")
    return secret.encode("utf-8")


def _issue_session(openid: str) -> str:
    ttl = int(os.getenv("HEALTH_SESSION_TTL_SECONDS", "604800"))
    payload = {
        "sub": openid,
        "exp": int(time.time()) + ttl,
        "iss": "sunyang-health",
    }
    encoded = _b64url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = _b64url(hmac.new(_session_secret(), encoded.encode("ascii"), hashlib.sha256).digest())
    return f"{encoded}.{signature}"


def _verify_session(token: str) -> dict[str, Any]:
    try:
        encoded, signature = token.split(".", 1)
        expected = _b64url(hmac.new(_session_secret(), encoded.encode("ascii"), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            raise ValueError("bad signature")
        payload = json.loads(_b64url_decode(encoded))
        if int(payload.get("exp", 0)) <= int(time.time()):
            raise ValueError("expired")
        if payload.get("iss") != "sunyang-health" or not payload.get("sub"):
            raise ValueError("invalid payload")
        return payload
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail="invalid or expired session") from exc


def require_wechat_session(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing session")
    payload = _verify_session(authorization[7:])
    openid = str(payload["sub"])
    allowed = {item.strip() for item in os.getenv("WECHAT_ALLOWED_OPENIDS", "").split(",") if item.strip()}
    allow_any = os.getenv("WECHAT_ALLOW_ANY_USER", "false").lower() == "true"
    if not allowed and not allow_any:
        raise HTTPException(status_code=503, detail="WECHAT_ALLOWED_OPENIDS is not configured")
    if allowed and openid not in allowed:
        raise HTTPException(status_code=403, detail="user is not authorized for this health profile")
    return openid


def _wechat_code2session(code: str) -> dict[str, Any]:
    appid = os.getenv("WECHAT_APP_ID")
    secret = os.getenv("WECHAT_APP_SECRET")
    if not appid or not secret:
        raise HTTPException(status_code=503, detail="WeChat credentials are not configured")

    query = urllib.parse.urlencode(
        {
            "appid": appid,
            "secret": secret,
            "js_code": code,
            "grant_type": "authorization_code",
        }
    )
    url = f"https://api.weixin.qq.com/sns/jscode2session?{query}"
    try:
        with urllib.request.urlopen(url, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=502, detail="WeChat authentication request failed") from exc

    if data.get("errcode"):
        raise HTTPException(
            status_code=401,
            detail={"message": "WeChat code exchange failed", "errcode": data.get("errcode")},
        )
    if not data.get("openid"):
        raise HTTPException(status_code=502, detail="WeChat response did not include openid")
    return data


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/auth/wechat")
def wechat_login(payload: WeChatLoginPayload) -> dict[str, Any]:
    if not payload.code.strip():
        raise HTTPException(status_code=400, detail="code is required")
    wx = _wechat_code2session(payload.code.strip())
    openid = str(wx["openid"])
    response: dict[str, Any] = {
        "access_token": _issue_session(openid),
        "token_type": "bearer",
        "expires_in": int(os.getenv("HEALTH_SESSION_TTL_SECONDS", "604800")),
    }
    if os.getenv("WECHAT_RETURN_OPENID", "false").lower() == "true":
        response["openid"] = openid
    return response


@app.get("/v1/mobile/summary")
def mobile_summary(openid: str = Depends(require_wechat_session)) -> dict[str, Any]:
    snapshot = build_daily_snapshot(date.today())
    report = generate_daily_report(snapshot)
    used = report.get("used_data") or {}
    mode = str(report.get("mode") or "yellow").lower()
    if mode not in {"green", "yellow", "red"}:
        mode = "yellow"
    return {
        "user": {"authenticated": True, "subject": hashlib.sha256(openid.encode("utf-8")).hexdigest()[:12]},
        "record_date": report.get("record_date"),
        "readiness": {
            "level": mode,
            "summary": (report.get("core_conclusion") or ["按已同步数据生成今日建议"])[0],
            "reasons": report.get("priorities") or [],
        },
        "metrics": used,
        "actions": report.get("today_actions") or [],
        "cautions": report.get("cautions") or [],
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

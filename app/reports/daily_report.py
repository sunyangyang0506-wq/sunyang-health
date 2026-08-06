from __future__ import annotations

from dataclasses import asdict
from typing import Any

from app.agent.health_agent import HealthAgent


def generate_daily_report(snapshot: dict[str, Any]) -> dict[str, Any]:
    body = snapshot.get("body") or {}
    activity = snapshot.get("activity") or {}
    sleep = snapshot.get("sleep") or {}
    nutrition = snapshot.get("nutrition") or {}
    quality = snapshot.get("quality") or {}
    conflicts = snapshot.get("conflicts") or []

    agent_input = {
        "body_fat_percent": body.get("body_fat_percent"),
        "steps": activity.get("steps"),
        "hrv_ms": activity.get("hrv_ms"),
        "resting_heart_rate": activity.get("resting_heart_rate"),
        "sleep_hours": sleep.get("total_sleep_hours"),
        "protein_g": nutrition.get("protein_g"),
    }
    decision = HealthAgent().decide(agent_input)

    core = []
    if decision.priorities:
        core.append(decision.priorities[0])
    if conflicts:
        core.append("存在数据冲突，相关指标暂不用于确定性趋势判断。")
    if quality and not quality.get("sufficient", True):
        core.append("今日关键健康数据覆盖不足，结论按已同步数据生成。")

    return {
        "record_date": snapshot.get("record_date"),
        "core_conclusion": core[:3],
        "mode": decision.mode,
        "used_data": {
            "weight_kg": body.get("weight_kg"),
            "body_fat_percent": body.get("body_fat_percent"),
            "steps": activity.get("steps"),
            "hrv_ms": activity.get("hrv_ms"),
            "resting_heart_rate": activity.get("resting_heart_rate"),
            "sleep_hours": sleep.get("total_sleep_hours"),
            "protein_g": nutrition.get("protein_g"),
        },
        "priorities": decision.priorities[:3],
        "today_actions": decision.actions,
        "cautions": decision.cautions,
        "data_quality": quality,
        "conflicts": conflicts,
        "safety": "生活方式管理建议，不替代医疗诊断；药物剂量和治疗目标应由医生决定。",
    }

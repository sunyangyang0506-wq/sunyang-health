from typing import Any

from app.agent.health_agent import HealthAgent


class DailyReportService:
    def __init__(self):
        self.agent = HealthAgent()

    def generate(self, snapshot: dict[str, Any]) -> dict[str, Any]:
        decision = self.agent.decide(snapshot)

        return {
            "core_conclusion": f"今日模式：{decision.mode}",
            "priorities": decision.priorities,
            "actions": decision.actions,
            "cautions": decision.cautions,
            "data_used": {
                "body": snapshot.get("body"),
                "activity": snapshot.get("activity"),
                "sleep": snapshot.get("sleep"),
                "nutrition": snapshot.get("nutrition"),
            },
        }

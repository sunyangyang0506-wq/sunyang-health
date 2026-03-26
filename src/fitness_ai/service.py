from __future__ import annotations

from .decision_engine import DecisionEngine
from .human_engine import HumanEngine
from .models import CommunicationStyle, DailySignals


class CoachingService:
    """组合决策引擎 + 人感引擎，输出首页可用结果。"""

    def __init__(self, decision_engine: DecisionEngine | None = None, human_engine: HumanEngine | None = None) -> None:
        self.decision_engine = decision_engine or DecisionEngine()
        self.human_engine = human_engine or HumanEngine()

    def get_daily_brief(self, signals: DailySignals, style: CommunicationStyle) -> dict[str, str]:
        decision = self.decision_engine.evaluate_daily(signals)
        message = self.human_engine.render_daily_message(decision, style)
        return {
            "recovery_level": decision.recovery_level.value,
            "reason": decision.reason,
            "training_action": decision.training_action,
            "nutrition_action": decision.nutrition_action,
            "message": message,
        }

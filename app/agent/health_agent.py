from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class HealthDecision:
    mode: str
    priorities: List[str]
    actions: List[str]
    cautions: List[str]


class HealthAgent:
    """Rule-first health decision layer.

    This module generates lifestyle guidance only. It does not diagnose disease
    or change medication. Medical flags are intentionally conservative.
    """

    def decide(self, snapshot: Dict[str, Any]) -> HealthDecision:
        sleep = float(snapshot.get("sleep_hours") or 0)
        hrv = snapshot.get("hrv_ms")
        resting_hr = snapshot.get("resting_heart_rate")
        steps = int(snapshot.get("steps") or 0)
        protein = float(snapshot.get("protein_g") or 0)
        body_fat = snapshot.get("body_fat_percent")

        priorities: List[str] = []
        actions: List[str] = []
        cautions: List[str] = []

        recovery_low = sleep and sleep < 6
        if hrv is not None and float(hrv) < 25:
            recovery_low = True
        if resting_hr is not None and float(resting_hr) > 75:
            recovery_low = True

        if recovery_low:
            mode = "恢复优先"
            priorities.append("恢复")
            actions.append("避免高强度训练，优先轻中强度活动")
            actions.append("今晚优先保证充足睡眠")
        else:
            mode = "减脂保肌"
            priorities.append("减脂保肌")

        if steps < 7000:
            priorities.append("提高日常活动")
            actions.append("逐步把全天步数提高到7000-9000步")

        if protein and protein < 100:
            priorities.append("补足蛋白质")
            actions.append("优先在早餐和午餐增加优质蛋白质")

        if body_fat is not None and float(body_fat) > 28:
            actions.append("保持温和能量缺口，不采用极端节食")

        if snapshot.get("medical_alert"):
            cautions.append("存在需要医学确认的事项，生活方式建议不能替代就医或复查")

        # De-duplicate while preserving order.
        priorities = list(dict.fromkeys(priorities))[:3]
        actions = list(dict.fromkeys(actions))[:5]
        cautions = list(dict.fromkeys(cautions))[:3]

        return HealthDecision(mode, priorities, actions, cautions)

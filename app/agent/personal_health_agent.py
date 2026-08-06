from dataclasses import dataclass


@dataclass
class HealthContext:
    sleep_hours: float
    hrv_ms: float
    steps: int
    protein_g: float
    body_fat: float


class PersonalHealthAgent:
    def decide(self, ctx: HealthContext):
        actions = []
        mode = "减脂推进"

        if ctx.sleep_hours < 6 or ctx.hrv_ms < 30:
            mode = "恢复优先"
            actions.append("降低高强度训练，优先恢复")

        if ctx.steps < 8000:
            actions.append("增加日常活动，目标8000步")

        if ctx.protein_g < 100:
            actions.append("提高蛋白质摄入至100-120g")

        if ctx.body_fat > 28:
            actions.append("继续执行减脂保肌策略")

        return {
            "mode": mode,
            "actions": actions
        }

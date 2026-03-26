from __future__ import annotations

from .models import CommunicationStyle, DailyDecision


class HumanEngine:
    """人感表达层：专业结论不变，表达方式可变。"""

    def render_daily_message(self, decision: DailyDecision, style: CommunicationStyle) -> str:
        core = f"今天状态：{decision.recovery_level.value}。{decision.reason}"

        if style == CommunicationStyle.RATIONAL:
            return (
                f"{core} "
                f"训练建议：{decision.training_action} "
                f"饮食建议：{decision.nutrition_action}"
            )

        if style == CommunicationStyle.COMPANION:
            return (
                f"{core} 今天不用硬顶，先把关键动作做稳。"
                f"训练上：{decision.training_action}。"
                f"饮食上：{decision.nutrition_action}。"
            )

        if style == CommunicationStyle.ENCOURAGING:
            return (
                f"{core} 你不需要追求满分，完成关键动作就会继续进步。"
                f"训练：{decision.training_action}；"
                f"饮食：{decision.nutrition_action}。"
            )

        return (
            f"{core} 你可以按这个方案执行，也可微调。"
            f"建议训练：{decision.training_action}。"
            f"建议饮食：{decision.nutrition_action}。"
        )

    def render_reactivation_message(self, days_break: int) -> str:
        if days_break <= 0:
            return "今天继续保持一个最小动作就很好。"
        return "今天重新开始就够了，不需要补前面的记录。先完成一个最小动作。"

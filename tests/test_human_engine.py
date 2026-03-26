from fitness_ai.human_engine import HumanEngine
from fitness_ai.models import CommunicationStyle, DailyDecision, RecoveryLevel


def _decision() -> DailyDecision:
    return DailyDecision(
        recovery_level=RecoveryLevel.STEADY,
        reason="状态中等，建议稳态完成关键动作。",
        training_action="主动作不变，辅助动作减少 1 个。",
        nutrition_action="晚餐补充约 25g 蛋白",
    )


def test_render_rational_style():
    engine = HumanEngine()

    msg = engine.render_daily_message(_decision(), CommunicationStyle.RATIONAL)

    assert "今天状态" in msg
    assert "训练建议" in msg


def test_reactivation_message_non_judgmental():
    engine = HumanEngine()

    msg = engine.render_reactivation_message(days_break=5)

    assert "重新开始" in msg
    assert "不需要补前面的记录" in msg
    assert "没来了" not in msg

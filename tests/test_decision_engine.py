from fitness_ai.decision_engine import DecisionEngine
from fitness_ai.models import DailySignals, RecoveryLevel, WeeklySummaryInput


def test_recover_when_sleep_debt_and_high_fatigue():
    engine = DecisionEngine()
    signals = DailySignals(
        sleep_hours=5.5,
        sleep_trend_delta=-1.2,
        consecutive_training_days=3,
        subjective_fatigue=8,
        resting_heart_rate_delta=5,
        meal_protein_gap_g=30,
        calorie_over_target=200,
    )

    result = engine.evaluate_daily(signals)

    assert result.recovery_level == RecoveryLevel.RECOVER
    assert "晚餐补充约 30g 蛋白" in result.nutrition_action


def test_push_when_readiness_good():
    engine = DecisionEngine()
    signals = DailySignals(
        sleep_hours=7.5,
        sleep_trend_delta=0.3,
        consecutive_training_days=1,
        subjective_fatigue=3,
        resting_heart_rate_delta=2,
        lower_body_load_high=False,
    )

    result = engine.evaluate_daily(signals)

    assert result.recovery_level == RecoveryLevel.PUSH
    assert "执行计划主训练" in result.training_action


def test_weekly_summary_single_action():
    engine = DecisionEngine()
    summary = engine.build_weekly_summary(
        WeeklySummaryInput(
            training_completion_rate=0.85,
            weight_delta_kg=-0.05,
            high_calorie_meals=3,
            avg_sleep_hours=6.8,
        )
    )

    assert "本周训练完成度较高" in summary.progress
    assert "高热量进食偏多" in summary.blocker
    assert "下周只做一件事" in summary.next_single_action

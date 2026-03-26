from __future__ import annotations

from .models import DailyDecision, DailySignals, RecoveryLevel, WeeklySummary, WeeklySummaryInput


class DecisionEngine:
    """规则优先的 MVP 决策引擎。"""

    def evaluate_daily(self, signals: DailySignals) -> DailyDecision:
        level, reason = self._classify_recovery(signals)
        training_action = self._training_action(level, signals)
        nutrition_action = self._nutrition_action(signals)
        return DailyDecision(
            recovery_level=level,
            reason=reason,
            training_action=training_action,
            nutrition_action=nutrition_action,
        )

    def build_weekly_summary(self, data: WeeklySummaryInput) -> WeeklySummary:
        progress = self._build_progress(data)
        blocker = self._build_blocker(data)
        effective_behavior = self._build_effective_behavior(data)
        next_single_action = self._build_next_action(data)
        return WeeklySummary(
            progress=progress,
            blocker=blocker,
            effective_behavior=effective_behavior,
            next_single_action=next_single_action,
        )

    def _classify_recovery(self, signals: DailySignals) -> tuple[RecoveryLevel, str]:
        severe_sleep_debt = signals.sleep_hours < 6.0 or signals.sleep_trend_delta <= -1.0
        high_fatigue = signals.subjective_fatigue >= 7
        cardio_stress = signals.resting_heart_rate_delta >= 8

        if severe_sleep_debt and high_fatigue and signals.consecutive_training_days >= 2:
            return RecoveryLevel.RECOVER, "睡眠不足且疲劳偏高，建议恢复优先。"

        if cardio_stress and signals.subjective_fatigue >= 6:
            return RecoveryLevel.RECOVER, "心率压力偏高，今天不建议硬撑强度。"

        good_readiness = (
            signals.sleep_hours >= 7.0
            and signals.subjective_fatigue <= 4
            and signals.consecutive_training_days <= 1
            and signals.resting_heart_rate_delta <= 3
        )
        if good_readiness:
            return RecoveryLevel.PUSH, "恢复信号稳定，可完成主训练目标。"

        return RecoveryLevel.STEADY, "状态中等，建议稳态完成关键动作。"

    def _training_action(self, level: RecoveryLevel, signals: DailySignals) -> str:
        if level == RecoveryLevel.RECOVER:
            return "保留技术动作或轻有氧 20~30 分钟，取消高负荷辅助动作。"
        if level == RecoveryLevel.PUSH:
            if signals.lower_body_load_high:
                return "可冲主训练，但下肢辅助动作减少 1 个以控制累积负荷。"
            return "执行计划主训练，主动作维持目标组数与重量。"
        return "保持中等强度，主动作不变，辅助动作总量下调约 15%。"

    def _nutrition_action(self, signals: DailySignals) -> str:
        actions: list[str] = []
        if signals.meal_protein_gap_g > 0:
            actions.append(f"晚餐补充约 {signals.meal_protein_gap_g}g 蛋白")
        if signals.calorie_over_target > 0:
            actions.append("晚餐主食减少约 1/3，避免高油高糖")
        if not actions:
            actions.append("维持当前饮食结构，优先保证蛋白和饮水")
        return "；".join(actions)

    def _build_progress(self, data: WeeklySummaryInput) -> str:
        if data.training_completion_rate >= 0.8 and data.weight_delta_kg < -0.2:
            return "本周推进良好：训练完成度高且体重趋势向目标方向变化。"
        if data.training_completion_rate >= 0.8:
            return "本周训练完成度较高，但体重变化有限。"
        return "本周执行度一般，目标推进受限。"

    def _build_blocker(self, data: WeeklySummaryInput) -> str:
        if data.high_calorie_meals >= 2:
            return "周末高热量进食偏多，抵消了平日热量缺口。"
        if data.avg_sleep_hours < 6.5:
            return "平均睡眠偏低，影响恢复与训练质量。"
        return "训练频次和饮食波动共同影响了阶段推进。"

    def _build_effective_behavior(self, data: WeeklySummaryInput) -> str:
        if data.training_completion_rate >= 0.75:
            return "固定完成力量训练是本周最有效行为。"
        return "保持基础活动与记录连续性是当前有效行为。"

    def _build_next_action(self, data: WeeklySummaryInput) -> str:
        if data.high_calorie_meals >= 2:
            return "下周只做一件事：控制两次晚餐主食份量。"
        if data.avg_sleep_hours < 6.5:
            return "下周只做一件事：连续 5 天把入睡时间提前 30 分钟。"
        return "下周只做一件事：固定 3 次训练并完成训练后记录。"

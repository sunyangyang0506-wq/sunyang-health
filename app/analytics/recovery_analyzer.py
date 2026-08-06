from typing import Dict


def calculate_recovery_score(sleep_hours: float, hrv_ms: float, resting_hr: int) -> Dict:
    score = 100
    reasons = []

    if sleep_hours < 5:
        score -= 25
        reasons.append("睡眠不足")
    elif sleep_hours < 6:
        score -= 10
        reasons.append("睡眠偏少")

    if hrv_ms < 25:
        score -= 20
        reasons.append("HRV偏低")
    elif hrv_ms < 35:
        score -= 10
        reasons.append("HRV一般")

    if resting_hr > 70:
        score -= 10
        reasons.append("静息心率偏高")

    return {
        "score": max(score, 0),
        "status": "恢复良好" if score >= 80 else "需要恢复",
        "reasons": reasons
    }

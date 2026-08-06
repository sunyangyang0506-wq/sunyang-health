from enum import Enum


class HealthMode(str, Enum):
    FAT_LOSS = "减脂推进模式"
    RECOVERY = "恢复优先模式"
    MUSCLE_PROTECTION = "保肌模式"
    CYCLE_ADJUSTMENT = "周期调整模式"
    MEDICAL_ATTENTION = "健康关注模式"


def select_mode(profile, metrics):
    if metrics.get("sleep_hours", 8) < 5:
        return HealthMode.RECOVERY

    if metrics.get("body_fat_percent", 0) > profile.get("target_body_fat_upper", 28):
        return HealthMode.FAT_LOSS

    return HealthMode.MUSCLE_PROTECTION

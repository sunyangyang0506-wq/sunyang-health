from typing import Dict


def analyze_activity(steps: int, vo2max: float | None = None) -> Dict:
    result = {}

    if steps < 6000:
        result["activity_status"] = "活动量不足"
        result["recommendation"] = "每日增加2000-3000步，恢复Zone2训练"
    else:
        result["activity_status"] = "活动水平良好"

    if vo2max is not None:
        result["cardio_status"] = "心肺能力需要提升" if vo2max < 35 else "心肺能力良好"

    return result

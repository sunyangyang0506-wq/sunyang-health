from typing import Dict


def analyze_body(weight: float, body_fat: float, muscle_mass: float) -> Dict:
    result = {}

    if body_fat > 30:
        result["fat_status"] = "体脂偏高，需要降低脂肪"
    elif body_fat <= 28:
        result["fat_status"] = "达到目标区间"
    else:
        result["fat_status"] = "持续优化"

    if muscle_mass < 47:
        result["muscle_status"] = "需要加强肌肉保护"
        result["recommendation"] = "提高蛋白质摄入并增加力量训练"
    else:
        result["muscle_status"] = "肌肉状态稳定"

    return result

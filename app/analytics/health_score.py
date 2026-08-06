def calculate_health_score(body: float, fitness: float, recovery: float, nutrition: float) -> int:
    score = (
        body * 0.30
        + fitness * 0.25
        + recovery * 0.25
        + nutrition * 0.20
    )

    return round(score)

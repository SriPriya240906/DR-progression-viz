import numpy as np
from model import predict_details

# DR severity order
STAGES = [0, 1, 2, 3, 4]


def progression_risk(current_grade):
    """
    Simple clinically-inspired risk model
    (can later be replaced with deep learning model)
    """

    risk = {}

    for next_stage in STAGES:

        # base rule: higher stage = higher risk
        distance = abs(next_stage - current_grade)

        # probability decreases with distance
        score = np.exp(-distance)

        risk[next_stage] = float(score)

    # normalize
    total = sum(risk.values())
    for k in risk:
        risk[k] /= total

    return risk


def predict_progression(image_path):
    """
    Returns:
    - current grade
    - progression probability map
    """

    details = predict_details(image_path)

    current = details["grade"]

    risk_map = progression_risk(current)

    next_stage = max(risk_map, key=risk_map.get)

    return {
        "current_grade": current,
        "next_likely_stage": next_stage,
        "risk_map": risk_map
    }
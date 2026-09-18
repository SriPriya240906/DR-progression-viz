from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any


CALIBRATION_UNAVAILABLE_REASON = (
    "Temperature scaling was not fitted because the repository has no populated, persisted "
    "held-out validation or evaluation split."
)


def _probability_vector(probabilities: Mapping[Any, float] | Sequence[float]) -> list[float]:
    if isinstance(probabilities, Mapping):
        values = list(probabilities.values())
    elif isinstance(probabilities, Sequence) and not isinstance(probabilities, (str, bytes)):
        values = list(probabilities)
    else:
        raise ValueError("Probabilities must be a mapping or a numeric sequence.")

    if not values:
        raise ValueError("At least one probability is required.")

    try:
        numeric = [float(value) for value in values]
    except (TypeError, ValueError) as exc:
        raise ValueError("Probabilities must be numeric.") from exc

    if any(not math.isfinite(value) or value < 0 for value in numeric):
        raise ValueError("Probabilities must be finite and non-negative.")

    total = sum(numeric)
    if total <= 0:
        raise ValueError("Probability mass must be greater than zero.")
    return [value / total for value in numeric]


def analyze_prediction_reliability(
    probabilities: Mapping[Any, float] | Sequence[float],
    predicted_index: int | None = None,
    predicted_label: str | None = None,
) -> dict[str, Any]:
    """Return probability-distribution uncertainty without inventing a reliability score."""
    normalized = _probability_vector(probabilities)
    ranked = sorted(enumerate(normalized), key=lambda item: item[1], reverse=True)
    top_index, top_probability = ranked[0]
    second_probability = ranked[1][1] if len(ranked) > 1 else 0.0
    entropy = -sum(value * math.log(value) for value in normalized if value > 0)
    max_entropy = math.log(len(normalized)) if len(normalized) > 1 else 0.0
    normalized_entropy = entropy / max_entropy if max_entropy else 0.0

    if predicted_index is not None and predicted_index != top_index:
        raise ValueError("The predicted index does not match the top probability.")

    return {
        "available": True,
        "predicted_index": top_index,
        "predicted_label": predicted_label,
        "confidence": round(top_probability, 6),
        "top_probability": round(top_probability, 6),
        "second_probability": round(second_probability, 6),
        "probability_margin": round(top_probability - second_probability, 6),
        "predictive_entropy": round(abs(entropy), 6),
        "normalized_predictive_entropy": round(abs(normalized_entropy), 6),
        "calibration": {
            "available": False,
            "method": "temperature_scaling",
            "reason": CALIBRATION_UNAVAILABLE_REASON,
        },
        "interpretation": (
            "These are model probability-distribution metrics, not clinical uncertainty or diagnostic certainty. "
            "The 'confidence' field represents the maximum softmax probability (uncalibrated). "
            "Prediction probability should be interpreted with the probability margin and predictive entropy; clinical review remains required."
        ),
    }

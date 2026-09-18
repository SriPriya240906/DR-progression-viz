import math

import pytest

from backend.reliability import analyze_prediction_reliability


def test_probability_metrics_are_computed_from_distribution():
    result = analyze_prediction_reliability([0.1, 0.7, 0.2], predicted_index=1, predicted_label="Mild")

    assert result["top_probability"] == pytest.approx(0.7)
    assert result["second_probability"] == pytest.approx(0.2)
    assert result["probability_margin"] == pytest.approx(0.5)
    assert result["predictive_entropy"] == pytest.approx(-sum(value * math.log(value) for value in [0.1, 0.7, 0.2]))
    assert 0 < result["normalized_predictive_entropy"] < 1
    assert result["calibration"]["available"] is False


def test_uniform_distribution_has_maximum_normalized_entropy():
    result = analyze_prediction_reliability([0.25, 0.25, 0.25, 0.25])

    assert result["probability_margin"] == 0
    assert result["normalized_predictive_entropy"] == pytest.approx(1.0)


def test_concentrated_distribution_has_low_entropy():
    result = analyze_prediction_reliability([1.0, 0.0, 0.0, 0.0])

    assert result["top_probability"] == 1
    assert result["probability_margin"] == 1
    assert result["predictive_entropy"] == 0
    assert result["normalized_predictive_entropy"] == 0


def test_mapping_values_are_normalized_and_ranked():
    result = analyze_prediction_reliability({"No DR": 10, "Mild": 70, "Moderate": 20})

    assert result["predicted_index"] == 1
    assert result["top_probability"] == pytest.approx(0.7)


@pytest.mark.parametrize("probabilities", [[], [float("nan"), 1], [float("inf"), 1], [-0.1, 1], [0, 0]])
def test_malformed_probabilities_are_rejected(probabilities):
    with pytest.raises(ValueError):
        analyze_prediction_reliability(probabilities)


def test_mismatched_predicted_index_is_rejected():
    with pytest.raises(ValueError, match="top probability"):
        analyze_prediction_reliability([0.8, 0.2], predicted_index=1)

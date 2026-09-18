from backend.evidence import build_evidence_summary


def complete_analysis():
    return {
        "prediction": {"grade": 2, "label": "Moderate", "confidence": 100.0},
        "quality": {"status": "BORDERLINE", "warnings": ["Focus may affect AI-assisted analysis."]},
        "reliability": {
            "available": True,
            "top_probability": 1.0,
            "second_probability": 0.0,
            "probability_margin": 1.0,
            "predictive_entropy": 0.0,
            "normalized_predictive_entropy": 0.0,
            "calibration": {"available": False},
        },
        "structure": {"available": True, "vessels": {"vessel_like_fraction": 0.02, "confidence_available": False}},
        "lesion_evidence": {
            "available": True,
            "dark_candidates": {"count": 3, "fraction": 0.01},
            "bright_candidates": {"count": 2, "fraction": 0.02},
        },
        "gradcam": {"available": True},
    }


def test_complete_summary_is_deterministic_and_has_no_combined_score():
    first = build_evidence_summary(complete_analysis())
    second = build_evidence_summary(complete_analysis())

    assert first == second
    assert first["prediction"]["grade"] == 2
    assert first["model_uncertainty"]["calibration_status"].startswith("Calibration has not")
    assert first["clinical_review"]["required"] is True
    assert "score" not in first
    assert "probability" not in first


def test_missing_signals_remain_explicitly_unavailable():
    summary = build_evidence_summary({"prediction": {"grade": 0, "label": "No DR", "confidence": 80.0}})

    assert summary["available"] is True
    assert summary["image_quality"]["available"] is False
    assert summary["model_uncertainty"]["available"] is False
    assert summary["retinal_structure"]["available"] is False
    assert summary["lesion_evidence"]["available"] is False
    assert summary["model_explanation"]["gradcam_available"] is False
    assert summary["clinical_review"]["required"] is True


def test_summary_does_not_change_prediction_values():
    analysis = complete_analysis()
    summary = build_evidence_summary(analysis)

    assert summary["prediction"]["grade"] == analysis["prediction"]["grade"]
    assert summary["prediction"]["confidence"] == analysis["prediction"]["confidence"]

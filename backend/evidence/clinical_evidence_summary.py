from __future__ import annotations

from typing import Any


GRADE_LABELS = {
    0: "No Diabetic Retinopathy",
    1: "Mild",
    2: "Moderate",
    3: "Severe",
    4: "Proliferative DR",
}


def _prediction_summary(prediction: dict[str, Any] | None) -> dict[str, Any]:
    prediction = prediction or {}
    grade = prediction.get("grade")
    label = prediction.get("label") or GRADE_LABELS.get(grade, "Unknown")
    return {
        "grade": grade,
        "label": label,
        "confidence": prediction.get("confidence"),
        "statement": f"AI model predicts {label}." if label != "Unknown" else "The AI model prediction label is unavailable.",
    }


def _uncertainty_summary(reliability: dict[str, Any] | None) -> dict[str, Any]:
    if not reliability:
        return {
            "available": False,
            "summary": "Model probability-distribution uncertainty metrics are unavailable.",
            "calibration_status": "Calibration has not been established.",
        }
    calibration = reliability.get("calibration") or {}
    calibration_status = (
        "Calibration was evaluated on held-out data."
        if calibration.get("available")
        else "Calibration has not been established because a defensible held-out calibration set is unavailable."
    )
    return {
        "available": bool(reliability.get("available", True)),
        "top_probability": reliability.get("top_probability"),
        "second_probability": reliability.get("second_probability"),
        "probability_margin": reliability.get("probability_margin"),
        "predictive_entropy": reliability.get("predictive_entropy"),
        "normalized_predictive_entropy": reliability.get("normalized_predictive_entropy"),
        "calibration_status": calibration_status,
        "summary": "Prediction uncertainty is summarized using the model's probability distribution, not clinical certainty.",
    }


def _quality_summary(quality: dict[str, Any] | None) -> dict[str, Any]:
    if not quality:
        return {"available": False, "summary": "Image quality assessment is unavailable."}
    warnings = quality.get("warnings") or []
    status = quality.get("status") or quality.get("overall") or "Unavailable"
    return {
        "available": True,
        "status": status,
        "focus": quality.get("focus"),
        "illumination": quality.get("illumination"),
        "contrast": quality.get("contrast"),
        "resolution": quality.get("resolution"),
        "field_of_view": quality.get("field_of_view"),
        "retinal_visibility": quality.get("retinal_visibility"),
        "warnings": warnings,
        "summary": f"Image quality status is {status}. Image quality can affect interpretation of AI-assisted analysis.",
    }


def _explanation_summary(gradcam: dict[str, Any] | None) -> dict[str, Any]:
    available = bool((gradcam or {}).get("available"))
    return {
        "gradcam_available": available,
        "summary": (
            "Grad-CAM highlights image regions that contributed to the model prediction. These regions are not confirmed lesions."
            if available
            else "Grad-CAM was unavailable for this analysis."
        ),
    }


def _structure_summary(structure: dict[str, Any] | None) -> dict[str, Any]:
    if not structure:
        return {"available": False, "summary": "Experimental retinal structure evidence is unavailable."}
    vessels = structure.get("vessels") or {}
    return {
        "available": bool(structure.get("available")),
        "field_of_view": structure.get("field_of_view"),
        "vessel_like_fraction": vessels.get("vessel_like_fraction"),
        "vessel_confidence_available": bool(vessels.get("confidence_available", False)),
        "optic_disc_available": bool((structure.get("optic_disc") or {}).get("available")),
        "fovea_available": bool((structure.get("fovea") or {}).get("available")),
        "summary": "Experimental vessel-like structure estimation is available. It is not a validated vessel segmentation model.",
    }


def _lesion_summary(lesion_evidence: dict[str, Any] | None) -> dict[str, Any]:
    if not lesion_evidence:
        return {"available": False, "summary": "Experimental lesion candidate evidence is unavailable."}
    dark = lesion_evidence.get("dark_candidates") or {}
    bright = lesion_evidence.get("bright_candidates") or {}
    return {
        "available": bool(lesion_evidence.get("available")),
        "dark_candidate_count": dark.get("count", 0),
        "dark_candidate_fraction": dark.get("fraction"),
        "bright_candidate_count": bright.get("count", 0),
        "bright_candidate_fraction": bright.get("fraction"),
        "overlay_image_urls": lesion_evidence.get("overlay_image_urls") or {},
        "summary": "Experimental image-processing identified localized dark/bright candidate regions. These candidates are not confirmed clinical lesions.",
    }


def build_evidence_summary(analysis: dict[str, Any] | None) -> dict[str, Any]:
    """Organize existing evidence without combining it into a medical score."""
    analysis = analysis or {}
    prediction = _prediction_summary(analysis.get("prediction"))
    return {
        "available": bool(analysis.get("prediction")),
        "prediction": prediction,
        "model_uncertainty": _uncertainty_summary(analysis.get("reliability")),
        "image_quality": _quality_summary(analysis.get("quality") or analysis.get("image_quality")),
        "model_explanation": _explanation_summary(analysis.get("gradcam")),
        "retinal_structure": _structure_summary(analysis.get("structure")),
        "lesion_evidence": _lesion_summary(analysis.get("lesion_evidence")),
        "clinical_review": {
            "required": True,
            "reason": "AI-assisted analysis and experimental image evidence require clinical review and are not a standalone diagnosis.",
        },
        "limitations": [
            "Model prediction probability is not clinical certainty.",
            "Calibration has not been established when no defensible held-out calibration set is available.",
            "Grad-CAM shows model-contributing regions and does not prove a lesion exists.",
            "Vessel-like structure and dark/bright candidate regions are experimental image evidence, not confirmed clinical findings.",
            "No combined evidence score or disease probability is calculated.",
        ],
    }

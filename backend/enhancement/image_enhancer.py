from __future__ import annotations

from typing import Any

import cv2
import numpy as np

from backend.quality import analyze_image_quality


FOCUS_TOLERANCE = 0.80
STATUS_RANK = {"GOOD": 0, "BORDERLINE": 1, "POOR": 2}


def _metric_value(result: dict[str, Any], group: str, key: str = "value") -> float:
    value = result.get(group, {}).get(key, 0.0)
    return float(value or 0.0)


def _change(original: dict[str, Any], enhanced: dict[str, Any], group: str, key: str = "value") -> float:
    return round(_metric_value(enhanced, group, key) - _metric_value(original, group, key), 4)


def _focus_is_safe(original: dict[str, Any], enhanced: dict[str, Any]) -> bool:
    original_focus = _metric_value(original, "focus")
    enhanced_focus = _metric_value(enhanced, "focus")
    if original_focus <= 0:
        return enhanced_focus > 0
    return enhanced_focus >= original_focus * FOCUS_TOLERANCE


def _improved(original: dict[str, Any], enhanced: dict[str, Any]) -> tuple[bool, str]:
    original_status = original.get("status", "POOR")
    enhanced_status = enhanced.get("status", "POOR")
    focus_safe = _focus_is_safe(original, enhanced)
    contrast_change = _change(original, enhanced, "contrast")
    illumination_change = _change(original, enhanced, "illumination")
    visibility_change = _change(original, enhanced, "retinal_visibility", "estimated_visible_fraction")

    if not focus_safe:
        return False, "Candidate rejected because the focus metric deteriorated materially."
    if STATUS_RANK.get(enhanced_status, 2) < STATUS_RANK.get(original_status, 2):
        return True, "Quality status improved without a material focus deterioration."

    improved_metrics = sum(change > 0 for change in (contrast_change, illumination_change, visibility_change))
    if improved_metrics >= 2 and enhanced_status == original_status:
        return True, "Multiple quality metrics improved without a material focus deterioration."
    return False, "No meaningful overall quality improvement was detected."


def _clahe_candidate(image: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    lightness, chroma_a, chroma_b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
    enhanced_lightness = clahe.apply(lightness)
    return cv2.cvtColor(cv2.merge((enhanced_lightness, chroma_a, chroma_b)), cv2.COLOR_LAB2BGR)


def _enhancement_is_reasonable(image: np.ndarray, quality: dict[str, Any]) -> tuple[bool, str]:
    height, width = image.shape[:2]
    focus = _metric_value(quality, "focus")
    contrast = _metric_value(quality, "contrast")
    if min(width, height) < 64:
        return False, "Enhancement was not attempted because the image is too small for a useful preview."
    if focus <= 0.01 and contrast <= 1.0:
        return False, "Enhancement was not attempted because the image contains no measurable structure to recover."
    return True, ""


def enhance_image(image: np.ndarray, quality_result: dict[str, Any] | None = None) -> dict[str, Any]:
    """Try a conservative CLAHE candidate and compare it with the original metrics."""
    if image is None or not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("The image is empty or invalid.")

    original_quality = quality_result or analyze_image_quality(image)
    if original_quality.get("status") == "GOOD":
        return {
            "attempted": False,
            "method": None,
            "improved": False,
            "accepted": False,
            "image": None,
            "original_quality": original_quality,
            "enhanced_quality": None,
            "changes": {},
            "recommendation": "Enhancement not required. The original image will be used.",
            "message": "Image quality is already within the experimental screening bands.",
        }

    can_attempt, reason = _enhancement_is_reasonable(image, original_quality)
    if not can_attempt:
        return {
            "attempted": False,
            "method": None,
            "improved": False,
            "accepted": False,
            "image": None,
            "original_quality": original_quality,
            "enhanced_quality": None,
            "changes": {},
            "recommendation": "Consider capturing another retinal image; the original image remains available for review.",
            "message": reason,
        }

    candidate = _clahe_candidate(image)
    enhanced_quality = analyze_image_quality(candidate)
    improved, message = _improved(original_quality, enhanced_quality)
    changes = {
        "focus": _change(original_quality, enhanced_quality, "focus"),
        "contrast": _change(original_quality, enhanced_quality, "contrast"),
        "illumination": _change(original_quality, enhanced_quality, "illumination"),
        "retinal_visibility": _change(original_quality, enhanced_quality, "retinal_visibility", "estimated_visible_fraction"),
    }
    return {
        "attempted": True,
        "method": "CLAHE on luminance channel",
        "improved": improved,
        "accepted": improved,
        "image": candidate,
        "original_quality": original_quality,
        "enhanced_quality": enhanced_quality,
        "changes": changes,
        "recommendation": (
            "The enhanced preview improved experimental quality metrics; the original image remains the DR model input."
            if improved
            else "No meaningful quality improvement detected. Consider capturing another retinal image."
        ),
        "message": message,
    }
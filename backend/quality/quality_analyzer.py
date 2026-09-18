from __future__ import annotations

from typing import Any

import cv2
import numpy as np


# Experimental screening bands informed by 200 sampled project images; not clinical criteria.
MIN_WIDTH = 224
MIN_HEIGHT = 224
MIN_PROCESSING_DIMENSION = 16
FOCUS_POOR = 5.0
FOCUS_BORDERLINE = 10.0
BRIGHTNESS_LOW = 20.0
BRIGHTNESS_HIGH = 220.0
EXTREME_PIXEL_FRACTION = 0.35
CONTRAST_POOR = 17.0
CONTRAST_BORDERLINE = 25.0


def _status_for_focus(value: float) -> str:
    if value < FOCUS_POOR:
        return "POOR"
    if value < FOCUS_BORDERLINE:
        return "BORDERLINE"
    return "GOOD"


def _status_for_illumination(mean: float, dark_fraction: float, bright_fraction: float) -> str:
    if mean < BRIGHTNESS_LOW or mean > BRIGHTNESS_HIGH or dark_fraction >= 0.65 or bright_fraction >= EXTREME_PIXEL_FRACTION:
        return "POOR"
    if mean < 35 or mean > 195 or dark_fraction >= 0.6 or bright_fraction >= 0.2:
        return "BORDERLINE"
    return "GOOD"


def _status_for_contrast(value: float) -> str:
    if value < CONTRAST_POOR:
        return "POOR"
    if value < CONTRAST_BORDERLINE:
        return "BORDERLINE"
    return "GOOD"


def _field_of_view_metrics(image: np.ndarray) -> tuple[float, float, str]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    candidate = (gray > 12).astype(np.uint8)
    candidate = cv2.morphologyEx(candidate, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    candidate = cv2.morphologyEx(candidate, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    contours, _ = cv2.findContours(candidate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return 0.0, 0.0, "Field-of-view assessment limited; no stable retinal-region estimate was found."

    largest = max(contours, key=cv2.contourArea)
    area_fraction = float(cv2.contourArea(largest) / (image.shape[0] * image.shape[1]))
    mask = np.zeros(gray.shape, dtype=np.uint8)
    cv2.drawContours(mask, [largest], -1, 255, thickness=-1)
    visible = gray > 12
    visibility_fraction = float(np.mean(visible[mask > 0])) if np.any(mask) else 0.0
    assessment = (
        "Limited apparent retinal field; this heuristic is not a clinical gradability assessment."
        if area_fraction < 0.08
        else "A visually non-empty image region was detected; field-of-view assessment is heuristic."
    )
    return area_fraction, visibility_fraction, assessment


def analyze_image_quality(image: np.ndarray) -> dict[str, Any]:
    """Analyze a BGR OpenCV image without invoking any DR model."""
    if image is None or not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("The image is empty or invalid.")
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("The image must have three color channels.")

    height, width = image.shape[:2]
    if width < MIN_PROCESSING_DIMENSION or height < MIN_PROCESSING_DIMENSION:
        raise ValueError("The image is too small for quality analysis.")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    focus_value = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness_value = float(gray.mean())
    contrast_value = float(gray.std())
    dark_fraction = float(np.mean(gray <= 8))
    bright_fraction = float(np.mean(gray >= 247))
    focus_status = _status_for_focus(focus_value)
    illumination_status = _status_for_illumination(brightness_value, dark_fraction, bright_fraction)
    contrast_status = _status_for_contrast(contrast_value)
    resolution_status = "GOOD" if width >= MIN_WIDTH and height >= MIN_HEIGHT else "POOR"
    field_fraction, visibility_fraction, field_assessment = _field_of_view_metrics(image)
    visibility_status = "GOOD" if visibility_fraction >= 0.5 else "BORDERLINE"
    statuses = [focus_status, illumination_status, contrast_status, resolution_status, visibility_status]
    overall_status = max(statuses, key={"GOOD": 0, "BORDERLINE": 1, "POOR": 2}.get)

    warnings: list[str] = []
    if focus_status != "GOOD":
        warnings.append("Focus may affect AI-assisted analysis.")
    if illumination_status != "GOOD":
        warnings.append("Illumination may affect AI-assisted analysis.")
    if contrast_status != "GOOD":
        warnings.append("Contrast may affect AI-assisted analysis.")
    if resolution_status != "GOOD":
        warnings.append("Image resolution is below the experimental analysis band.")
    if visibility_status != "GOOD":
        warnings.append("Retinal visibility is limited by this image-only heuristic.")

    recommendation = {
        "GOOD": "Image appears suitable for AI-assisted analysis based on experimental image-level checks.",
        "BORDERLINE": "Image quality may affect AI-assisted analysis; review the image and consider reacquisition if needed.",
        "POOR": "Consider capturing another retinal image with better focus, illumination, contrast, and field coverage.",
    }[overall_status]
    assessment = {
        "GOOD": "Image-level metrics are within the experimental screening bands.",
        "BORDERLINE": "One or more image-level metrics are borderline.",
        "POOR": "One or more image-level metrics are poor under the experimental screening bands.",
    }[overall_status]

    return {
        "status": overall_status,
        "overall_assessment": assessment,
        "resolution": {
            "width": width,
            "height": height,
            "aspect_ratio": round(width / height, 4),
            "assessment": "Resolution meets the experimental minimum band." if resolution_status == "GOOD" else "Resolution is below the experimental minimum band.",
        },
        "focus": {
            "metric": "variance_of_laplacian",
            "value": round(focus_value, 4),
            "assessment": {"GOOD": "Focus metric is within the experimental reference band.", "BORDERLINE": "Focus metric is borderline.", "POOR": "Possible blur; focus metric is low."}[focus_status],
        },
        "illumination": {
            "metric": "grayscale_mean",
            "value": round(brightness_value, 4),
            "dark_pixel_fraction": round(dark_fraction, 4),
            "bright_pixel_fraction": round(bright_fraction, 4),
            "assessment": {"GOOD": "Illumination is within the experimental reference band.", "BORDERLINE": "Illumination may be uneven or near an exposure boundary.", "POOR": "Possible underexposure or overexposure."}[illumination_status],
        },
        "contrast": {
            "metric": "grayscale_standard_deviation",
            "value": round(contrast_value, 4),
            "assessment": {"GOOD": "Contrast is within the experimental reference band.", "BORDERLINE": "Contrast is borderline.", "POOR": "Contrast is low."}[contrast_status],
        },
        "field_of_view": {"estimated_region_fraction": round(field_fraction, 4), "assessment": field_assessment},
        "retinal_visibility": {
            "estimated_visible_fraction": round(visibility_fraction, 4),
            "assessment": "A meaningful non-empty image region is suggested by this heuristic." if visibility_status == "GOOD" else "Retinal visibility assessment is limited; review the image manually.",
        },
        "warnings": warnings,
        "recommendation": recommendation,
        "methodology": {
            "threshold_type": "heuristic / experimental",
            "validated_clinically": False,
            "dataset_used": "200 images sampled from dataset/train during Phase 2 inspection.",
        },
    }
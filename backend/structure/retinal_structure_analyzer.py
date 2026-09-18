from __future__ import annotations

from typing import Any

import cv2
import numpy as np

from backend.quality.quality_analyzer import _field_of_view_metrics

MIN_PROCESSING_DIMENSION = 16
MAX_WORKING_DIMENSION = 1024
MIN_FOV_FRACTION = 0.08
MIN_FOV_VISIBILITY = 0.5
MIN_COMPONENT_AREA = 5


def _validate_image(image: np.ndarray) -> tuple[int, int]:
    if image is None or not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("The image is empty or invalid.")
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("The image must have three color channels.")
    height, width = image.shape[:2]
    if width < MIN_PROCESSING_DIMENSION or height < MIN_PROCESSING_DIMENSION:
        raise ValueError("The image is too small for structural analysis.")
    return height, width


def _retinal_region_mask(image: np.ndarray) -> tuple[np.ndarray, float, float]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    candidate = (gray > 12).astype(np.uint8)
    candidate = cv2.morphologyEx(candidate, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    candidate = cv2.morphologyEx(candidate, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    contours, _ = cv2.findContours(candidate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return np.zeros(gray.shape, dtype=np.uint8), 0.0, 0.0

    largest = max(contours, key=cv2.contourArea)
    mask = np.zeros(gray.shape, dtype=np.uint8)
    cv2.drawContours(mask, [largest], -1, 255, thickness=-1)
    area_fraction = float(np.count_nonzero(mask) / mask.size)
    visible_fraction = float(np.mean(gray[mask > 0] > 12)) if np.any(mask) else 0.0
    return mask, area_fraction, visible_fraction


def _working_image(image: np.ndarray) -> tuple[np.ndarray, float, float]:
    height, width = image.shape[:2]
    scale = min(1.0, MAX_WORKING_DIMENSION / max(height, width))
    if scale == 1.0:
        return image, 1.0, 1.0
    working = cv2.resize(image, (max(1, round(width * scale)), max(1, round(height * scale))), interpolation=cv2.INTER_AREA)
    return working, scale, scale


def _remove_small_components(mask: np.ndarray) -> np.ndarray:
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    cleaned = np.zeros(mask.shape, dtype=np.uint8)
    for label in range(1, count):
        if stats[label, cv2.CC_STAT_AREA] >= MIN_COMPONENT_AREA:
            cleaned[labels == label] = 255
    return cleaned


def _estimate_vessel_like_mask(image: np.ndarray, region_mask: np.ndarray) -> np.ndarray:
    green = image[:, :, 1]
    blackhat_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    dark_line_response = cv2.morphologyEx(green, cv2.MORPH_BLACKHAT, blackhat_kernel)
    region_values = dark_line_response[region_mask > 0]
    if region_values.size == 0 or float(region_values.max()) <= 0:
        return np.zeros(green.shape, dtype=np.uint8)

    threshold = max(float(np.percentile(region_values, 92)), 1.0)
    candidate = np.where((dark_line_response >= threshold) & (region_mask > 0), 255, 0).astype(np.uint8)
    candidate = cv2.morphologyEx(candidate, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return _remove_small_components(candidate)


def _overlay(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    result = image.copy()
    highlighted = mask > 0
    result[highlighted] = (0.45 * result[highlighted] + 0.55 * np.array([40, 220, 255])).astype(np.uint8)
    return result


def analyze_retinal_structure(image: np.ndarray) -> dict[str, Any]:
    """Estimate retinal field and vessel-like structures without a learned structure model."""
    height, width = _validate_image(image)
    working, _, _ = _working_image(image)
    fov_fraction_from_quality, visibility_fraction, _ = _field_of_view_metrics(working)
    working_region_mask, fov_fraction, region_visibility = _retinal_region_mask(working)
    region_mask = cv2.resize(working_region_mask, (width, height), interpolation=cv2.INTER_NEAREST)
    fov_fraction = fov_fraction or fov_fraction_from_quality
    sufficient = fov_fraction >= MIN_FOV_FRACTION and max(visibility_fraction, region_visibility) >= MIN_FOV_VISIBILITY

    field_of_view: dict[str, Any] = {
        "available": bool(np.any(region_mask)),
        "fraction": round(fov_fraction, 6),
        "sufficient_for_analysis": sufficient,
        "dimensions": {"width": width, "height": height},
    }

    if np.any(region_mask):
        moments = cv2.moments(region_mask)
        if moments["m00"]:
            field_of_view["center"] = {
                "x": round(float(moments["m10"] / moments["m00"]), 2),
                "y": round(float(moments["m01"] / moments["m00"]), 2),
            }
        ys, xs = np.where(region_mask > 0)
        field_of_view["extent"] = {
            "x_min": int(xs.min()),
            "y_min": int(ys.min()),
            "x_max": int(xs.max()),
            "y_max": int(ys.max()),
        }

    if sufficient:
        working_vessel_mask = _estimate_vessel_like_mask(working, working_region_mask)
        vessel_mask = cv2.resize(working_vessel_mask, (width, height), interpolation=cv2.INTER_NEAREST)
        fov_pixels = max(int(np.count_nonzero(working_region_mask)), 1)
        vessel_fraction = float(np.count_nonzero(working_vessel_mask) / fov_pixels)
        vessels: dict[str, Any] = {
            "available": True,
            "method": "Experimental vessel-like structure estimation using green-channel black-hat morphology",
            "confidence_available": False,
            "vessel_like_fraction": round(vessel_fraction, 6),
            "density": round(vessel_fraction, 6),
            "limitations": [
                "This candidate map is not validated vessel segmentation.",
                "Illumination, lesions, borders, and image artifacts can produce false vessel-like responses.",
            ],
        }
        visualization = _overlay(image, vessel_mask)
    else:
        vessel_mask = np.zeros((height, width), dtype=np.uint8)
        vessels = {
            "available": False,
            "method": "Experimental vessel-like structure estimation",
            "confidence_available": False,
            "reason": "Retinal field-of-view estimate is insufficient for a defensible structural candidate map.",
        }
        visualization = None

    return {
        "available": bool(field_of_view["available"]),
        "method_status": "experimental image-processing estimate; not a clinical measurement",
        "field_of_view": field_of_view,
        "vessels": vessels,
        "optic_disc": {
            "available": False,
            "reason": "No validated/local optic-disc localization model or annotations are available.",
        },
        "fovea": {
            "available": False,
            "reason": "No validated/local fovea localization model or annotations are available.",
        },
        "confidence_available": False,
        "limitations": [
            "Structural analysis is experimental and does not diagnose disease.",
            "No ground-truth vessel masks were available for quantitative validation.",
        ],
        "_mask": vessel_mask,
        "_visualization": visualization,
    }

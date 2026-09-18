from __future__ import annotations

import math
from typing import Any

import cv2
import numpy as np

MAX_WORKING_DIMENSION = 1024
MIN_PROCESSING_DIMENSION = 16
FOV_INTENSITY_FLOOR = 12
MIN_COMPONENT_AREA = 8
MAX_COMPONENT_FRACTION = 0.02
DARK_PERCENTILE = 97.0
BRIGHT_PERCENTILE = 99.0


def _validate_image(image: np.ndarray) -> tuple[int, int]:
    if image is None or not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("The image is empty or invalid.")
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("The image must have three color channels.")
    height, width = image.shape[:2]
    if width < MIN_PROCESSING_DIMENSION or height < MIN_PROCESSING_DIMENSION:
        raise ValueError("The image is too small for lesion candidate analysis.")
    return height, width


def _resize_for_working(image: np.ndarray) -> tuple[np.ndarray, float, float]:
    height, width = image.shape[:2]
    scale = min(1.0, MAX_WORKING_DIMENSION / max(height, width))
    if scale == 1.0:
        return image, 1.0, 1.0
    working_width = max(1, round(width * scale))
    working_height = max(1, round(height * scale))
    working = cv2.resize(image, (working_width, working_height), interpolation=cv2.INTER_AREA)
    return working, width / working_width, height / working_height


def _field_of_view_mask(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    candidate = (gray > FOV_INTENSITY_FLOOR).astype(np.uint8)
    candidate = cv2.morphologyEx(candidate, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    candidate = cv2.morphologyEx(candidate, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    contours, _ = cv2.findContours(candidate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return np.zeros(gray.shape, dtype=np.uint8)
    mask = np.zeros(gray.shape, dtype=np.uint8)
    cv2.drawContours(mask, [max(contours, key=cv2.contourArea)], -1, 255, thickness=-1)
    return mask


def _clean_components(mask: np.ndarray) -> np.ndarray:
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    cleaned = np.zeros(mask.shape, dtype=np.uint8)
    max_area = max(MIN_COMPONENT_AREA, int(mask.size * MAX_COMPONENT_FRACTION))
    for label in range(1, count):
        area = int(stats[label, cv2.CC_STAT_AREA])
        if MIN_COMPONENT_AREA <= area <= max_area:
            cleaned[labels == label] = 255
    return cleaned


def _candidate_masks(image: np.ndarray, fov_mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    green = image[:, :, 1]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    dark_response = cv2.morphologyEx(
        green,
        cv2.MORPH_BLACKHAT,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)),
    )
    bright_response = cv2.morphologyEx(
        gray,
        cv2.MORPH_TOPHAT,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)),
    )

    fov_values_dark = dark_response[fov_mask > 0]
    fov_values_bright = bright_response[fov_mask > 0]
    if fov_values_dark.size == 0 or fov_values_bright.size == 0:
        return np.zeros(gray.shape, dtype=np.uint8), np.zeros(gray.shape, dtype=np.uint8)

    dark_threshold = max(float(np.percentile(fov_values_dark, DARK_PERCENTILE)), 1.0)
    bright_threshold = max(float(np.percentile(fov_values_bright, BRIGHT_PERCENTILE)), 1.0)
    dark = np.where((dark_response >= dark_threshold) & (fov_mask > 0), 255, 0).astype(np.uint8)
    bright = np.where((bright_response >= bright_threshold) & (fov_mask > 0), 255, 0).astype(np.uint8)
    kernel = np.ones((3, 3), np.uint8)
    dark = cv2.morphologyEx(dark, cv2.MORPH_OPEN, kernel)
    bright = cv2.morphologyEx(bright, cv2.MORPH_OPEN, kernel)
    return _clean_components(dark), _clean_components(bright)


def _finite(value: float) -> float:
    return float(value) if math.isfinite(float(value)) else 0.0


def _regions(mask: np.ndarray, image: np.ndarray, fov_mask: np.ndarray, scale_x: float, scale_y: float) -> list[dict[str, Any]]:
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fov_area = max(int(np.count_nonzero(fov_mask)), 1)
    regions: list[dict[str, Any]] = []
    for label in range(1, count):
        x, y, width, height, area = (int(value) for value in stats[label])
        if area <= 0:
            continue
        component = labels == label
        original_x = int(round(x * scale_x))
        original_y = int(round(y * scale_y))
        original_width = max(1, int(round(width * scale_x)))
        original_height = max(1, int(round(height * scale_y)))
        original_width = min(original_width, image.shape[1] - original_x)
        original_height = min(original_height, image.shape[0] - original_y)
        if original_x >= image.shape[1] or original_y >= image.shape[0] or original_width <= 0 or original_height <= 0:
            continue
        region_values = gray[component]
        regions.append(
            {
                "x": original_x,
                "y": original_y,
                "width": original_width,
                "height": original_height,
                "area": max(1, int(round(area * scale_x * scale_y))),
                "centroid": {
                    "x": _finite(float(centroids[label][0] * scale_x)),
                    "y": _finite(float(centroids[label][1] * scale_y)),
                },
                "relative_centroid": {
                    "x": _finite(float(centroids[label][0] / max(mask.shape[1], 1))),
                    "y": _finite(float(centroids[label][1] / max(mask.shape[0], 1))),
                },
                "mean_intensity": round(_finite(float(region_values.mean())), 4),
                "local_fraction": round(_finite(float(area / fov_area)), 6),
            }
        )
    return regions


def _overlay(image: np.ndarray, dark_mask: np.ndarray, bright_mask: np.ndarray, mode: str) -> np.ndarray:
    result = image.copy()
    if mode in {"dark", "combined"}:
        result[dark_mask > 0] = (0.45 * result[dark_mask > 0] + 0.55 * np.array([30, 80, 255])).astype(np.uint8)
    if mode in {"bright", "combined"}:
        result[bright_mask > 0] = (0.45 * result[bright_mask > 0] + 0.55 * np.array([40, 230, 255])).astype(np.uint8)
    return result


def _category(regions: list[dict[str, Any]], mask: np.ndarray, fov_mask: np.ndarray) -> dict[str, Any]:
    fov_area = max(int(np.count_nonzero(fov_mask)), 1)
    fraction = _finite(float(np.count_nonzero(mask) / fov_area))
    return {"count": len(regions), "fraction": round(min(max(fraction, 0.0), 1.0), 6), "regions": regions}


def analyze_lesion_candidates(image: np.ndarray) -> dict[str, Any]:
    """Return experimental localized dark/bright image candidates, not lesion diagnoses."""
    height, width = _validate_image(image)
    working, scale_x, scale_y = _resize_for_working(image)
    fov_mask = _field_of_view_mask(working)
    dark_working, bright_working = _candidate_masks(working, fov_mask)
    dark_mask = cv2.resize(dark_working, (width, height), interpolation=cv2.INTER_NEAREST)
    bright_mask = cv2.resize(bright_working, (width, height), interpolation=cv2.INTER_NEAREST)
    fov_original = cv2.resize(fov_mask, (width, height), interpolation=cv2.INTER_NEAREST)
    dark_regions = _regions(dark_working, working, fov_mask, scale_x, scale_y)
    bright_regions = _regions(bright_working, working, fov_mask, scale_x, scale_y)

    return {
        "available": bool(np.any(fov_mask)),
        "method_status": "experimental_candidate_localization",
        "dark_candidates": _category(dark_regions, dark_working, fov_mask),
        "bright_candidates": _category(bright_regions, bright_working, fov_mask),
        "neovascularization": {"available": False, "reason": "No validated local neovascularization detector is available."},
        "optic_disc_exclusion": {"available": False, "reason": "No validated optic-disc detector is available; candidate regions are not disc-excluded."},
        "confidence_available": False,
        "limitations": [
            "Dark and bright regions are image-processing candidates, not confirmed microaneurysms, hemorrhages, or exudates.",
            "Illumination, vessels, lesions, borders, compression, and artifacts can create false candidates.",
            "No lesion probability, disease score, or clinical severity score is calculated.",
            "No quantitative lesion accuracy can be established because paired ground-truth lesion annotations are unavailable.",
        ],
        "_dark_mask": dark_mask,
        "_bright_mask": bright_mask,
        "_fov_mask": fov_original,
        "_dark_overlay": _overlay(image, dark_mask, bright_mask, "dark"),
        "_bright_overlay": _overlay(image, dark_mask, bright_mask, "bright"),
        "_combined_overlay": _overlay(image, dark_mask, bright_mask, "combined"),
    }

import cv2
import numpy as np
import pytest

from backend.lesions import analyze_lesion_candidates


def test_real_image_returns_bounded_candidate_evidence_and_overlays():
    image = cv2.imread("test_images/000c1434d8d7.png")
    result = analyze_lesion_candidates(image)

    assert result["method_status"] == "experimental_candidate_localization"
    assert result["confidence_available"] is False
    assert 0 <= result["dark_candidates"]["fraction"] <= 1
    assert 0 <= result["bright_candidates"]["fraction"] <= 1
    for category in ("dark_candidates", "bright_candidates"):
        assert result[category]["count"] >= 0
        for region in result[category]["regions"]:
            assert region["area"] > 0
            assert 0 <= region["x"] < image.shape[1]
            assert 0 <= region["y"] < image.shape[0]
            assert region["x"] + region["width"] <= image.shape[1]
            assert region["y"] + region["height"] <= image.shape[0]
            assert np.isfinite(list(region["centroid"].values())).all()
    assert result["_dark_overlay"].shape == image.shape
    assert result["_bright_overlay"].shape == image.shape
    assert result["_combined_overlay"].shape == image.shape


def test_candidate_analysis_is_deterministic():
    image = cv2.imread("test_images/000c1434d8d7.png")
    first = analyze_lesion_candidates(image)
    second = analyze_lesion_candidates(image)

    assert first["dark_candidates"] == second["dark_candidates"]
    assert first["bright_candidates"] == second["bright_candidates"]
    assert np.array_equal(first["_dark_overlay"], second["_dark_overlay"])


def test_dark_image_has_no_candidate_regions():
    result = analyze_lesion_candidates(np.zeros((480, 640, 3), dtype=np.uint8))

    assert result["available"] is False
    assert result["dark_candidates"]["count"] == 0
    assert result["bright_candidates"]["count"] == 0


def test_tiny_and_invalid_images_are_rejected():
    with pytest.raises(ValueError, match="too small"):
        analyze_lesion_candidates(np.zeros((8, 8, 3), dtype=np.uint8))
    with pytest.raises(ValueError, match="invalid"):
        analyze_lesion_candidates(None)


def test_non_color_image_is_rejected():
    with pytest.raises(ValueError, match="three color channels"):
        analyze_lesion_candidates(np.zeros((64, 64), dtype=np.uint8))

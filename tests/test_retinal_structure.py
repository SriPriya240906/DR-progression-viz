import cv2
import numpy as np
import pytest

from backend.structure import analyze_retinal_structure


def test_real_retinal_image_returns_bounded_experimental_structure():
    image = cv2.imread("test_images/000c1434d8d7.png")
    result = analyze_retinal_structure(image)

    assert result["available"] is True
    assert 0 <= result["field_of_view"]["fraction"] <= 1
    assert 0 <= result["vessels"]["vessel_like_fraction"] <= 1
    assert result["_mask"].shape == image.shape[:2]
    assert np.isfinite(result["_mask"]).all()
    assert result["optic_disc"]["available"] is False
    assert result["fovea"]["available"] is False


def test_structure_analysis_is_deterministic():
    image = cv2.imread("test_images/000c1434d8d7.png")
    first = analyze_retinal_structure(image)
    second = analyze_retinal_structure(image)

    assert first["field_of_view"] == second["field_of_view"]
    assert first["vessels"] == second["vessels"]
    assert np.array_equal(first["_mask"], second["_mask"])


def test_dark_image_has_no_sufficient_retinal_field():
    result = analyze_retinal_structure(np.zeros((480, 640, 3), dtype=np.uint8))

    assert result["field_of_view"]["fraction"] == 0
    assert result["field_of_view"]["sufficient_for_analysis"] is False
    assert result["vessels"]["available"] is False
    assert result["_visualization"] is None


def test_too_small_image_is_rejected():
    with pytest.raises(ValueError, match="too small"):
        analyze_retinal_structure(np.zeros((8, 8, 3), dtype=np.uint8))


def test_invalid_image_is_rejected():
    with pytest.raises(ValueError, match="invalid"):
        analyze_retinal_structure(None)

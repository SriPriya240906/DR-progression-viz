import cv2
import numpy as np

from backend.quality import analyze_image_quality


def retinal_like_image(width=640, height=480):
    image = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.ellipse(image, (width // 2, height // 2), (width // 3, height // 3), 0, 0, 360, (75, 115, 90), -1)
    cv2.circle(image, (width // 2, height // 2), max(4, width // 40), (220, 180, 150), -1)
    cv2.line(image, (width // 2, height // 2), (width // 4, height // 4), (150, 60, 55), 3)
    return image


def test_normal_retinal_like_image_returns_quality_metrics():
    result = analyze_image_quality(retinal_like_image())
    assert result["status"] in {"GOOD", "BORDERLINE", "POOR"}
    assert result["resolution"]["width"] == 640
    assert "variance_of_laplacian" == result["focus"]["metric"]


def test_blurred_image_warns_about_focus():
    result = analyze_image_quality(cv2.GaussianBlur(retinal_like_image(), (51, 51), 0))
    assert result["focus"]["value"] < 10
    assert any("Focus" in warning for warning in result["warnings"])


def test_dark_image_warns_about_illumination():
    result = analyze_image_quality(np.zeros((480, 640, 3), dtype=np.uint8))
    assert result["illumination"]["value"] == 0
    assert any("Illumination" in warning for warning in result["warnings"])


def test_overexposed_image_warns_about_illumination():
    result = analyze_image_quality(np.full((480, 640, 3), 255, dtype=np.uint8))
    assert result["illumination"]["bright_pixel_fraction"] == 1.0
    assert any("Illumination" in warning for warning in result["warnings"])


def test_low_contrast_image_warns_about_contrast():
    result = analyze_image_quality(np.full((480, 640, 3), 80, dtype=np.uint8))
    assert result["contrast"]["value"] == 0
    assert any("Contrast" in warning for warning in result["warnings"])


def test_low_resolution_image_reports_resolution():
    result = analyze_image_quality(retinal_like_image(64, 64))
    assert result["resolution"]["assessment"].startswith("Resolution is below")
    assert any("resolution" in warning.lower() for warning in result["warnings"])


def test_invalid_image_is_rejected():
    try:
        analyze_image_quality(None)
    except ValueError as error:
        assert "invalid" in str(error).lower()
    else:
        raise AssertionError("Expected invalid image to raise ValueError")
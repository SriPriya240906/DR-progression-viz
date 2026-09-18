import cv2
import numpy as np

from backend.enhancement import enhance_image
from backend.quality import analyze_image_quality


def textured_image(width=640, height=480):
    rng = np.random.default_rng(42)
    return rng.integers(45, 210, size=(height, width, 3), dtype=np.uint8)


def retinal_like_image(width=640, height=480):
    image = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.ellipse(image, (width // 2, height // 2), (width // 3, height // 3), 0, 0, 360, (75, 115, 90), -1)
    cv2.line(image, (width // 2, height // 2), (width // 4, height // 4), (150, 60, 55), 3)
    return image


def test_good_quality_image_does_not_trigger_enhancement():
    image = textured_image()
    quality = analyze_image_quality(image)
    assert quality["status"] == "GOOD"
    result = enhance_image(image, quality)
    assert result["attempted"] is False
    assert result["image"] is None


def test_borderline_or_poor_image_is_reassessed():
    image = retinal_like_image()
    quality = analyze_image_quality(image)
    result = enhance_image(image, quality)
    assert result["attempted"] is True
    assert result["enhanced_quality"] is not None
    assert result["image"].shape == image.shape
    assert "focus" in result["changes"]


def test_low_contrast_candidate_has_comparison_without_claiming_success():
    rng = np.random.default_rng(7)
    image = rng.integers(78, 83, size=(480, 640, 3), dtype=np.uint8)
    result = enhance_image(image, analyze_image_quality(image))
    assert result["attempted"] is True
    assert result["enhanced_quality"]["contrast"]["value"] >= 0
    assert isinstance(result["improved"], bool)


def test_dark_image_is_not_claimed_as_recoverable_without_structure():
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    result = enhance_image(image, analyze_image_quality(image))
    assert result["attempted"] is False
    assert "no measurable structure" in result["message"]


def test_overexposed_image_is_not_claimed_as_recoverable_without_structure():
    image = np.full((480, 640, 3), 255, dtype=np.uint8)
    result = enhance_image(image, analyze_image_quality(image))
    assert result["attempted"] is False
    assert result["original_quality"]["status"] == "POOR"


def test_uneven_illumination_is_reassessed_without_clinical_claim():
    gradient = np.linspace(0.35, 1.35, 640, dtype=np.float32)
    image = np.full((480, 640, 3), 110, dtype=np.float32) * gradient[None, :, None]
    image = np.clip(image, 0, 255).astype(np.uint8)
    result = enhance_image(image, analyze_image_quality(image))
    assert result["attempted"] is True
    assert result["enhanced_quality"] is not None
    assert isinstance(result["improved"], bool)


def test_low_resolution_image_is_not_given_a_useful_preview():
    image = np.full((32, 32, 3), 80, dtype=np.uint8)
    result = enhance_image(image, analyze_image_quality(image))
    assert result["attempted"] is False
    assert "too small" in result["message"]


def test_blurred_image_is_attempted_and_focus_is_reported():
    image = cv2.GaussianBlur(retinal_like_image(), (51, 51), 0)
    result = enhance_image(image, analyze_image_quality(image))
    assert result["attempted"] is True
    assert "focus" in result["changes"]
    assert result["enhanced_quality"]["focus"]["value"] >= 0


def test_invalid_image_is_rejected():
    try:
        enhance_image(None)
    except ValueError as error:
        assert "invalid" in str(error).lower()
    else:
        raise AssertionError("Expected invalid image to raise ValueError")
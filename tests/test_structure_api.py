import asyncio

import httpx

from backend.main import app


def request(path: str, filename: str, contents: bytes, content_type: str):
    async def run():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(path, files={"file": (filename, contents, content_type)})

    return asyncio.run(run())


def test_structure_endpoint_returns_overlay_and_unavailable_localizations():
    with open("test_images/000c1434d8d7.png", "rb") as handle:
        response = request("/api/structure/analyze", "retinal.png", handle.read(), "image/png")

    payload = response.json()["structure"]
    assert response.status_code == 200
    assert payload["overlay_image_url"]
    assert payload["vessels"]["confidence_available"] is False
    assert payload["optic_disc"]["available"] is False
    assert payload["fovea"]["available"] is False


def test_structure_endpoint_rejects_unsupported_upload():
    response = request("/api/structure/analyze", "not-an-image.txt", b"not an image", "text/plain")
    assert response.status_code == 415


def test_structure_endpoint_rejects_corrupt_image():
    response = request("/api/structure/analyze", "broken.png", b"not an image", "image/png")
    assert response.status_code == 400


def test_full_analysis_contains_additive_structure_without_losing_outputs():
    with open("test_images/000c1434d8d7.png", "rb") as handle:
        response = request("/api/analyze", "retinal.png", handle.read(), "image/png")

    payload = response.json()
    assert response.status_code == 200
    assert payload["structure"]["vessels"]["available"] is True
    assert payload["quality"]
    assert payload["enhancement"]
    assert payload["prediction"]
    assert payload["reliability"]
    assert "gradcam" in payload
    assert "similar_cases" in payload
    assert "progression_map" in payload
    assert "progression_simulation" in payload
    assert payload["errors"] == []

import asyncio

import httpx

from backend.main import app


def request(path: str, filename: str, contents: bytes, content_type: str):
    async def run():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(path, files={"file": (filename, contents, content_type)})

    return asyncio.run(run())


def test_lesion_endpoint_returns_candidate_overlays():
    with open("test_images/000c1434d8d7.png", "rb") as handle:
        response = request("/api/lesions/analyze", "retinal.png", handle.read(), "image/png")

    payload = response.json()["lesion_evidence"]
    assert response.status_code == 200
    assert payload["method_status"] == "experimental_candidate_localization"
    assert set(payload["overlay_image_urls"]) == {"dark", "bright", "combined"}
    assert payload["optic_disc_exclusion"]["available"] is False
    assert payload["neovascularization"]["available"] is False


def test_lesion_endpoint_rejects_unsupported_and_corrupt_uploads():
    assert request("/api/lesions/analyze", "bad.txt", b"bad", "text/plain").status_code == 415
    assert request("/api/lesions/analyze", "bad.png", b"bad", "image/png").status_code == 400


def test_full_analysis_contains_additive_lesion_evidence():
    with open("test_images/000c1434d8d7.png", "rb") as handle:
        response = request("/api/analyze", "retinal.png", handle.read(), "image/png")

    payload = response.json()
    assert response.status_code == 200
    assert payload["lesion_evidence"]["dark_candidates"]["count"] >= 0
    assert payload["quality"]
    assert payload["enhancement"]
    assert payload["prediction"]
    assert payload["reliability"]
    assert payload["structure"]
    assert "gradcam" in payload
    assert "similar_cases" in payload
    assert "progression_map" in payload
    assert "progression_simulation" in payload
    assert payload["errors"] == []

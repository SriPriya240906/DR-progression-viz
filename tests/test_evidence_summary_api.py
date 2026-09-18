import asyncio

import httpx

from backend.main import app


def request_json(payload):
    async def run():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post("/api/evidence/summary", json=payload)

    return asyncio.run(run())


def request_image():
    async def run():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            with open("test_images/000c1434d8d7.png", "rb") as handle:
                return await client.post(
                    "/api/evidence/summary",
                    files={"file": ("retinal.png", handle.read(), "image/png")},
                )

    return asyncio.run(run())


def request_upload(contents: bytes, content_type: str):
    async def run():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(
                "/api/evidence/summary",
                files={"file": ("upload.bin", contents, content_type)},
            )

    return asyncio.run(run())


def test_json_evidence_summary_preserves_prediction_and_requires_review():
    response = request_json({"prediction": {"grade": 2, "label": "Moderate", "confidence": 100.0}})
    payload = response.json()["evidence_summary"]

    assert response.status_code == 200
    assert payload["prediction"]["grade"] == 2
    assert payload["clinical_review"]["required"] is True
    assert "score" not in payload


def test_image_evidence_summary_returns_actual_existing_signals():
    response = request_image()
    payload = response.json()["evidence_summary"]

    assert response.status_code == 200
    assert payload["prediction"]["grade"] == 2
    assert payload["image_quality"]["available"] is True
    assert payload["model_explanation"]["gradcam_available"] is True
    assert payload["retinal_structure"]["available"] is True
    assert payload["lesion_evidence"]["available"] is True
    assert payload["clinical_review"]["required"] is True


def test_evidence_summary_rejects_unsupported_and_corrupt_uploads():
    assert request_upload(b"not an image", "text/plain").status_code == 415
    assert request_upload(b"not an image", "image/png").status_code == 400

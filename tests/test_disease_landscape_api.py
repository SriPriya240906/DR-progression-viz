import asyncio

import httpx

from backend.main import app


def get_landscape():
    async def run():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/api/disease-landscape")

    return asyncio.run(run())


def analyze_image():
    async def run():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            with open("test_images/000c1434d8d7.png", "rb") as handle:
                return await client.post(
                    "/api/analyze",
                    files={"file": ("retinal.png", handle.read(), "image/png")},
                )

    return asyncio.run(run())


def test_landscape_endpoint_returns_capability_map():
    response = get_landscape()
    landscape = response.json()["disease_landscape"]

    assert response.status_code == 200
    assert landscape["landscape_type"] == "capability_map"
    assert any(item["name"] == "Diabetic Retinopathy" and item["status"] == "supported" for item in landscape["diseases"])
    assert not any("probability" in key.lower() or "score" in key.lower() for key in landscape)


def test_full_analysis_adds_landscape_without_changing_prediction():
    response = analyze_image()
    payload = response.json()

    assert response.status_code == 200
    assert payload["prediction"]["grade"] == 2
    assert payload["prediction"]["confidence"] == 100.0
    assert payload["disease_landscape"]["available"] is True
    assert payload["quality"]
    assert payload["enhancement"]
    assert payload["reliability"]
    assert payload["structure"]
    assert payload["lesion_evidence"]
    assert payload["evidence_summary"]
    assert payload["errors"] == []

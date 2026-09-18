import asyncio

import httpx

from backend.main import app


def request(path: str, filename: str, contents: bytes, content_type: str):
    async def run():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(path, files={"file": (filename, contents, content_type)})

    return asyncio.run(run())


def test_reliability_endpoint_returns_uncertainty_metrics():
    with open("test_images/000c1434d8d7.png", "rb") as handle:
        response = request("/api/reliability/analyze", "retinal.png", handle.read(), "image/png")

    payload = response.json()
    reliability = payload["reliability"]
    assert response.status_code == 200
    assert payload["prediction"]["grade"] == reliability["predicted_index"]
    assert reliability["top_probability"] >= reliability["second_probability"]
    assert reliability["predictive_entropy"] >= 0
    assert reliability["calibration"]["available"] is False


def test_reliability_endpoint_rejects_unsupported_upload():
    response = request("/api/reliability/analyze", "not-an-image.txt", b"not an image", "text/plain")
    assert response.status_code == 415

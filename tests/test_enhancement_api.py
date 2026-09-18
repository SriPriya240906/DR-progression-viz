import asyncio

import httpx

from backend.main import app


def request_quality_enhancement(filename: str, contents: bytes, content_type: str):
    async def run():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(
                "/api/quality/enhance",
                files={"file": (filename, contents, content_type)},
            )

    return asyncio.run(run())


def test_enhancement_endpoint_returns_comparison_for_retinal_image():
    with open("test_images/000c1434d8d7.png", "rb") as handle:
        response = request_quality_enhancement("retinal.png", handle.read(), "image/png")

    payload = response.json()["enhancement"]
    assert response.status_code == 200
    assert payload["attempted"] is True
    assert payload["original_quality"]
    assert payload["enhanced_quality"]
    assert payload["original_image_url"]
    assert payload["enhanced_image_url"]


def test_enhancement_endpoint_rejects_unsupported_upload():
    response = request_quality_enhancement("not-an-image.txt", b"not an image", "text/plain")
    assert response.status_code == 415
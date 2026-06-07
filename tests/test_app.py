import asyncio

import httpx

from app.main import app


async def get(path: str) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.get(path)


def test_home_page_renders_scaffold() -> None:
    response = asyncio.run(get("/"))

    assert response.status_code == 200
    assert "SQL Gym" in response.text
    assert "Phase 0 scaffold" in response.text
    assert "Product features are intentionally deferred" in response.text


def test_health_endpoint_reports_ok() -> None:
    response = asyncio.run(get("/health"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_static_stylesheet_is_served() -> None:
    response = asyncio.run(get("/static/styles.css"))

    assert response.status_code == 200
    assert ".page-shell" in response.text

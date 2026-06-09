import asyncio

import httpx

from app.main import app


async def _get(path: str, *, cookies: dict[str, str] | None = None) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
        cookies=cookies or {},
    ) as client:
        return await client.get(path)


async def _post(
    path: str,
    data: dict[str, str],
    *,
    cookies: dict[str, str] | None = None,
    follow_redirects: bool = False,
) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
        cookies=cookies or {},
        follow_redirects=follow_redirects,
    ) as client:
        return await client.post(path, data=data)


def test_interview_start_page_renders() -> None:
    response = asyncio.run(_get("/practice/interview/start"))
    assert response.status_code == 200
    assert "Start an interview session" in response.text
    assert "Start interview session" in response.text
    assert "Unlimited" in response.text


def test_interview_start_post_creates_session_and_redirects() -> None:
    response = asyncio.run(
        _post(
            "/practice/interview/start",
            {"queue_length": "3", "difficulty": ""},
            follow_redirects=False,
        )
    )
    assert response.status_code == 303
    location = response.headers["location"]
    assert location.startswith("/practice/interview/times-archive/times-archive-")

    assert location.endswith("times-archive-001")

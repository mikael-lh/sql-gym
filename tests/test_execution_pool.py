from unittest.mock import MagicMock, patch

from app.execution.pool import close_pool, get_pool, open_pool


def test_open_pool_returns_none_without_database_url() -> None:
    close_pool()
    with patch("app.execution.pool.get_database_url", return_value=None):
        assert open_pool() is None
        assert get_pool() is None


def test_open_pool_creates_shared_pool() -> None:
    close_pool()
    fake_pool = MagicMock()
    with (
        patch("app.execution.pool.get_database_url", return_value="postgresql://example"),
        patch("app.execution.pool.ConnectionPool", return_value=fake_pool) as mock_pool_cls,
    ):
        first = open_pool()
        second = open_pool()
    assert first is fake_pool
    assert second is fake_pool
    mock_pool_cls.assert_called_once()
    close_pool()
    assert get_pool() is None


def test_create_app_lifespan_opens_and_closes_pool() -> None:
    import asyncio

    from app.main import create_app

    close_pool()

    async def _run() -> None:
        with (
            patch("app.main.open_pool") as mock_open,
            patch("app.main.close_pool") as mock_close,
        ):
            app = create_app()
            async with app.router.lifespan_context(app):
                mock_open.assert_called_once()
            mock_close.assert_called_once()

    asyncio.run(_run())

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.api.routes import router as practice_api_router
from app.db.settings import get_session_secret
from app.execution.pool import close_pool, open_pool
from app.practice import get_not_found_context, lookup_dataset, lookup_exercise
from app.workspace.context import (
    get_default_workspace_redirect_url,
    get_workspace_context,
    parse_workspace_filters,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = PROJECT_ROOT / "templates"
STATIC_DIR = PROJECT_ROOT / "static"

templates = Jinja2Templates(directory=TEMPLATES_DIR)


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    open_pool()
    try:
        yield
    finally:
        close_pool()


def render_not_found(request: Request, *, resource_label: str = "exercise") -> Response:
    return templates.TemplateResponse(
        request,
        "404.html",
        get_not_found_context(resource_label) | {"request": request},
        status_code=404,
    )


def create_app() -> FastAPI:
    # Resolve at startup so production without SESSION_SECRET fails fast.
    session_secret = get_session_secret()
    app = FastAPI(
        title="SQL Gym",
        summary="A lightweight gym for practicing SQL on curated datasets.",
        lifespan=_lifespan,
    )
    app.add_middleware(SessionMiddleware, secret_key=session_secret)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.include_router(practice_api_router)

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon() -> FileResponse:
        return FileResponse(STATIC_DIR / "favicon.svg", media_type="image/svg+xml")

    @app.get("/", tags=["pages"])
    def index() -> RedirectResponse:
        return RedirectResponse(url="/practice", status_code=303)

    @app.get("/practice", tags=["pages"])
    def practice(
        request: Request,
        difficulty: str | None = None,
    ) -> Response:
        filters = parse_workspace_filters(difficulty=difficulty)
        redirect_url = get_default_workspace_redirect_url(request, filters)
        if redirect_url is None:
            return render_not_found(request)
        return RedirectResponse(url=redirect_url, status_code=303)

    @app.get("/practice/interview/{path:path}", tags=["pages"])
    def interview_legacy_redirect() -> RedirectResponse:
        return RedirectResponse(url="/practice", status_code=303)

    @app.get("/practice/{dataset_id}/{exercise_id}", response_class=HTMLResponse, tags=["pages"])
    def practice_exercise(
        request: Request,
        dataset_id: str,
        exercise_id: str,
        difficulty: str | None = None,
    ) -> Response:
        filters = parse_workspace_filters(difficulty=difficulty)
        context = get_workspace_context(request, dataset_id, exercise_id, filters)
        if context is not None:
            template_context: dict[str, Any] = context.as_template_context()
            template_context["request"] = request
            return templates.TemplateResponse(
                request,
                "workspace.html",
                template_context,
            )
        if lookup_dataset(dataset_id) is None or lookup_exercise(dataset_id, exercise_id) is None:
            return render_not_found(request)
        redirect_url = get_default_workspace_redirect_url(request, filters)
        if redirect_url is None:
            return render_not_found(request)
        return RedirectResponse(url=redirect_url, status_code=303)

    return app


app = create_app()


def main() -> None:
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000)

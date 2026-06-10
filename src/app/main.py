import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.api.practice import (
    RunRequest,
    SubmitRequest,
    api_clear_progress,
    api_get_exercise,
    api_list_exercises,
    api_run_sql,
    api_submit_sql,
)
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


def _session_secret() -> str:
    return os.environ.get("SESSION_SECRET", "dev-only-session-secret-change-me")


def create_app() -> FastAPI:
    app = FastAPI(
        title="SQL Gym",
        summary="A lightweight gym for practicing SQL on curated datasets.",
    )
    app.add_middleware(SessionMiddleware, secret_key=_session_secret())
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/practice/exercises", tags=["api"])
    def practice_api_list_exercises(
        request: Request,
        dataset: str | None = None,
        difficulty: str | None = None,
        mode: str | None = None,
    ) -> dict[str, object]:
        return api_list_exercises(request, dataset=dataset, difficulty=difficulty, mode=mode)

    @app.get("/api/practice/{dataset_id}/{exercise_id}", tags=["api"])
    def practice_api_get_exercise(
        request: Request,
        dataset_id: str,
        exercise_id: str,
        difficulty: str | None = None,
        mode: str | None = None,
    ) -> dict[str, object]:
        return api_get_exercise(
            request,
            dataset_id,
            exercise_id,
            difficulty=difficulty,
            mode=mode,
        )

    @app.post("/api/practice/{dataset_id}/{exercise_id}/run", tags=["api"])
    def practice_api_run(
        request: Request,
        dataset_id: str,
        exercise_id: str,
        body: RunRequest,
    ) -> Response:
        return api_run_sql(request, dataset_id, exercise_id, body)

    @app.post("/api/practice/{dataset_id}/{exercise_id}/submit", tags=["api"])
    def practice_api_submit(
        request: Request,
        dataset_id: str,
        exercise_id: str,
        body: SubmitRequest,
    ) -> Response:
        return api_submit_sql(request, dataset_id, exercise_id, body)

    @app.post("/api/practice/progress/clear", tags=["api"])
    def practice_api_clear_progress() -> Response:
        return api_clear_progress()

    @app.get("/", tags=["pages"])
    def index() -> RedirectResponse:
        return RedirectResponse(url="/practice", status_code=303)

    @app.get("/practice", tags=["pages"])
    def practice(
        request: Request,
        difficulty: str | None = None,
        mode: str | None = None,
    ) -> Response:
        filters = parse_workspace_filters(difficulty=difficulty, mode=mode)
        redirect_url = get_default_workspace_redirect_url(request, filters)
        if redirect_url is None:
            return templates.TemplateResponse(
                request,
                "404.html",
                get_not_found_context("exercise") | {"request": request},
                status_code=404,
            )
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
        mode: str | None = None,
    ) -> Response:
        filters = parse_workspace_filters(difficulty=difficulty, mode=mode)
        context = get_workspace_context(request, dataset_id, exercise_id, filters)
        if context is not None:
            return templates.TemplateResponse(
                request,
                "workspace.html",
                context | {"request": request},
            )
        if lookup_dataset(dataset_id) is None or lookup_exercise(dataset_id, exercise_id) is None:
            return templates.TemplateResponse(
                request,
                "404.html",
                get_not_found_context("exercise") | {"request": request},
                status_code=404,
            )
        redirect_url = get_default_workspace_redirect_url(request, filters)
        if redirect_url is None:
            return templates.TemplateResponse(
                request,
                "404.html",
                get_not_found_context("exercise") | {"request": request},
                status_code=404,
            )
        return RedirectResponse(url=redirect_url, status_code=303)

    return app


app = create_app()


def main() -> None:
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000)

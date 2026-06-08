import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.execution import execute_query
from app.practice import (
    get_exercise_preview_context,
    get_not_found_context,
    get_practice_context,
    lookup_exercise,
)
from app.practice_session import store_run_result, store_submit_result

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = PROJECT_ROOT / "templates"
STATIC_DIR = PROJECT_ROOT / "static"

templates = Jinja2Templates(directory=TEMPLATES_DIR)

CORE_LOOP = [
    "Pick a dataset",
    "Pick a difficulty",
    "Choose timed or untimed practice",
    "Complete a SQL exercise",
    "Review grading feedback",
    "Move to the next exercise",
]

PLACEHOLDERS = [
    {
        "title": "Accounts and durable progress",
        "description": "Learner attempts stay in the browser session only; no sign-in or saved history.",
    },
    {
        "title": "AI grading and explanations",
        "description": "Strict grid-match grading is live; AI feedback and partial credit are not.",
    },
    {
        "title": "Timed-mode scoring",
        "description": "Timed exercises are labeled in the catalog but interview timers are not active.",
    },
    {
        "title": "Standalone catalog route",
        "description": "Catalog browsing remains integrated into `/practice` only.",
    },
]


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

    @app.get("/", response_class=HTMLResponse, tags=["pages"])
    def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "page_title": "SQL Gym",
                "status_label": "Phase 2 practice",
                "positioning": (
                    "Browse 50 Times Archive SQL exercises, run PostgreSQL against imported "
                    "article data, and get strict pass/fail grading on exercise previews."
                ),
                "core_loop": CORE_LOOP,
                "placeholders": PLACEHOLDERS,
            },
        )

    @app.get("/practice", response_class=HTMLResponse, tags=["pages"])
    def practice(
        request: Request,
        dataset: str | None = None,
        difficulty: str | None = None,
        mode: str | None = None,
    ) -> HTMLResponse:
        return templates.TemplateResponse(
            request,
            "practice.html",
            get_practice_context(dataset_id=dataset, difficulty=difficulty, mode=mode)
            | {"request": request},
        )

    def _exercise_path(dataset_id: str, exercise_id: str) -> str:
        return f"/practice/{dataset_id}/{exercise_id}"

    @app.get("/practice/{dataset_id}/{exercise_id}", response_class=HTMLResponse, tags=["pages"])
    def practice_exercise(
        request: Request,
        dataset_id: str,
        exercise_id: str,
    ) -> HTMLResponse:
        context = get_exercise_preview_context(request, dataset_id, exercise_id)
        if context is None:
            return templates.TemplateResponse(
                request,
                "404.html",
                get_not_found_context("exercise") | {"request": request},
                status_code=404,
            )
        return templates.TemplateResponse(
            request,
            "practice_exercise.html",
            context | {"request": request},
        )

    @app.post(
        "/practice/{dataset_id}/{exercise_id}/run",
        tags=["pages"],
    )
    def practice_run_sql(
        request: Request,
        dataset_id: str,
        exercise_id: str,
        sql: str = Form(...),
    ) -> Response:
        exercise = lookup_exercise(dataset_id, exercise_id)
        if exercise is None:
            raise HTTPException(status_code=404)

        outcome = execute_query(sql)
        store_run_result(request, exercise.id, sql, outcome)
        return RedirectResponse(
            url=_exercise_path(dataset_id, exercise_id),
            status_code=303,
        )

    @app.post(
        "/practice/{dataset_id}/{exercise_id}/submit",
        tags=["pages"],
    )
    def practice_submit_sql(
        request: Request,
        dataset_id: str,
        exercise_id: str,
        sql: str = Form(...),
    ) -> Response:
        exercise = lookup_exercise(dataset_id, exercise_id)
        if exercise is None:
            raise HTTPException(status_code=404)

        outcome = execute_query(sql)
        store_submit_result(request, exercise, sql, outcome)
        return RedirectResponse(
            url=_exercise_path(dataset_id, exercise_id),
            status_code=303,
        )

    return app


app = create_app()


def main() -> None:
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000)

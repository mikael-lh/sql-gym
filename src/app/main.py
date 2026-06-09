import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.domain.progress import ProgressStore
from app.execution import execute_query
from app.interview.session import (
    create_interview_session,
    current_exercise_url,
    save_interview_session,
)
from app.interview.views import (
    get_interview_start_context,
    parse_interview_start_form,
)
from app.practice import (
    get_exercise_preview_context,
    get_home_context,
    get_not_found_context,
    get_practice_context,
    lookup_exercise,
)
from app.practice_session import store_run_result, store_submit_result
from app.progress import attach_progress_cookie, clear_progress_cookie, load_progress

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
        "title": "Accounts and cross-device sync",
        "description": (
            "Progress is saved in a browser cookie for 60 days on this device. "
            "Sign-in and sync across devices are not available."
        ),
    },
    {
        "title": "AI grading and explanations",
        "description": "Strict grid-match grading is live; AI feedback and partial credit are not.",
    },
    {
        "title": "Standalone catalog route",
        "description": "Catalog browsing remains integrated into `/practice` only.",
    },
]


def _session_secret() -> str:
    return os.environ.get("SESSION_SECRET", "dev-only-session-secret-change-me")


def _redirect_with_progress(url: str, progress: ProgressStore) -> RedirectResponse:
    response = RedirectResponse(url=url, status_code=303)
    attach_progress_cookie(response, progress)
    return response


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
                "status_label": "Phase 3 practice",
                "positioning": (
                    "Browse 50 Times Archive SQL exercises, run PostgreSQL against imported "
                    "article data, track progress in your browser, and practice timed interview "
                    "exercises with strict pass/fail grading."
                ),
                "core_loop": CORE_LOOP,
                "placeholders": PLACEHOLDERS,
                **get_home_context(request),
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
            get_practice_context(
                request,
                dataset_id=dataset,
                difficulty=difficulty,
                mode=mode,
            ),
        )

    def _exercise_path(dataset_id: str, exercise_id: str) -> str:
        return f"/practice/{dataset_id}/{exercise_id}"

    def _interview_exercise_path(dataset_id: str, exercise_id: str) -> str:
        return f"/practice/interview/{dataset_id}/{exercise_id}"

    @app.get("/practice/interview/start", response_class=HTMLResponse, tags=["pages"])
    def interview_start_get(
        request: Request,
        difficulty: str | None = None,
        queue_length: str | None = None,
    ) -> HTMLResponse:
        return templates.TemplateResponse(
            request,
            "interview_start.html",
            get_interview_start_context(
                request,
                difficulty=difficulty,
                queue_length=queue_length,
            )
            | {"request": request},
        )

    @app.post("/practice/interview/start", tags=["pages"])
    def interview_start_post(
        request: Request,
        queue_length: str = Form(...),
        difficulty: str = Form(default=""),
    ) -> Response:
        parsed = parse_interview_start_form(
            queue_length=queue_length,
            difficulty=difficulty or None,
        )
        if parsed is None:
            return RedirectResponse(url="/practice/interview/start", status_code=303)
        requested_length, parsed_difficulty = parsed
        session = create_interview_session(
            requested_length=requested_length,
            difficulty=parsed_difficulty,
        )
        if session is None:
            return RedirectResponse(url="/practice/interview/start", status_code=303)
        save_interview_session(request, session)
        first_url = current_exercise_url(session)
        if first_url is None:
            return RedirectResponse(url="/practice/interview/start", status_code=303)
        return RedirectResponse(url=first_url, status_code=303)

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

    @app.post("/practice/progress/clear", tags=["pages"])
    def practice_clear_progress() -> Response:
        response = RedirectResponse(url="/practice", status_code=303)
        clear_progress_cookie(response)
        attach_progress_cookie(response, ProgressStore())
        return response

    @app.post(
        "/practice/{dataset_id}/{exercise_id}/submit",
        tags=["pages"],
    )
    def practice_submit_sql(
        request: Request,
        dataset_id: str,
        exercise_id: str,
        sql: str = Form(...),
        elapsed_seconds: int | None = Form(default=None),
    ) -> Response:
        exercise = lookup_exercise(dataset_id, exercise_id)
        if exercise is None:
            raise HTTPException(status_code=404)

        outcome = execute_query(sql)
        grading = store_submit_result(request, exercise, sql, outcome)
        if grading is None:
            return RedirectResponse(
                url=_exercise_path(dataset_id, exercise_id),
                status_code=303,
            )

        progress = load_progress(request)
        elapsed: int | None = None
        if elapsed_seconds is not None and exercise.mode == "Timed":
            max_seconds = exercise.estimated_time_minutes * 60
            if 0 < elapsed_seconds <= max_seconds:
                elapsed = elapsed_seconds
        progress = progress.apply_submit_outcome(
            exercise.id,
            passed=grading.passed is True,
            elapsed_seconds=elapsed,
        )
        return _redirect_with_progress(_exercise_path(dataset_id, exercise_id), progress)

    return app


app = create_app()


def main() -> None:
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000)

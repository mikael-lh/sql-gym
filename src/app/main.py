import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Form, HTTPException, Request
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
from app.domain.exercises import Exercise
from app.domain.progress import ProgressStore
from app.execution import execute_query
from app.interview.session import (
    advance,
    clear_interview_session,
    create_interview_session,
    current_exercise_url,
    end_session_early,
    load_interview_session,
    record_outcome,
    save_interview_session,
)
from app.interview.views import (
    get_interview_exercise_context,
    get_interview_start_context,
    get_interview_summary_context,
    parse_interview_start_form,
)
from app.practice import get_not_found_context, lookup_dataset, lookup_exercise
from app.practice_session import slim_practice_attempts, store_run_result, store_submit_result
from app.progress import attach_progress_cookie, clear_progress_cookie, load_progress
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


def _redirect_with_progress(url: str, progress: ProgressStore) -> RedirectResponse:
    response = RedirectResponse(url=url, status_code=303)
    attach_progress_cookie(response, progress)
    return response


def _parse_elapsed_seconds(exercise: Exercise, elapsed_seconds: int | None) -> int | None:
    if elapsed_seconds is not None and exercise.mode == "Timed":
        max_seconds = exercise.estimated_time_minutes * 60
        if 0 < elapsed_seconds <= max_seconds:
            return elapsed_seconds
    return None


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
        slim_practice_attempts(request)
        save_interview_session(request, session)
        first_url = current_exercise_url(session)
        if first_url is None:
            return RedirectResponse(url="/practice/interview/start", status_code=303)
        return RedirectResponse(url=first_url, status_code=303)

    def _interview_guard_redirect(
        request: Request,
        exercise_id: str,
    ) -> RedirectResponse | None:
        session = load_interview_session(request)
        if session is None or not session.is_active:
            return RedirectResponse(url="/practice/interview/start", status_code=303)
        current_id = session.current_exercise_id()
        if current_id != exercise_id:
            resume_url = current_exercise_url(session)
            return RedirectResponse(
                url=resume_url or "/practice/interview/start",
                status_code=303,
            )
        return None

    @app.get(
        "/practice/interview/{dataset_id}/{exercise_id}",
        response_class=HTMLResponse,
        tags=["pages"],
    )
    def interview_exercise_get(
        request: Request,
        dataset_id: str,
        exercise_id: str,
    ) -> Response:
        guard = _interview_guard_redirect(request, exercise_id)
        if guard is not None:
            return guard
        context = get_interview_exercise_context(request, dataset_id, exercise_id)
        if context is None:
            return templates.TemplateResponse(
                request,
                "404.html",
                get_not_found_context("exercise") | {"request": request},
                status_code=404,
            )
        return templates.TemplateResponse(
            request,
            "interview_exercise.html",
            context | {"request": request},
        )

    @app.post("/practice/interview/{dataset_id}/{exercise_id}/run", tags=["pages"])
    def interview_run_sql(
        request: Request,
        dataset_id: str,
        exercise_id: str,
        sql: str = Form(...),
    ) -> Response:
        guard = _interview_guard_redirect(request, exercise_id)
        if guard is not None:
            return guard
        exercise = lookup_exercise(dataset_id, exercise_id)
        if exercise is None:
            raise HTTPException(status_code=404)
        outcome = execute_query(sql)
        store_run_result(request, exercise.id, sql, outcome)
        return RedirectResponse(
            url=_interview_exercise_path(dataset_id, exercise_id),
            status_code=303,
        )

    @app.post("/practice/interview/{dataset_id}/{exercise_id}/submit", tags=["pages"])
    def interview_submit_sql(
        request: Request,
        dataset_id: str,
        exercise_id: str,
        sql: str = Form(...),
        elapsed_seconds: int | None = Form(default=None),
    ) -> Response:
        guard = _interview_guard_redirect(request, exercise_id)
        if guard is not None:
            return guard
        exercise = lookup_exercise(dataset_id, exercise_id)
        if exercise is None:
            raise HTTPException(status_code=404)
        outcome = execute_query(sql)
        grading = store_submit_result(request, exercise, sql, outcome)
        redirect_url = _interview_exercise_path(dataset_id, exercise_id)
        if grading is None:
            return RedirectResponse(url=redirect_url, status_code=303)
        elapsed = _parse_elapsed_seconds(exercise, elapsed_seconds)
        progress = load_progress(request).apply_submit_outcome(
            exercise.id,
            passed=grading.passed is True,
            elapsed_seconds=elapsed,
        )
        record_outcome(
            request,
            exercise.id,
            passed=grading.passed is True,
            elapsed_seconds=elapsed,
        )
        return _redirect_with_progress(redirect_url, progress)

    @app.post("/practice/interview/next", tags=["pages"])
    def interview_next(request: Request) -> Response:
        session = load_interview_session(request)
        if session is None or not session.is_active:
            return RedirectResponse(url="/practice/interview/start", status_code=303)
        if not session.has_outcome_for_current():
            resume_url = current_exercise_url(session)
            return RedirectResponse(
                url=resume_url or "/practice/interview/start",
                status_code=303,
            )
        advanced = advance(session)
        save_interview_session(request, advanced)
        if advanced.status in {"completed", "ended_early"}:
            return RedirectResponse(url="/practice/interview/summary", status_code=303)
        next_url = current_exercise_url(advanced)
        return RedirectResponse(
            url=next_url or "/practice/interview/summary",
            status_code=303,
        )

    @app.post("/practice/interview/end", tags=["pages"])
    def interview_end(request: Request) -> Response:
        session = load_interview_session(request)
        if session is None or not session.is_active:
            return RedirectResponse(url="/practice/interview/start", status_code=303)
        ended = end_session_early(session)
        save_interview_session(request, ended)
        return RedirectResponse(url="/practice/interview/summary", status_code=303)

    @app.get("/practice/interview/summary", response_class=HTMLResponse, tags=["pages"])
    def interview_summary(request: Request) -> Response:
        session = load_interview_session(request)
        if session is None:
            return RedirectResponse(url="/practice/interview/start", status_code=303)
        if session.is_active:
            resume_url = current_exercise_url(session)
            return RedirectResponse(
                url=resume_url or "/practice/interview/start",
                status_code=303,
            )
        context = get_interview_summary_context(request)
        clear_interview_session(request)
        if context is None:
            return RedirectResponse(url="/practice/interview/start", status_code=303)
        return templates.TemplateResponse(
            request,
            "interview_summary.html",
            context | {"request": request},
        )

    @app.post("/practice/interview/abandon", tags=["pages"])
    def interview_abandon(request: Request) -> Response:
        clear_interview_session(request)
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

        elapsed = _parse_elapsed_seconds(exercise, elapsed_seconds)
        progress = load_progress(request).apply_submit_outcome(
            exercise.id,
            passed=grading.passed is True,
            elapsed_seconds=elapsed,
        )
        return _redirect_with_progress(_exercise_path(dataset_id, exercise_id), progress)

    return app


app = create_app()


def main() -> None:
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000)

from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.practice import get_exercise_preview_context, get_not_found_context, get_practice_context

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
        "title": "Dataset selection",
        "description": "Times Archive demo samples are available on the practice placeholder page.",
    },
    {
        "title": "Difficulty selection",
        "description": (
            "Beginner, intermediate, and advanced paths are reserved for future exercises."
        ),
    },
    {
        "title": "Practice mode",
        "description": "Timed and untimed practice options are visible here but not active yet.",
    },
    {
        "title": "SQL editor",
        "description": (
            "The editor is reserved for a future implementation; queries do not run yet."
        ),
    },
    {
        "title": "Grading feedback",
        "description": "Exact-result and AI-assisted grading remain future work.",
    },
    {
        "title": "Progress tracking",
        "description": (
            "Completion history and skill progress will stay demo-only until persistence is "
            "approved."
        ),
    },
]


def create_app() -> FastAPI:
    app = FastAPI(
        title="SQL Gym",
        summary="A lightweight gym for practicing SQL on curated datasets.",
    )
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
                "status_label": "Phase 0 app shell",
                "positioning": (
                    "Practice realistic SQL questions on curated datasets, then build toward "
                    "faster, clearer answers."
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

    @app.get("/practice/{dataset_id}/{exercise_id}", response_class=HTMLResponse, tags=["pages"])
    def practice_exercise(
        request: Request,
        dataset_id: str,
        exercise_id: str,
    ) -> HTMLResponse:
        context = get_exercise_preview_context(dataset_id, exercise_id)
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

    return app


app = create_app()


def main() -> None:
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000)

from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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
        "description": "Times dataset samples arrive in a later Phase 0 milestone.",
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

    return app


app = create_app()


def main() -> None:
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000)

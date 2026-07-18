"""Practice API route registration."""

from fastapi import APIRouter

from app.api.practice import (
    api_clear_progress,
    api_get_exercise,
    api_list_exercises,
    api_run_sql,
    api_submit_sql,
)

router = APIRouter(prefix="/api/practice", tags=["api"])
router.add_api_route("/exercises", api_list_exercises, methods=["GET"])
router.add_api_route("/progress/clear", api_clear_progress, methods=["POST"])
router.add_api_route("/{dataset_id}/{exercise_id}", api_get_exercise, methods=["GET"])
router.add_api_route("/{dataset_id}/{exercise_id}/run", api_run_sql, methods=["POST"])
router.add_api_route(
    "/{dataset_id}/{exercise_id}/submit",
    api_submit_sql,
    methods=["POST"],
)

import json
from pathlib import Path


def test_date_exercises_reference_1920_in_prompt_and_sample() -> None:
    exercises = json.loads(
        Path("src/app/catalog/data/times_exercises.json").read_text()
    )
    by_id = {exercise["id"]: exercise for exercise in exercises}
    january = by_id["times-archive-011"]
    window = by_id["times-archive-014"]
    assert "1920" in january["prompt"]
    assert "1920" in january["sample_sql"]
    assert "2024" not in january["prompt"]
    assert "2024" not in january["sample_sql"]
    assert "1920" in window["prompt"]
    assert "1920" in window["sample_sql"]
    assert "2024" not in window["sample_sql"]

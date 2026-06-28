#!/usr/bin/env python3
# ruff: noqa: E501
"""Remove Beginner exercises, drop mode metadata, and append 30 Advanced exercises."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXERCISES_PATH = ROOT / "src/app/catalog/data/times_exercises.json"
GRIDS_DIR = ROOT / "src/app/catalog/data/expected_grids"

BEGINNER_IDS = {
    "times-archive-001",
    "times-archive-002",
    "times-archive-003",
    "times-archive-004",
    "times-archive-005",
    "times-archive-006",
    "times-archive-007",
    "times-archive-008",
    "times-archive-009",
    "times-archive-010",
    "times-archive-023",
    "times-archive-024",
    "times-archive-025",
    "times-archive-031",
    "times-archive-032",
    "times-archive-033",
    "times-archive-039",
    "times-archive-040",
    "times-archive-045",
    "times-archive-046",
}

NEW_EXERCISES: list[dict[str, Any]] = [
    {
        "id": "times-archive-051",
        "title": "Recursive publication years",
        "prompt": "List publication years from 1920 through 1925 using a recursive CTE.",
        "concept_tags": ["recursive-cte"],
        "hint": "Anchor on 1920 and increment until 1925.",
        "sample_sql": "WITH RECURSIVE years AS (\n  SELECT 1920 AS pub_year\n  UNION ALL\n  SELECT pub_year + 1 FROM years WHERE pub_year < 1925\n)\nSELECT pub_year FROM years;",
        "column_names": ["pub_year"],
        "reference_sql": "WITH RECURSIVE years AS (SELECT 1920 AS pub_year UNION ALL SELECT pub_year + 1 FROM years WHERE pub_year < 1925) SELECT pub_year FROM years ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-052",
        "title": "Sections without Sports",
        "prompt": "Which sections have articles but never appear under the Sports desk?",
        "concept_tags": ["anti-join"],
        "hint": "Use NOT EXISTS against Sports desk rows.",
        "sample_sql": "SELECT DISTINCT section_name FROM times_archive t WHERE NOT EXISTS (SELECT 1 FROM times_archive s WHERE s.section_name = t.section_name AND s.news_desk = 'Sports');",
        "column_names": ["section_name"],
        "reference_sql": "SELECT DISTINCT section_name FROM times_archive t WHERE NOT EXISTS (SELECT 1 FROM times_archive s WHERE s.section_name = t.section_name AND s.news_desk = 'Sports') ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-053",
        "title": "Keyword subject tags",
        "prompt": "Extract the first keyword subject value for each article.",
        "concept_tags": ["jsonb"],
        "hint": "Expand keywords JSON and read the value field.",
        "sample_sql": "SELECT headline_main, kw.value AS keyword_subject FROM times_archive, LATERAL jsonb_array_elements(keywords) AS kw WHERE kw->>'name' = 'subject' LIMIT 10;",
        "column_names": ["headline_main", "keyword_subject"],
        "reference_sql": "SELECT headline_main, kw.value AS keyword_subject FROM times_archive, LATERAL jsonb_array_elements(keywords) AS kw WHERE kw->>'name' = 'subject' ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-054",
        "title": "Long reads with FILTER",
        "prompt": "Per section, count articles over 1500 words and under 500 words using FILTER.",
        "concept_tags": ["filter-clause"],
        "hint": "Use COUNT(*) FILTER (WHERE ...).",
        "sample_sql": "SELECT section_name, COUNT(*) FILTER (WHERE word_count > 1500) AS long_reads, COUNT(*) FILTER (WHERE word_count < 500) AS short_reads FROM times_archive GROUP BY section_name;",
        "column_names": ["section_name", "long_reads", "short_reads"],
        "reference_sql": "SELECT section_name, COUNT(*) FILTER (WHERE word_count > 1500) AS long_reads, COUNT(*) FILTER (WHERE word_count < 500) AS short_reads FROM times_archive GROUP BY section_name ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-055",
        "title": "Desk union snapshot",
        "prompt": "Return distinct desk names from both news_desk and section_name columns in one result.",
        "concept_tags": ["union"],
        "hint": "UNION two SELECT DISTINCT queries.",
        "sample_sql": "SELECT news_desk AS desk_name FROM times_archive UNION SELECT section_name AS desk_name FROM times_archive;",
        "column_names": ["desk_name"],
        "reference_sql": "SELECT news_desk AS desk_name FROM times_archive UNION SELECT section_name AS desk_name FROM times_archive ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-056",
        "title": "Headlines with digits",
        "prompt": "Find headlines that contain at least one digit.",
        "concept_tags": ["regexp"],
        "hint": "Use headline_main ~ '[0-9]'.",
        "sample_sql": "SELECT headline_main FROM times_archive WHERE headline_main ~ '[0-9]';",
        "column_names": ["headline_main"],
        "reference_sql": "SELECT headline_main FROM times_archive WHERE headline_main ~ '[0-9]' ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-057",
        "title": "Median word count by desk",
        "prompt": "Compute the median word count for each news desk.",
        "concept_tags": ["percentile"],
        "hint": "Use PERCENTILE_CONT(0.5) WITHIN GROUP.",
        "sample_sql": "SELECT news_desk, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY word_count) AS median_word_count FROM times_archive GROUP BY news_desk;",
        "column_names": ["news_desk", "median_word_count"],
        "reference_sql": "SELECT news_desk, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY word_count) AS median_word_count FROM times_archive GROUP BY news_desk ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-058",
        "title": "Section and grand totals",
        "prompt": "Count articles by section and include a grand total row with GROUPING SETS.",
        "concept_tags": ["grouping-sets"],
        "hint": "GROUP BY GROUPING SETS ((section_name), ()).",
        "sample_sql": "SELECT section_name, COUNT(*) AS article_count FROM times_archive GROUP BY GROUPING SETS ((section_name), ());",
        "column_names": ["section_name", "article_count"],
        "reference_sql": "SELECT section_name, COUNT(*) AS article_count FROM times_archive GROUP BY GROUPING SETS ((section_name), ()) ORDER BY 1 NULLS LAST LIMIT 500;",
    },
    {
        "id": "times-archive-059",
        "title": "Publication month series",
        "prompt": "Generate each month in 1920 and left join article counts for that month.",
        "concept_tags": ["generate-series"],
        "hint": "Use generate_series with date_trunc month.",
        "sample_sql": "SELECT month_start, COUNT(t.article_id) AS article_count FROM generate_series('1920-01-01'::date, '1920-12-01'::date, interval '1 month') AS month_start LEFT JOIN times_archive t ON date_trunc('month', t.pub_date) = month_start GROUP BY month_start;",
        "column_names": ["month_start", "article_count"],
        "reference_sql": "SELECT month_start::date AS month_start, COUNT(t.article_id) AS article_count FROM generate_series('1920-01-01'::date, '1920-12-01'::date, interval '1 month') AS month_start LEFT JOIN times_archive t ON date_trunc('month', t.pub_date) = month_start GROUP BY month_start ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-060",
        "title": "Same-day longer neighbor",
        "prompt": "For each article, count how many other articles on the same day have a higher word count.",
        "concept_tags": ["self-join"],
        "hint": "Self-join on pub_date and compare word_count.",
        "sample_sql": "SELECT a.headline_main, COUNT(*) AS longer_same_day FROM times_archive a JOIN times_archive b ON a.pub_date = b.pub_date AND b.word_count > a.word_count GROUP BY a.headline_main;",
        "column_names": ["headline_main", "longer_same_day"],
        "reference_sql": "SELECT a.headline_main, COUNT(*) AS longer_same_day FROM times_archive a JOIN times_archive b ON a.pub_date = b.pub_date AND b.word_count > a.word_count GROUP BY a.headline_main ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-061",
        "title": "Desk above section average",
        "prompt": "Return desks whose average word count exceeds their section average.",
        "concept_tags": ["correlated-subquery"],
        "hint": "Compare desk AVG(word_count) to section AVG in a correlated subquery.",
        "sample_sql": "SELECT news_desk, section_name, ROUND(AVG(word_count), 2) AS desk_avg FROM times_archive GROUP BY news_desk, section_name HAVING AVG(word_count) > (SELECT AVG(word_count) FROM times_archive t2 WHERE t2.section_name = times_archive.section_name);",
        "column_names": ["news_desk", "section_name", "desk_avg"],
        "reference_sql": "SELECT news_desk, section_name, ROUND(AVG(word_count), 2) AS desk_avg FROM times_archive GROUP BY news_desk, section_name HAVING AVG(word_count) > (SELECT AVG(word_count) FROM times_archive t2 WHERE t2.section_name = times_archive.section_name) ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-062",
        "title": "Word count deciles",
        "prompt": "Assign each article to a word-count decile using NTILE(10).",
        "concept_tags": ["ntile"],
        "hint": "NTILE(10) OVER (ORDER BY word_count).",
        "sample_sql": "SELECT headline_main, word_count, NTILE(10) OVER (ORDER BY word_count) AS word_decile FROM times_archive;",
        "column_names": ["headline_main", "word_count", "word_decile"],
        "reference_sql": "SELECT headline_main, word_count, NTILE(10) OVER (ORDER BY word_count) AS word_decile FROM times_archive ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-063",
        "title": "Day-over-day publication change",
        "prompt": "For each publication date, show the change in daily article volume versus the previous day.",
        "concept_tags": ["lag-lead"],
        "hint": "Aggregate by day, then LAG daily counts.",
        "sample_sql": "WITH daily AS (SELECT pub_date, COUNT(*) AS daily_count FROM times_archive GROUP BY pub_date) SELECT pub_date, daily_count, daily_count - LAG(daily_count) OVER (ORDER BY pub_date) AS day_over_day_change FROM daily;",
        "column_names": ["pub_date", "daily_count", "day_over_day_change"],
        "reference_sql": "WITH daily AS (SELECT pub_date, COUNT(*) AS daily_count FROM times_archive GROUP BY pub_date) SELECT pub_date, daily_count, daily_count - LAG(daily_count) OVER (ORDER BY pub_date) AS day_over_day_change FROM daily ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-064",
        "title": "Ordered headline list per desk",
        "prompt": "For each desk, concatenate the three shortest headlines in alphabetical order.",
        "concept_tags": ["string-agg"],
        "hint": "Use string_agg inside a subquery limited to three rows per desk.",
        "sample_sql": "SELECT news_desk, string_agg(headline_main, '; ' ORDER BY headline_main) AS sample_headlines FROM (SELECT news_desk, headline_main, ROW_NUMBER() OVER (PARTITION BY news_desk ORDER BY LENGTH(headline_main), headline_main) AS rn FROM times_archive) ranked WHERE rn <= 3 GROUP BY news_desk;",
        "column_names": ["news_desk", "sample_headlines"],
        "reference_sql": "SELECT news_desk, string_agg(headline_main, '; ' ORDER BY headline_main) AS sample_headlines FROM (SELECT news_desk, headline_main, ROW_NUMBER() OVER (PARTITION BY news_desk ORDER BY LENGTH(headline_main), headline_main) AS rn FROM times_archive) ranked WHERE rn <= 3 GROUP BY news_desk ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-065",
        "title": "Keyword array per section",
        "prompt": "Collect distinct keyword values into an array for each section.",
        "concept_tags": ["array-agg"],
        "hint": "Expand keywords JSON and use array_agg(DISTINCT ...).",
        "sample_sql": "SELECT section_name, array_agg(DISTINCT kw.value) AS keyword_values FROM times_archive, LATERAL jsonb_array_elements(keywords) AS kw GROUP BY section_name;",
        "column_names": ["section_name", "keyword_values"],
        "reference_sql": "SELECT section_name, array_agg(DISTINCT kw.value ORDER BY kw.value) AS keyword_values FROM times_archive, LATERAL jsonb_array_elements(keywords) AS kw GROUP BY section_name ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-066",
        "title": "Sections beating archive average",
        "prompt": "Which sections have average word count above the overall archive average?",
        "concept_tags": ["having-subquery"],
        "hint": "GROUP BY section_name and compare to a scalar subquery.",
        "sample_sql": "SELECT section_name, ROUND(AVG(word_count), 2) AS avg_word_count FROM times_archive GROUP BY section_name HAVING AVG(word_count) > (SELECT AVG(word_count) FROM times_archive);",
        "column_names": ["section_name", "avg_word_count"],
        "reference_sql": "SELECT section_name, ROUND(AVG(word_count), 2) AS avg_word_count FROM times_archive GROUP BY section_name HAVING AVG(word_count) > (SELECT AVG(word_count) FROM times_archive) ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-067",
        "title": "Section rollup totals",
        "prompt": "Show article counts by section with subtotal rows using ROLLUP.",
        "concept_tags": ["rollup"],
        "hint": "GROUP BY ROLLUP(section_name).",
        "sample_sql": "SELECT section_name, COUNT(*) AS article_count FROM times_archive GROUP BY ROLLUP(section_name);",
        "column_names": ["section_name", "article_count"],
        "reference_sql": "SELECT section_name, COUNT(*) AS article_count FROM times_archive GROUP BY ROLLUP(section_name) ORDER BY 1 NULLS LAST LIMIT 500;",
    },
    {
        "id": "times-archive-068",
        "title": "Latest headline per section",
        "prompt": "Return the most recent headline for each section using DISTINCT ON.",
        "concept_tags": ["distinct-on"],
        "hint": "DISTINCT ON (section_name) ... ORDER BY section_name, pub_date DESC.",
        "sample_sql": "SELECT DISTINCT ON (section_name) section_name, headline_main, pub_date FROM times_archive ORDER BY section_name, pub_date DESC;",
        "column_names": ["section_name", "headline_main", "pub_date"],
        "reference_sql": "SELECT DISTINCT ON (section_name) section_name, headline_main, pub_date FROM times_archive ORDER BY section_name, pub_date DESC, headline_main LIMIT 500;",
    },
    {
        "id": "times-archive-069",
        "title": "Desk coverage gaps",
        "prompt": "List desks that appear in news_desk but not as any article's section_name.",
        "concept_tags": ["except"],
        "hint": "Use EXCEPT between two DISTINCT lists.",
        "sample_sql": "SELECT DISTINCT news_desk AS name FROM times_archive EXCEPT SELECT DISTINCT section_name AS name FROM times_archive;",
        "column_names": ["name"],
        "reference_sql": "SELECT DISTINCT news_desk AS name FROM times_archive EXCEPT SELECT DISTINCT section_name AS name FROM times_archive ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-070",
        "title": "Multimedia image articles",
        "prompt": "Find articles whose multimedia JSON reports at least one image asset.",
        "concept_tags": ["jsonb"],
        "hint": "Read multimedia_count_by_type->>'image'.",
        "sample_sql": "SELECT headline_main, (multimedia_count_by_type->>'image')::int AS image_count FROM times_archive WHERE COALESCE((multimedia_count_by_type->>'image')::int, 0) > 0;",
        "column_names": ["headline_main", "image_count"],
        "reference_sql": "SELECT headline_main, (multimedia_count_by_type->>'image')::int AS image_count FROM times_archive WHERE COALESCE((multimedia_count_by_type->>'image')::int, 0) > 0 ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-071",
        "title": "Byline contributor count",
        "prompt": "Count how many structured byline contributors each article has.",
        "concept_tags": ["jsonb"],
        "hint": "Use jsonb_array_length(byline_person).",
        "sample_sql": "SELECT headline_main, jsonb_array_length(byline_person) AS contributor_count FROM times_archive;",
        "column_names": ["headline_main", "contributor_count"],
        "reference_sql": "SELECT headline_main, jsonb_array_length(byline_person) AS contributor_count FROM times_archive ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-072",
        "title": "Running desk share",
        "prompt": "Show each desk's cumulative share of total articles when desks are ordered alphabetically.",
        "concept_tags": ["window-share"],
        "hint": "Use window SUM over desk counts divided by total.",
        "sample_sql": "WITH desk_counts AS (SELECT news_desk, COUNT(*) AS article_count FROM times_archive GROUP BY news_desk) SELECT news_desk, article_count, ROUND(100.0 * SUM(article_count) OVER (ORDER BY news_desk) / SUM(article_count) OVER (), 2) AS cumulative_pct FROM desk_counts;",
        "column_names": ["news_desk", "article_count", "cumulative_pct"],
        "reference_sql": "WITH desk_counts AS (SELECT news_desk, COUNT(*) AS article_count FROM times_archive GROUP BY news_desk) SELECT news_desk, article_count, ROUND(100.0 * SUM(article_count) OVER (ORDER BY news_desk) / SUM(article_count) OVER (), 2) AS cumulative_pct FROM desk_counts ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-073",
        "title": "Dense rank by word count",
        "prompt": "Dense-rank articles by word count within each section.",
        "concept_tags": ["dense-rank"],
        "hint": "DENSE_RANK() OVER (PARTITION BY section_name ORDER BY word_count DESC).",
        "sample_sql": "SELECT section_name, headline_main, word_count, DENSE_RANK() OVER (PARTITION BY section_name ORDER BY word_count DESC) AS dense_word_rank FROM times_archive;",
        "column_names": ["section_name", "headline_main", "word_count", "dense_word_rank"],
        "reference_sql": "SELECT section_name, headline_main, word_count, DENSE_RANK() OVER (PARTITION BY section_name ORDER BY word_count DESC) AS dense_word_rank FROM times_archive ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-074",
        "title": "First and last headline per month",
        "prompt": "For each publication month, return the alphabetically first and last headline.",
        "concept_tags": ["first-last-value"],
        "hint": "Use FIRST_VALUE and LAST_VALUE over monthly partitions.",
        "sample_sql": "SELECT DISTINCT date_trunc('month', pub_date) AS month_start, FIRST_VALUE(headline_main) OVER w AS first_headline, LAST_VALUE(headline_main) OVER w AS last_headline FROM times_archive WINDOW w AS (PARTITION BY date_trunc('month', pub_date) ORDER BY headline_main ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING);",
        "column_names": ["month_start", "first_headline", "last_headline"],
        "reference_sql": "SELECT DISTINCT date_trunc('month', pub_date) AS month_start, FIRST_VALUE(headline_main) OVER w AS first_headline, LAST_VALUE(headline_main) OVER w AS last_headline FROM times_archive WINDOW w AS (PARTITION BY date_trunc('month', pub_date) ORDER BY headline_main ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-075",
        "title": "Articles newer than section median",
        "prompt": "Return articles whose word count exceeds the median for their section.",
        "concept_tags": ["lateral"],
        "hint": "Join to a lateral subquery computing section medians.",
        "sample_sql": "SELECT t.headline_main, t.section_name, t.word_count FROM times_archive t JOIN LATERAL (SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY word_count) AS section_median FROM times_archive s WHERE s.section_name = t.section_name) m ON t.word_count > m.section_median;",
        "column_names": ["headline_main", "section_name", "word_count"],
        "reference_sql": "SELECT t.headline_main, t.section_name, t.word_count FROM times_archive t JOIN LATERAL (SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY word_count) AS section_median FROM times_archive s WHERE s.section_name = t.section_name) m ON t.word_count > m.section_median ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-076",
        "title": "Pivot-style material counts",
        "prompt": "For each section, count News and Review material types in separate columns.",
        "concept_tags": ["conditional-aggregation"],
        "hint": "SUM(CASE WHEN type_of_material = 'News' THEN 1 ELSE 0 END).",
        "sample_sql": "SELECT section_name, SUM(CASE WHEN type_of_material = 'News' THEN 1 ELSE 0 END) AS news_count, SUM(CASE WHEN type_of_material = 'Review' THEN 1 ELSE 0 END) AS review_count FROM times_archive GROUP BY section_name;",
        "column_names": ["section_name", "news_count", "review_count"],
        "reference_sql": "SELECT section_name, SUM(CASE WHEN type_of_material = 'News' THEN 1 ELSE 0 END) AS news_count, SUM(CASE WHEN type_of_material = 'Review' THEN 1 ELSE 0 END) AS review_count FROM times_archive GROUP BY section_name ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-077",
        "title": "Exists longer snippet",
        "prompt": "Find articles that have another article in the same section with a longer snippet.",
        "concept_tags": ["exists"],
        "hint": "Correlated EXISTS comparing snippet lengths.",
        "sample_sql": "SELECT headline_main, section_name FROM times_archive a WHERE EXISTS (SELECT 1 FROM times_archive b WHERE b.section_name = a.section_name AND LENGTH(b.snippet) > LENGTH(a.snippet));",
        "column_names": ["headline_main", "section_name"],
        "reference_sql": "SELECT headline_main, section_name FROM times_archive a WHERE EXISTS (SELECT 1 FROM times_archive b WHERE b.section_name = a.section_name AND LENGTH(b.snippet) > LENGTH(a.snippet)) ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-078",
        "title": "Weekday publication mix",
        "prompt": "Count articles published on each day of week.",
        "concept_tags": ["dates"],
        "hint": "to_char(pub_date, 'Day') or EXTRACT(DOW FROM pub_date).",
        "sample_sql": "SELECT TRIM(to_char(pub_date, 'Day')) AS weekday_name, COUNT(*) AS article_count FROM times_archive GROUP BY TRIM(to_char(pub_date, 'Day')), EXTRACT(DOW FROM pub_date) ORDER BY EXTRACT(DOW FROM pub_date);",
        "column_names": ["weekday_name", "article_count"],
        "reference_sql": "SELECT TRIM(to_char(pub_date, 'Day')) AS weekday_name, COUNT(*) AS article_count FROM times_archive GROUP BY TRIM(to_char(pub_date, 'Day')), EXTRACT(DOW FROM pub_date) ORDER BY EXTRACT(DOW FROM pub_date) LIMIT 500;",
    },
    {
        "id": "times-archive-079",
        "title": "Nth headline per desk",
        "prompt": "Return the second-shortest headline for each desk.",
        "concept_tags": ["nth-value"],
        "hint": "Use NTH_VALUE over PARTITION BY news_desk ordered by word_count.",
        "sample_sql": "SELECT DISTINCT news_desk, NTH_VALUE(headline_main, 2) OVER (PARTITION BY news_desk ORDER BY word_count, headline_main ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS second_shortest_headline FROM times_archive;",
        "column_names": ["news_desk", "second_shortest_headline"],
        "reference_sql": "SELECT DISTINCT news_desk, NTH_VALUE(headline_main, 2) OVER (PARTITION BY news_desk ORDER BY word_count, headline_main ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS second_shortest_headline FROM times_archive ORDER BY 1 LIMIT 500;",
    },
    {
        "id": "times-archive-080",
        "title": "Archive year depth",
        "prompt": "Using a recursive CTE, list archive years from the earliest publication year up to five years later.",
        "concept_tags": ["recursive-cte"],
        "hint": "Anchor on MIN(pub_date) year and recurse five steps.",
        "sample_sql": "WITH bounds AS (SELECT EXTRACT(YEAR FROM MIN(pub_date))::int AS start_year FROM times_archive), RECURSIVE years AS (SELECT start_year AS archive_year FROM bounds UNION ALL SELECT archive_year + 1 FROM years, bounds WHERE archive_year < start_year + 5) SELECT archive_year FROM years;",
        "column_names": ["archive_year"],
        "reference_sql": "WITH bounds AS (SELECT EXTRACT(YEAR FROM MIN(pub_date))::int AS start_year FROM times_archive), RECURSIVE years AS (SELECT start_year AS archive_year FROM bounds UNION ALL SELECT archive_year + 1 FROM years, bounds WHERE archive_year < start_year + 5) SELECT archive_year FROM years ORDER BY 1 LIMIT 500;",
    },
]


def _build_entry(spec: dict[str, Any], *, estimated_minutes: int) -> dict[str, Any]:
    exercise_id = spec["id"]
    title = spec["title"]
    concept = spec["concept_tags"][0]
    return {
        "id": exercise_id,
        "dataset_id": "times-archive",
        "title": title,
        "prompt": spec["prompt"],
        "difficulty": "Advanced",
        "target_dialect": "PostgreSQL",
        "concept_tags": spec["concept_tags"],
        "estimated_time_minutes": estimated_minutes,
        "learning_objectives": [
            f"Apply {concept} patterns to Times archive data.",
            f"Write an advanced PostgreSQL query for: {title.lower()}.",
        ],
        "hint": spec["hint"],
        "sample_sql": f"-- PostgreSQL target dialect\n{spec['sample_sql']}",
        "availability_status": "available",
        "expected_result": {
            "description": f"Reserved expected columns for {title}.",
            "column_names": spec["column_names"],
            "grading_row_order": "multiset",
        },
        "reference_sql": spec["reference_sql"],
    }


def main() -> None:
    exercises = json.loads(EXERCISES_PATH.read_text(encoding="utf-8"))
    retained: list[dict[str, Any]] = []
    for entry in exercises:
        if entry["id"] in BEGINNER_IDS:
            grid_path = GRIDS_DIR / f"{entry['id']}.json"
            if grid_path.exists():
                grid_path.unlink()
            continue
        entry.pop("mode", None)
        retained.append(entry)

    start_minutes = 15
    for index, spec in enumerate(NEW_EXERCISES):
        retained.append(_build_entry(spec, estimated_minutes=start_minutes + index))

    EXERCISES_PATH.write_text(
        json.dumps(retained, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(retained)} exercises to {EXERCISES_PATH}")


if __name__ == "__main__":
    main()

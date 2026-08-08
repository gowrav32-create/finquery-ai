import json
from pathlib import Path

from src.regression_detection.baseline import (
    load_evaluation_report,
    select_latest_report
)


def test_loads_saved_evaluation_report(
    tmp_path: Path
):
    report_path = tmp_path / "v1_test.json"

    report_data = {
        "prompt_version": "v1",
        "total_cases": 1,
        "passed_cases": 0,
        "failed_cases": 1,
        "pass_rate": 0.0,
        "failed_case_ids": [
            "finance_001"
        ],
        "results": [
            {
                "case_id": "finance_001",
                "passed": False
            }
        ]
    }

    report_path.write_text(
        json.dumps(report_data),
        encoding="utf-8"
    )

    loaded = load_evaluation_report(
        report_path
    )

    assert loaded["prompt_version"] == "v1"
    assert loaded["pass_rate"] == 0.0
    assert loaded["results"][0]["case_id"] == (
        "finance_001"
    )


def test_selects_latest_evaluation_report(
    tmp_path: Path
):
    older_report = tmp_path / (
        "v1_2026-08-01_10-00-00.json"
    )

    newer_report = tmp_path / (
        "v1_2026-08-07_20-00-00.json"
    )

    older_report.write_text(
        "{}",
        encoding="utf-8"
    )

    newer_report.write_text(
        "{}",
        encoding="utf-8"
    )

    import os

    os.utime(
        older_report,
        (1000, 1000)
    )

    os.utime(
        newer_report,
        (2000, 2000)
    )

    selected = select_latest_report(
        runs_directory=tmp_path
    )

    assert selected == newer_report


def test_returns_none_when_no_reports_exist(
    tmp_path: Path
):
    selected = select_latest_report(
        runs_directory=tmp_path
    )

    assert selected is None


def test_missing_report_raises_error(
    tmp_path: Path
):
    missing_report = tmp_path / "missing.json"

    try:
        load_evaluation_report(
            missing_report
        )

        assert False

    except FileNotFoundError as error:
        assert "Evaluation report not found" in str(error)
        
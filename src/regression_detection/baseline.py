import json
from pathlib import Path


def load_evaluation_report(
    report_path: Path
) -> dict:
    """
    Load one saved financial evaluation report from JSON.
    """
    if not report_path.exists():
        raise FileNotFoundError(
            f"Evaluation report not found: {report_path}"
        )

    with report_path.open(
        "r",
        encoding="utf-8"
    ) as file:
        report_data = json.load(file)

    if not isinstance(report_data, dict):
        raise ValueError(
            "Evaluation report must contain a JSON object."
        )

    return report_data


def select_latest_report(
    runs_directory: Path
) -> Path | None:
    """
    Return the most recently modified evaluation JSON report.

    Returns None when no reports are available.
    """
    if not runs_directory.exists():
        return None

    reports = list(
        runs_directory.glob("*.json")
    )

    if not reports:
        return None

    reports.sort(
        key=lambda report: report.stat().st_mtime
    )

    return reports[-1]

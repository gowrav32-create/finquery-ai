import json
from pathlib import Path

from src.regression_detection.evaluator import (
    FinancialCaseEvaluationResult
)
from src.regression_detection.reporting import (
    save_financial_evaluation_report
)
from src.regression_detection.runner import (
    FinancialEvaluationRun
)


def test_saves_financial_evaluation_report(
    tmp_path: Path
):
    evaluation_run = FinancialEvaluationRun(
        prompt_version="v1",
        total_cases=1,
        passed_cases=0,
        failed_cases=1,
        pass_rate=0.0,
        failed_case_ids=["finance_001"],
        results=[
            FinancialCaseEvaluationResult(
                case_id="finance_001",
                category="ranking",
                passed=False,
                clarification_match=True,
                execution_match=True,
                safety_match=True,
                tables_match=False,
                columns_match=False,
                row_count_match=True,
                rows_match=False,
                generated_sql=(
                    "SELECT ticker "
                    "FROM financial_metrics"
                ),
                actual_tables=[
                    "financial_metrics",
                    "annual_financials"
                ],
                actual_columns=["ticker"],
                actual_rows=[
                    {
                        "ticker": "NSS"
                    }
                ],
                failure_reasons=[
                    "unexpected_tables",
                    "result_columns_mismatch",
                    "row_values_mismatch"
                ]
            )
        ]
    )

    report_path = tmp_path / "report.json"

    save_financial_evaluation_report(
        evaluation_run=evaluation_run,
        report_path=report_path
    )

    report_data = json.loads(
        report_path.read_text(
            encoding="utf-8"
        )
    )

    assert report_data["prompt_version"] == "v1"
    assert report_data["total_cases"] == 1
    assert report_data["passed_cases"] == 0
    assert report_data["pass_rate"] == 0.0

    assert report_data["failed_case_ids"] == [
        "finance_001"
    ]

    assert report_data["results"][0]["case_id"] == (
        "finance_001"
    )

    assert (
        "unexpected_tables"
        in report_data["results"][0]["failure_reasons"]
    )


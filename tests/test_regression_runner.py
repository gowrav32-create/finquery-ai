from pathlib import Path
from types import SimpleNamespace

from src.regression_detection import runner
from src.regression_detection.runner import (
    load_golden_financial_cases,
    run_financial_evaluation
)


def test_loads_golden_financial_dataset():
    dataset_path = Path(
        "datasets/golden_financial_queries_v1.json"
    )

    test_cases = load_golden_financial_cases(
        dataset_path
    )

    assert len(test_cases) == 1
    assert test_cases[0].id == "finance_001"

    assert test_cases[0].question == (
        "Which company had the highest "
        "revenue growth in 2024?"
    )


def test_runs_dataset_and_calculates_failure_rate(
    tmp_path: Path,
    monkeypatch
):
    def fake_run_financial_query(
        question,
        database_path,
        prompt_path
    ):
        return SimpleNamespace(
            prompt_version="v1",
            generation_result=SimpleNamespace(
                sql=(
                    "SELECT t2.ticker "
                    "FROM financial_metrics AS t2 "
                    "JOIN annual_financials AS t1 "
                    "ON t2.ticker = t1.ticker "
                    "AND t2.fiscal_year = t1.fiscal_year "
                    "WHERE t2.fiscal_year = 2024 "
                    "ORDER BY "
                    "t2.revenue_growth_pct DESC "
                    "LIMIT 1"
                ),
                tables_used=[
                    "financial_metrics",
                    "annual_financials"
                ],
                clarification_needed=False
            ),
            execution=SimpleNamespace(
                safety_result=SimpleNamespace(
                    is_safe=True
                ),
                query_result=SimpleNamespace(
                    columns=["ticker"],
                    row_count=1,
                    rows=[
                        {
                            "ticker": "NSS"
                        }
                    ]
                )
            )
        )

    monkeypatch.setattr(
        runner,
        "run_financial_query",
        fake_run_financial_query
    )

    evaluation_run = run_financial_evaluation(
        dataset_path=Path(
            "datasets/golden_financial_queries_v1.json"
        ),
        database_path=(
            tmp_path / "financial_data.duckdb"
        ),
        prompt_path=Path(
            "prompts/sql_generation_v1.yaml"
        )
    )

    assert evaluation_run.prompt_version == "v1"
    assert evaluation_run.total_cases == 1
    assert evaluation_run.passed_cases == 0
    assert evaluation_run.failed_cases == 1
    assert evaluation_run.pass_rate == 0.0

    assert evaluation_run.failed_case_ids == [
        "finance_001"
    ]

    case_result = evaluation_run.results[0]

    assert case_result.passed is False

    assert "unexpected_tables" in (
        case_result.failure_reasons
    )

    assert "result_columns_mismatch" in (
        case_result.failure_reasons
    )

    assert "row_values_mismatch" in (
        case_result.failure_reasons
    )

from pathlib import Path

from src.database.build_database import (
    build_financial_database,
    create_financial_metrics_view,
    seed_demo_data
)
from src.query_engine import service
from src.query_engine.models import SQLGenerationResult
from src.query_engine.service import run_financial_query


def create_test_database(database_path: Path) -> None:
    build_financial_database(database_path)
    seed_demo_data(database_path)
    create_financial_metrics_view(database_path)


def test_runs_complete_financial_query_workflow(
    tmp_path: Path,
    monkeypatch
):
    database_path = tmp_path / "financial_data.duckdb"
    create_test_database(database_path)

    captured_request = {}

    def fake_generate_financial_sql(
        question,
        schema_context,
        prompt_config
    ):
        captured_request["question"] = question
        captured_request["schema_context"] = schema_context
        captured_request["prompt_version"] = (
            prompt_config.version
        )

        return SQLGenerationResult(
            sql=(
                "SELECT "
                "ticker, revenue_growth_pct "
                "FROM financial_metrics "
                "WHERE fiscal_year = 2024 "
                "ORDER BY revenue_growth_pct DESC "
                "LIMIT 1"
            ),
            explanation=(
                "Returns the company with the highest "
                "2024 revenue growth."
            ),
            confidence=0.97,
            tables_used=["financial_metrics"],
            columns_used=[
                "ticker",
                "revenue_growth_pct",
                "fiscal_year"
            ],
            clarification_needed=False,
            clarification_question=None
        )

    monkeypatch.setattr(
        service,
        "generate_financial_sql",
        fake_generate_financial_sql
    )

    response = run_financial_query(
        question=(
            "Which company had the highest "
            "revenue growth in 2024?"
        ),
        database_path=database_path,
        prompt_path=Path(
            "prompts/sql_generation_v1.yaml"
        )
    )

    assert response.prompt_version == "v1"
    assert response.generation_result.confidence == 0.97
    assert response.execution is not None

    assert response.execution.query_result.rows == [
        {
            "ticker": "NSS",
            "revenue_growth_pct": 22.92
        }
    ]

    assert captured_request["prompt_version"] == "v1"

    assert (
        "TABLE financial_metrics"
        in captured_request["schema_context"]
    )


def test_returns_clarification_without_executing_sql(
    tmp_path: Path,
    monkeypatch
):
    database_path = tmp_path / "financial_data.duckdb"
    create_test_database(database_path)

    def fake_generate_financial_sql(
        question,
        schema_context,
        prompt_config
    ):
        return SQLGenerationResult(
            sql=None,
            explanation=(
                "The meaning of best revenue "
                "is ambiguous."
            ),
            confidence=0.35,
            tables_used=[],
            columns_used=[],
            clarification_needed=True,
            clarification_question=(
                "Do you mean highest total revenue "
                "or highest revenue growth?"
            )
        )

    def fail_if_query_executes(*args, **kwargs):
        raise AssertionError(
            "SQL should not execute when "
            "clarification is required."
        )

    monkeypatch.setattr(
        service,
        "generate_financial_sql",
        fake_generate_financial_sql
    )

    monkeypatch.setattr(
        service,
        "run_validated_query",
        fail_if_query_executes
    )

    response = run_financial_query(
        question="Which company has the best revenue?",
        database_path=database_path,
        prompt_path=Path(
            "prompts/sql_generation_v1.yaml"
        )
    )

    assert response.execution is None
    assert (
        response.generation_result.clarification_needed
        is True
    )

    assert response.generation_result.clarification_question == (
        "Do you mean highest total revenue "
        "or highest revenue growth?"
    )
    
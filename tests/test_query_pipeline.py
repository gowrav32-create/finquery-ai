from pathlib import Path

import pytest

from src.database.build_database import (
    build_financial_database,
    create_financial_metrics_view,
    seed_demo_data
)
from src.query_engine.executor import UnsafeSQLQueryError
from src.query_engine.pipeline import (
    SQLSchemaError,
    run_validated_query
)


def create_test_database(database_path: Path) -> None:
    build_financial_database(database_path)
    seed_demo_data(database_path)
    create_financial_metrics_view(database_path)


def test_runs_query_after_all_validation_passes(
    tmp_path: Path
):
    database_path = tmp_path / "financial_data.duckdb"
    create_test_database(database_path)

    execution = run_validated_query(
        database_path=database_path,
        sql="""
            SELECT
                ticker,
                revenue_growth_pct
            FROM financial_metrics
            WHERE fiscal_year = 2024
            ORDER BY revenue_growth_pct DESC
        """
    )

    assert execution.safety_result.is_safe is True
    assert execution.schema_result.is_valid is True

    assert execution.query_result.row_count == 4

    assert execution.query_result.rows[0] == {
        "ticker": "NSS",
        "revenue_growth_pct": 22.92
    }


def test_blocks_unsafe_query(
    tmp_path: Path
):
    database_path = tmp_path / "financial_data.duckdb"
    create_test_database(database_path)

    with pytest.raises(
        UnsafeSQLQueryError,
        match="non_read_only_statement"
    ):
        run_validated_query(
            database_path=database_path,
            sql="DELETE FROM companies"
        )


def test_blocks_hallucinated_table(
    tmp_path: Path
):
    database_path = tmp_path / "financial_data.duckdb"
    create_test_database(database_path)

    with pytest.raises(
        SQLSchemaError,
        match="Unknown tables: stock_fundamentals"
    ):
        run_validated_query(
            database_path=database_path,
            sql="""
                SELECT ticker
                FROM stock_fundamentals
            """
        )


def test_blocks_hallucinated_column(
    tmp_path: Path
):
    database_path = tmp_path / "financial_data.duckdb"
    create_test_database(database_path)

    with pytest.raises(
        SQLSchemaError,
        match="Unknown columns: profit_growth"
    ):
        run_validated_query(
            database_path=database_path,
            sql="""
                SELECT
                    ticker,
                    profit_growth
                FROM financial_metrics
            """
        )

        
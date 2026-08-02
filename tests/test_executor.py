from pathlib import Path

import pytest

from src.database.build_database import (
    build_financial_database,
    create_financial_metrics_view,
    seed_demo_data
)
from src.query_engine.executor import (
    UnsafeSQLQueryError,
    execute_read_only_query
)


def create_test_database(database_path: Path) -> None:
    build_financial_database(database_path)
    seed_demo_data(database_path)
    create_financial_metrics_view(database_path)


def test_executes_safe_select_query(tmp_path: Path):
    database_path = tmp_path / "financial_data.duckdb"
    create_test_database(database_path)

    result = execute_read_only_query(
        database_path=database_path,
        sql="""
            SELECT
                ticker,
                company_name
            FROM companies
            ORDER BY ticker
        """
    )

    assert result.columns == [
        "ticker",
        "company_name"
    ]

    assert result.rows == [
        {
            "ticker": "ART",
            "company_name": "Apex Retail"
        },
        {
            "ticker": "HEN",
            "company_name": "Harbor Energy"
        },
        {
            "ticker": "MFB",
            "company_name": "Metro Financial Bank"
        },
        {
            "ticker": "NSS",
            "company_name": "Northstar Software"
        }
    ]

    assert result.row_count == 4
    assert result.execution_time_ms >= 0


def test_executes_financial_metrics_query(tmp_path: Path):
    database_path = tmp_path / "financial_data.duckdb"
    create_test_database(database_path)

    result = execute_read_only_query(
        database_path=database_path,
        sql="""
            SELECT
                ticker,
                revenue_growth_pct,
                operating_margin_pct
            FROM financial_metrics
            WHERE fiscal_year = 2024
              AND revenue_growth_pct > 20
            ORDER BY ticker
        """
    )

    assert result.row_count == 1

    assert result.rows[0] == {
        "ticker": "NSS",
        "revenue_growth_pct": 22.92,
        "operating_margin_pct": 24.58
    }


def test_blocks_unsafe_query_before_execution(
    tmp_path: Path
):
    database_path = tmp_path / "financial_data.duckdb"
    create_test_database(database_path)

    with pytest.raises(
        UnsafeSQLQueryError,
        match="non_read_only_statement"
    ):
        execute_read_only_query(
            database_path=database_path,
            sql="DROP TABLE companies"
        )


def test_rejects_missing_database(tmp_path: Path):
    database_path = tmp_path / "missing.duckdb"

    with pytest.raises(
        FileNotFoundError,
        match="Database not found"
    ):
        execute_read_only_query(
            database_path=database_path,
            sql="SELECT * FROM companies"
        )
        
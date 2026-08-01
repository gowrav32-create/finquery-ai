from pathlib import Path

import duckdb

from src.database.build_database import build_financial_database, create_financial_metrics_view, seed_demo_data


def test_build_financial_database_creates_expected_tables(
    tmp_path: Path
):
    database_path = tmp_path / "financial_data.duckdb"

    build_financial_database(database_path)

    with duckdb.connect(
        str(database_path),
        read_only=True
    ) as connection:
        table_rows = connection.execute(
            "SHOW TABLES"
        ).fetchall()

    tables = {
        row[0]
        for row in table_rows
    }

    assert tables == {
        "annual_financials",
        "companies",
        "valuation_snapshots"
    }

def test_seed_demo_data_inserts_expected_records(
    tmp_path: Path
):
    database_path = tmp_path / "financial_data.duckdb"

    build_financial_database(database_path)
    seed_demo_data(database_path)

    with duckdb.connect(
        str(database_path),
        read_only=True
    ) as connection:
        company_count = connection.execute(
            "SELECT COUNT(*) FROM companies"
        ).fetchone()[0]

        financial_count = connection.execute(
            "SELECT COUNT(*) FROM annual_financials"
        ).fetchone()[0]

        valuation_count = connection.execute(
            "SELECT COUNT(*) FROM valuation_snapshots"
        ).fetchone()[0]

    assert company_count == 4
    assert financial_count == 12
    assert valuation_count == 4

def test_financial_metrics_view_calculates_expected_values(
    tmp_path: Path
):
    database_path = tmp_path / "financial_data.duckdb"

    build_financial_database(database_path)
    seed_demo_data(database_path)
    create_financial_metrics_view(database_path)

    with duckdb.connect(
        str(database_path),
        read_only=True
    ) as connection:
        metrics = connection.execute(
            """
            SELECT
                revenue_growth_pct,
                operating_margin_pct,
                net_margin_pct,
                free_cash_flow,
                return_on_equity_pct,
                debt_to_equity
            FROM financial_metrics
            WHERE ticker = 'NSS'
              AND fiscal_year = 2024
            """
        ).fetchone()

    assert metrics == (
        22.92,
        24.58,
        18.64,
        2450.0,
        20.37,
        0.19
    )

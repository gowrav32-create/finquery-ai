from pathlib import Path

from src.database.build_database import (
    build_financial_database,
    create_financial_metrics_view,
    seed_demo_data
)
from src.database.schema import get_database_schema


def test_get_database_schema_returns_tables_and_columns(
    tmp_path: Path
):
    database_path = tmp_path / "financial_data.duckdb"

    build_financial_database(database_path)
    seed_demo_data(database_path)
    create_financial_metrics_view(database_path)

    schema = get_database_schema(database_path)

    assert set(schema.keys()) == {
        "annual_financials",
        "companies",
        "financial_metrics",
        "valuation_snapshots"
    }

    assert schema["companies"]["ticker"] == "VARCHAR"
    assert schema["companies"]["company_name"] == "VARCHAR"

    assert (
        schema["annual_financials"]["revenue"]
        == "DOUBLE"
    )

    assert (
        schema["financial_metrics"]["revenue_growth_pct"]
        == "DOUBLE"
    )

    assert (
        schema["valuation_snapshots"]["snapshot_date"]
        == "DATE"
    )
    
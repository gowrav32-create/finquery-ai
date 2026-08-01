from pathlib import Path

from src.database.build_database import (
    build_financial_database,
    create_financial_metrics_view,
    seed_demo_data
)
from src.database.schema import format_schema_for_prompt, get_database_schema


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

def test_format_schema_for_prompt_creates_readable_context():
    schema = {
        "companies": {
            "ticker": "VARCHAR",
            "company_name": "VARCHAR"
        },
        "financial_metrics": {
            "ticker": "VARCHAR",
            "fiscal_year": "INTEGER",
            "revenue_growth_pct": "DOUBLE"
        }
    }

    formatted_schema = format_schema_for_prompt(schema)

    assert formatted_schema == (
        "TABLE companies\n"
        "- ticker: VARCHAR\n"
        "- company_name: VARCHAR\n"
        "\n"
        "TABLE financial_metrics\n"
        "- ticker: VARCHAR\n"
        "- fiscal_year: INTEGER\n"
        "- revenue_growth_pct: DOUBLE"
    )
    
from pathlib import Path

import duckdb

FINANCIAL_COLUMN_DESCRIPTIONS = {
    "revenue_growth_pct": (
        "year-over-year percentage change in revenue"
    ),
    "operating_margin_pct": (
        "operating income divided by revenue, "
        "expressed as a percentage"
    ),
    "net_margin_pct": (
        "net income divided by revenue, "
        "expressed as a percentage"
    ),
    "free_cash_flow": (
        "operating cash flow minus capital expenditures"
    ),
    "return_on_equity_pct": (
        "net income divided by shareholder equity, "
        "expressed as a percentage"
    ),
    "debt_to_equity": (
        "total debt divided by shareholder equity"
    )
}

def get_database_schema(
    database_path: Path
) -> dict[str, dict[str, str]]:
    """
    Return every table or view and its columns from the DuckDB database.

    Example:
    {
        "companies": {
            "ticker": "VARCHAR",
            "company_name": "VARCHAR"
        }
    }
    """
    schema: dict[str, dict[str, str]] = {}

    with duckdb.connect(
        str(database_path),
        read_only=True
    ) as connection:
        rows = connection.execute(
            """
            SELECT
                table_name,
                column_name,
                data_type
            FROM information_schema.columns
            WHERE table_schema = 'main'
            ORDER BY
                table_name,
                ordinal_position
            """
        ).fetchall()

    for table_name, column_name, data_type in rows:
        if table_name not in schema:
            schema[table_name] = {}

        schema[table_name][column_name] = data_type

    return schema

def format_schema_for_prompt(
    schema: dict[str, dict[str, str]]
) -> str:
    """
    Convert a database schema dictionary into readable prompt context.

    Example:

    TABLE companies
    - ticker: VARCHAR
    - company_name: VARCHAR
    """
    sections = []

    for table_name, columns in schema.items():
        lines = [
            f"TABLE {table_name}"
        ]

        for column_name, data_type in columns.items():
            description = FINANCIAL_COLUMN_DESCRIPTIONS.get(
                column_name
            )

            if description:
                lines.append(
                    f"- {column_name}: {data_type}"
                    f" | Meaning: {description}"
                )
            else:
                lines.append(
                    f"- {column_name}: {data_type}"
                )

        sections.append(
            "\n".join(lines)
        )

    return "\n\n".join(sections)

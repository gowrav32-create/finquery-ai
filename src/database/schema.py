from pathlib import Path

import duckdb


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
            lines.append(
                f"- {column_name}: {data_type}"
            )

        sections.append(
            "\n".join(lines)
        )

    return "\n\n".join(sections)

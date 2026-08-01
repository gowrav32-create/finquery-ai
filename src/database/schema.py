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
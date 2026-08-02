from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

import duckdb

from src.query_engine.guardrails import check_sql_safety


class UnsafeSQLQueryError(ValueError):
    """Raised when a SQL query fails the safety guardrails."""


@dataclass
class QueryResult:
    """
    Structured result returned after executing a safe SQL query.
    """

    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    execution_time_ms: float


def execute_read_only_query(
    database_path: Path,
    sql: str
) -> QueryResult:
    """
    Validate and execute one read-only SQL query.

    The function:
    1. Applies SQL safety guardrails.
    2. Confirms the database exists.
    3. Opens DuckDB in read-only mode.
    4. Returns structured query results.
    """
    safety_result = check_sql_safety(sql)

    if not safety_result.is_safe:
        violations = ", ".join(
            safety_result.violations
        )

        raise UnsafeSQLQueryError(
            f"Unsafe SQL query: {violations}"
        )

    if not database_path.exists():
        raise FileNotFoundError(
            f"Database not found: {database_path}"
        )

    start_time = perf_counter()

    with duckdb.connect(
        str(database_path),
        read_only=True
    ) as connection:
        cursor = connection.execute(sql)

        column_names = [
            description[0]
            for description in cursor.description
        ]

        raw_rows = cursor.fetchall()

    execution_time_ms = round(
        (perf_counter() - start_time) * 1000,
        3
    )

    rows = [
        dict(zip(column_names, row))
        for row in raw_rows
    ]

    return QueryResult(
        columns=column_names,
        rows=rows,
        row_count=len(rows),
        execution_time_ms=execution_time_ms
    )

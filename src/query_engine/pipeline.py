from dataclasses import dataclass
from pathlib import Path

from src.database.schema import get_database_schema
from src.query_engine.executor import (
    QueryResult,
    UnsafeSQLQueryError,
    execute_read_only_query
)
from src.query_engine.guardrails import (
    SQLSafetyResult,
    check_sql_safety
)
from src.query_engine.validator import (
    SQLSchemaValidationResult,
    validate_sql_schema
)


class SQLSchemaError(ValueError):
    """Raised when SQL references unknown tables or columns."""


@dataclass
class ValidatedQueryExecution:
    """
    Evidence returned from every stage of the query pipeline.
    """

    safety_result: SQLSafetyResult
    schema_result: SQLSchemaValidationResult
    query_result: QueryResult


def run_validated_query(
    database_path: Path,
    sql: str
) -> ValidatedQueryExecution:
    """
    Validate and execute one financial SQL query.

    Processing order:
    1. Verify that the SQL is read-only.
    2. Load the real DuckDB schema.
    3. Detect hallucinated tables and columns.
    4. Execute through the read-only query executor.
    """
    safety_result = check_sql_safety(sql)

    if not safety_result.is_safe:
        violations = ", ".join(
            safety_result.violations
        )

        raise UnsafeSQLQueryError(
            f"Unsafe SQL query: {violations}"
        )

    schema = get_database_schema(database_path)

    schema_result = validate_sql_schema(
        sql=sql,
        schema=schema
    )

    if not schema_result.is_valid:
        error_parts = []

        if schema_result.unknown_tables:
            error_parts.append(
                "Unknown tables: "
                + ", ".join(schema_result.unknown_tables)
            )

        if schema_result.unknown_columns:
            error_parts.append(
                "Unknown columns: "
                + ", ".join(schema_result.unknown_columns)
            )

        if schema_result.errors:
            error_parts.append(
                "Validation errors: "
                + ", ".join(schema_result.errors)
            )

        raise SQLSchemaError(
            "; ".join(error_parts)
        )

    query_result = execute_read_only_query(
        database_path=database_path,
        sql=sql
    )

    return ValidatedQueryExecution(
        safety_result=safety_result,
        schema_result=schema_result,
        query_result=query_result
    )

from dataclasses import dataclass, field

from sqlglot import expressions as exp
from sqlglot import parse_one
from sqlglot.errors import ParseError


@dataclass
class SQLSchemaValidationResult:
    """
    Result of validating SQL table and column references
    against the real database schema.
    """

    is_valid: bool
    unknown_tables: list[str] = field(default_factory=list)
    unknown_columns: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def _append_unique(
    values: list[str],
    value: str
) -> None:
    """Append a value only when it is not already present."""
    if value not in values:
        values.append(value)


def validate_sql_schema(
    sql: str,
    schema: dict[str, dict[str, str]]
) -> SQLSchemaValidationResult:
    """
    Verify that SQL references only known database tables and columns.

    The validator supports:
    - Regular table references
    - Table aliases
    - JOIN statements
    - Unqualified columns
    - SELECT *
    - Common table expressions
    """
    try:
        parsed_query = parse_one(
            sql,
            read="duckdb"
        )
    except ParseError:
        return SQLSchemaValidationResult(
            is_valid=False,
            errors=["invalid_sql"]
        )

    unknown_tables: list[str] = []
    unknown_columns: list[str] = []

    alias_to_table: dict[str, str] = {}
    referenced_known_tables: list[str] = []

    cte_names = {
        cte.alias_or_name
        for cte in parsed_query.find_all(exp.CTE)
    }

    for table in parsed_query.find_all(exp.Table):
        table_name = table.name
        alias_name = table.alias_or_name

        # A CTE is a temporary query result, not a physical table.
        if table_name in cte_names:
            alias_to_table[alias_name] = table_name
            continue

        alias_to_table[alias_name] = table_name
        alias_to_table[table_name] = table_name

        if table_name not in schema:
            _append_unique(
                unknown_tables,
                table_name
            )
            continue

        _append_unique(
            referenced_known_tables,
            table_name
        )

    # An alias created in SELECT may be referenced later by ORDER BY.
    select_aliases = {
        alias.alias
        for alias in parsed_query.find_all(exp.Alias)
        if alias.alias
    }

    for column in parsed_query.find_all(exp.Column):
        column_name = column.name
        qualifier = column.table

        # SELECT * and table.* are allowed.
        if column_name == "*":
            continue

        if qualifier:
            # Columns produced by a CTE cannot always be validated
            # directly against the physical database schema.
            if qualifier in cte_names:
                continue

            actual_table = alias_to_table.get(
                qualifier
            )

            # Avoid reporting cascading column errors when the table
            # itself was already identified as hallucinated.
            if (
                actual_table is None
                or actual_table not in schema
            ):
                continue

            if column_name not in schema[actual_table]:
                _append_unique(
                    unknown_columns,
                    f"{qualifier}.{column_name}"
                )

            continue

        # ORDER BY may reference a SELECT alias rather than a
        # physical database column.
        if column_name in select_aliases:
            continue

        # If all referenced tables are unknown, avoid creating
        # additional misleading column errors.
        if not referenced_known_tables:
            continue

        column_exists = any(
            column_name in schema[table_name]
            for table_name in referenced_known_tables
        )

        if not column_exists:
            _append_unique(
                unknown_columns,
                column_name
            )

    is_valid = (
        not unknown_tables
        and not unknown_columns
    )

    return SQLSchemaValidationResult(
        is_valid=is_valid,
        unknown_tables=unknown_tables,
        unknown_columns=unknown_columns
    )

from dataclasses import dataclass, field

from sqlglot import expressions as exp
from sqlglot import parse
from sqlglot.errors import ParseError


@dataclass
class SQLSafetyResult:
    """
    Result returned after checking whether SQL is safe to execute.
    """

    is_safe: bool
    violations: list[str] = field(default_factory=list)


def check_sql_safety(sql: str) -> SQLSafetyResult:
    """
    Validate that a SQL string contains exactly one read-only query.

    Allowed:
    - SELECT statements
    - WITH common table expressions ending in SELECT

    Blocked:
    - INSERT
    - UPDATE
    - DELETE
    - CREATE
    - DROP
    - ALTER
    - Multiple statements
    - Invalid SQL
    """
    if not sql or not sql.strip():
        return SQLSafetyResult(
            is_safe=False,
            violations=["invalid_sql"]
        )

    try:
        statements = [
            statement
            for statement in parse(
                sql,
                read="duckdb"
            )
            if statement is not None
        ]
    except ParseError:
        return SQLSafetyResult(
            is_safe=False,
            violations=["invalid_sql"]
        )

    if len(statements) != 1:
        return SQLSafetyResult(
            is_safe=False,
            violations=["multiple_statements"]
        )

    statement = statements[0]

    if not isinstance(statement, exp.Select):
        return SQLSafetyResult(
            is_safe=False,
            violations=["non_read_only_statement"]
        )

    return SQLSafetyResult(
        is_safe=True,
        violations=[]
    )

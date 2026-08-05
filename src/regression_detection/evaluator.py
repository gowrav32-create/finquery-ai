from dataclasses import dataclass, field
from typing import Any

from src.regression_detection.models import (
    GoldenFinancialQueryCase
)


@dataclass
class FinancialCaseEvaluationResult:
    """
    Result of comparing one FinQuery AI response with
    one human-verified golden financial query case.
    """

    case_id: str
    category: str
    passed: bool

    clarification_match: bool
    execution_match: bool
    safety_match: bool
    tables_match: bool
    columns_match: bool
    row_count_match: bool
    rows_match: bool

    generated_sql: str | None
    actual_tables: list[str] = field(default_factory=list)
    actual_columns: list[str] = field(default_factory=list)
    actual_rows: list[dict[str, Any]] = field(
        default_factory=list
    )

    failure_reasons: list[str] = field(
        default_factory=list
    )


def evaluate_financial_case(
    test_case: GoldenFinancialQueryCase,
    response: Any
) -> FinancialCaseEvaluationResult:
    """
    Compare one FinQuery AI response against its golden expectations.

    The evaluator checks:
    - clarification behavior
    - successful execution
    - read-only safety
    - tables used
    - required result columns
    - returned row count
    - returned financial values
    """
    failure_reasons: list[str] = []

    generation_result = response.generation_result
    execution = response.execution

    clarification_requested = (
        generation_result.clarification_needed
    )

    clarification_match = not (
        test_case.requirements.must_not_request_clarification
        and clarification_requested
    )

    if not clarification_match:
        failure_reasons.append(
            "unexpected_clarification"
        )

    execution_match = not (
        test_case.requirements.must_execute
        and execution is None
    )

    if not execution_match:
        failure_reasons.append(
            "query_not_executed"
        )

    generated_sql = generation_result.sql
    actual_tables = list(
        generation_result.tables_used
    )

    expected_table_set = set(
        test_case.expected_tables
    )
    actual_table_set = set(
        actual_tables
    )

    tables_match = (
        expected_table_set == actual_table_set
    )

    if not tables_match:
        if actual_table_set - expected_table_set:
            failure_reasons.append(
                "unexpected_tables"
            )

        if expected_table_set - actual_table_set:
            failure_reasons.append(
                "missing_expected_tables"
            )

    safety_match = True
    actual_columns: list[str] = []
    actual_rows: list[dict[str, Any]] = []

    row_count_match = False
    columns_match = False
    rows_match = False

    if execution is not None:
        safety_match = (
            execution.safety_result.is_safe
        )

        if (
            test_case.requirements.must_be_read_only
            and not safety_match
        ):
            failure_reasons.append(
                "unsafe_sql"
            )

        query_result = execution.query_result

        actual_columns = list(
            query_result.columns
        )

        actual_rows = list(
            query_result.rows
        )

        expected_column_set = set(
            test_case.expected_columns
        )
        actual_column_set = set(
            actual_columns
        )

        columns_match = (
            expected_column_set
            .issubset(actual_column_set)
        )

        if not columns_match:
            failure_reasons.append(
                "result_columns_mismatch"
            )

        row_count_match = (
            query_result.row_count
            == test_case.expected_row_count
        )

        if not row_count_match:
            failure_reasons.append(
                "row_count_mismatch"
            )

        rows_match = (
            actual_rows
            == test_case.expected_rows
        )

        if not rows_match:
            failure_reasons.append(
                "row_values_mismatch"
            )
    else:
        safety_match = not (
            test_case.requirements.must_be_read_only
        )

        tables_match = (
            tables_match
            if not clarification_requested
            else False
        )

    passed = (
        clarification_match
        and execution_match
        and safety_match
        and tables_match
        and columns_match
        and row_count_match
        and rows_match
        and not failure_reasons
    )

    return FinancialCaseEvaluationResult(
        case_id=test_case.id,
        category=test_case.category,
        passed=passed,
        clarification_match=clarification_match,
        execution_match=execution_match,
        safety_match=safety_match,
        tables_match=tables_match,
        columns_match=columns_match,
        row_count_match=row_count_match,
        rows_match=rows_match,
        generated_sql=generated_sql,
        actual_tables=actual_tables,
        actual_columns=actual_columns,
        actual_rows=actual_rows,
        failure_reasons=failure_reasons
    )

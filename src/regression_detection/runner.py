import json
from dataclasses import dataclass, field
from pathlib import Path

from src.query_engine.service import FinancialSemanticError, run_financial_query
from src.regression_detection.evaluator import (
    FinancialCaseEvaluationResult,
    evaluate_financial_case
)
from src.regression_detection.models import (
    GoldenFinancialQueryCase
)

from src.query_engine.prompt_config import (
    load_sql_prompt_config
)


@dataclass
class FinancialEvaluationRun:
    """
    Summary of one complete regression evaluation run.
    """

    prompt_version: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float

    failed_case_ids: list[str] = field(
        default_factory=list
    )

    results: list[FinancialCaseEvaluationResult] = field(
        default_factory=list
    )


def load_golden_financial_cases(
    dataset_path: Path
) -> list[GoldenFinancialQueryCase]:
    """
    Load and validate the financial golden dataset.
    """
    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Golden dataset not found: {dataset_path}"
        )

    with dataset_path.open(
        "r",
        encoding="utf-8"
    ) as file:
        dataset_data = json.load(file)

    if not isinstance(dataset_data, list):
        raise ValueError(
            "Golden financial dataset must contain a JSON list."
        )

    return [
        GoldenFinancialQueryCase(**case)
        for case in dataset_data
    ]


def run_financial_evaluation(
    dataset_path: Path,
    database_path: Path,
    prompt_path: Path
) -> FinancialEvaluationRun:
    """
    Run every golden financial query against FinQuery AI.

    Individual model/query failures are recorded as failed
    evaluation cases instead of crashing the entire run.
    """
    test_cases = load_golden_financial_cases(
        dataset_path
    )

    prompt_config = load_sql_prompt_config(
        prompt_path
    )

    prompt_version = prompt_config.version

    results = []

    for test_case in test_cases:
        try:
            response = run_financial_query(
                question=test_case.question,
                database_path=database_path,
                prompt_path=prompt_path
            )

            result = evaluate_financial_case(
                test_case=test_case,
                response=response
            )

        except FinancialSemanticError as error:
            error_message = str(error)

            prefix = (
                "Generated SQL does not reference "
                "the requested financial metric(s): "
            )

            if error_message.startswith(prefix):
                missing_metrics = error_message[
                    len(prefix):
                ].strip()
            else:
                missing_metrics = error_message

            result = FinancialCaseEvaluationResult(
                case_id=test_case.id,
                category=test_case.category,
                passed=False,

                clarification_match=True,
                execution_match=False,
                safety_match=True,
                tables_match=False,
                columns_match=False,
                row_count_match=False,
                rows_match=False,

                generated_sql=None,
                actual_tables=[],
                actual_columns=[],
                actual_rows=[],

                failure_reasons=[
                    (
                        "semantic_validation_failed: "
                        f"{missing_metrics}"
                    )
                ]
            )

        except Exception as error:
            result = FinancialCaseEvaluationResult(
                case_id=test_case.id,
                category=test_case.category,
                passed=False,

                clarification_match=False,
                execution_match=False,
                safety_match=False,
                tables_match=False,
                columns_match=False,
                row_count_match=False,
                rows_match=False,

                generated_sql=None,
                actual_tables=[],
                actual_columns=[],
                actual_rows=[],

                failure_reasons=[
                    (
                        "generation_error: "
                        f"{type(error).__name__}: "
                        f"{error}"
                    )
                ]
            )

        results.append(
            result
        )

    passed_cases = sum(
        result.passed
        for result in results
    )

    total_cases = len(
        results
    )

    failed_cases = (
        total_cases
        - passed_cases
    )

    if total_cases == 0:
        pass_rate = 0.0
    else:
        pass_rate = round(
            (
                passed_cases
                / total_cases
            ) * 100,
            2
        )

    failed_case_ids = [
        result.case_id
        for result in results
        if not result.passed
    ]

    return FinancialEvaluationRun(
        prompt_version=prompt_version,
        total_cases=total_cases,
        passed_cases=passed_cases,
        failed_cases=failed_cases,
        pass_rate=pass_rate,
        failed_case_ids=failed_case_ids,
        results=results
    )

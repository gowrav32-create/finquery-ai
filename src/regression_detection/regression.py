from dataclasses import dataclass, field
from typing import Any

def calculate_regression(
    current_pass_rate: float,
    previous_pass_rate: float | None
) -> tuple[float | None, bool]:
    if previous_pass_rate is None:
        return None, False
    
    pass_rate_change = round(
        current_pass_rate - previous_pass_rate,
        2
    )

    regression_detected = pass_rate_change < 0

    return pass_rate_change, regression_detected


def calculate_shared_case_pass_rates(
        current_results: list[dict],
        previous_results: list[dict]
) -> tuple[float | None, float | None]:
    previous_results_by_case = {
        result["case_id"]: result["category_match"]
        for result in previous_results
    }

    shared_current_results = []
    shared_previous_results = []

    for current_result in current_results:
        case_id = current_result["case_id"]

        if case_id not in previous_results_by_case:
            continue

        shared_current_results.append(
            current_result["category_match"]
        )

        shared_previous_results.append(
            previous_results_by_case[case_id]
        )

    if not shared_current_results:
        return None, None

    current_passed = sum(shared_current_results)
    previous_passed = sum(shared_previous_results)
    shared_case_count = len(shared_current_results)

    current_pass_rate = round(
        (current_passed / shared_case_count) * 100,
        2
    )


    previous_pass_rate = round(
        (previous_passed / shared_case_count) * 100,
        2
    )

    return current_pass_rate, previous_pass_rate


def find_case_regressions(
    current_results: list[dict],
    previous_results: list[dict]
) -> list[str]:
    previous_results_by_case = {
        result["case_id"]: result["category_match"]
        for result in previous_results
    }

    regressions = []

    for current_result in current_results:
        case_id = current_result["case_id"]

        if case_id not in previous_results_by_case:
            continue

        previously_passed = (
            previous_results_by_case[case_id] is True
        )

        currently_failed = (
            current_result["category_match"] is False
        )

        if previously_passed and currently_failed:
            regressions.append(case_id)

    return regressions

def find_quality_gate_failures(
    current_pass_rate: float,
    pass_rate_change: float | None,
    minimum_pass_rate: float,
    maximum_drop: float
) -> list[str]:
    failures = []

    if current_pass_rate < minimum_pass_rate:
        failures.append("minimum_pass_rate")

    if (
        pass_rate_change is not None
        and pass_rate_change < -maximum_drop
    ):
        failures.append("maximum_drop")

    return failures

@dataclass
class FinancialRunComparison:
    """
    Comparison of shared financial evaluation cases
    between a previous run and the current run.
    """

    shared_case_count: int

    previous_pass_rate: float | None
    current_pass_rate: float | None
    pass_rate_change: float | None

    regressions: list[str] = field(
        default_factory=list
    )

    improvements: list[str] = field(
        default_factory=list
    )


def _get_result_value(
    result: Any,
    field_name: str
):
    """
    Read a field from either a dataclass/object
    or a dictionary loaded from JSON.
    """
    if isinstance(result, dict):
        return result[field_name]

    return getattr(
        result,
        field_name
    )


def compare_financial_runs(
    current_results: list,
    previous_results: list
) -> FinancialRunComparison:
    """
    Compare shared financial cases between two evaluation runs.

    A regression means:
        previous PASS -> current FAIL

    An improvement means:
        previous FAIL -> current PASS

    New cases are excluded from regression calculations because
    they did not exist in the previous run.
    """
    previous_by_case = {
        _get_result_value(
            result,
            "case_id"
        ): _get_result_value(
            result,
            "passed"
        )
        for result in previous_results
    }

    shared_previous_statuses = []
    shared_current_statuses = []

    regressions = []
    improvements = []

    for current_result in current_results:
        case_id = _get_result_value(
            current_result,
            "case_id"
        )

        if case_id not in previous_by_case:
            continue

        previous_passed = previous_by_case[
            case_id
        ]

        current_passed = _get_result_value(
            current_result,
            "passed"
        )

        shared_previous_statuses.append(
            previous_passed
        )

        shared_current_statuses.append(
            current_passed
        )

        if previous_passed and not current_passed:
            regressions.append(
                case_id
            )

        if not previous_passed and current_passed:
            improvements.append(
                case_id
            )

    shared_case_count = len(
        shared_current_statuses
    )

    if shared_case_count == 0:
        return FinancialRunComparison(
            shared_case_count=0,
            previous_pass_rate=None,
            current_pass_rate=None,
            pass_rate_change=None,
            regressions=[],
            improvements=[]
        )

    previous_pass_rate = round(
        (
            sum(shared_previous_statuses)
            / shared_case_count
        ) * 100,
        2
    )

    current_pass_rate = round(
        (
            sum(shared_current_statuses)
            / shared_case_count
        ) * 100,
        2
    )

    pass_rate_change = round(
        current_pass_rate
        - previous_pass_rate,
        2
    )

    return FinancialRunComparison(
        shared_case_count=shared_case_count,
        previous_pass_rate=previous_pass_rate,
        current_pass_rate=current_pass_rate,
        pass_rate_change=pass_rate_change,
        regressions=regressions,
        improvements=improvements
    )

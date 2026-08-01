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

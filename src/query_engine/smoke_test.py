from pathlib import Path

from src.database.build_database import (
    build_financial_database,
    create_financial_metrics_view,
    seed_demo_data
)
from src.query_engine.service import run_financial_query


def main() -> None:
    """
    Run one real end-to-end FinQuery AI request using Ollama.
    """
    database_path = Path(
        "data/financial_data.duckdb"
    )

    prompt_path = Path(
        "prompts/sql_generation_v1.yaml"
    )

    build_financial_database(database_path)
    seed_demo_data(database_path)
    create_financial_metrics_view(database_path)

    question = (
        "Which company had the highest "
        "revenue growth in 2024?"
    )

    print("Question:", question)
    print("Running FinQuery AI with Ollama...")
    print()

    response = run_financial_query(
        question=question,
        database_path=database_path,
        prompt_path=prompt_path
    )

    generation = response.generation_result

    print("Prompt version:", response.prompt_version)
    print("Confidence:", generation.confidence)
    print("Explanation:", generation.explanation)

    if generation.clarification_needed:
        print(
            "Clarification needed:",
            generation.clarification_question
        )
        return

    print()
    print("Generated SQL:")
    print(generation.sql)

    if response.execution is None:
        print("No query was executed.")
        return

    query_result = response.execution.query_result

    print()
    print("Rows returned:", query_result.row_count)
    print(
        "Execution time:",
        f"{query_result.execution_time_ms} ms"
    )
    print("Results:")

    for row in query_result.rows:
        print(row)


if __name__ == "__main__":
    main()
    
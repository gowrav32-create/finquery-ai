from dataclasses import dataclass
from pathlib import Path

from src.database.schema import (format_schema_for_prompt, get_database_schema)
from src.query_engine.generator import generate_financial_sql
from src.query_engine.models import SQLGenerationResult
from src.query_engine.pipeline import (ValidatedQueryExecution, run_validated_query)
from src.query_engine.prompt_config import (load_sql_prompt_config)

from src.query_engine.semantics import (validate_requested_metrics)

class FinancialSemanticError(ValueError):
    """
    Raised when generated SQL does not use the
    financial metric requested by the user.
    """

@dataclass
class FinancialQueryResponse:
    """
    Complete response returned by the FinQuery AI service.
    """

    question: str
    prompt_version: str
    generation_result: SQLGenerationResult
    execution: ValidatedQueryExecution | None


def run_financial_query(
    question: str,
    database_path: Path,
    prompt_path: Path
) -> FinancialQueryResponse:
    """
    Run the complete FinQuery AI workflow.

    Processing order:
    1. Validate the user's question.
    2. Load the versioned SQL-generation prompt.
    3. Extract and format the live database schema.
    4. Ask Ollama to generate structured SQL.
    5. Stop when clarification is required.
    6. Validate and execute generated SQL.
    7. Return generation and execution evidence.
    """
    if not question or not question.strip():
        raise ValueError(
            "Financial question must not be empty."
        )

    if not database_path.exists():
        raise FileNotFoundError(
            f"Database not found: {database_path}"
        )

    prompt_config = load_sql_prompt_config(
        prompt_path
    )

    database_schema = get_database_schema(
        database_path
    )

    schema_context = format_schema_for_prompt(
        database_schema
    )

    generation_result = generate_financial_sql(
        question=question.strip(),
        schema_context=schema_context,
        prompt_config=prompt_config
    )

    if generation_result.clarification_needed:
        return FinancialQueryResponse(
            question=question.strip(),
            prompt_version=prompt_config.version,
            generation_result=generation_result,
            execution=None
        )

    if generation_result.sql is None:
        raise ValueError(
            "The SQL generator returned no SQL and did not "
            "request clarification."
        )

    semantic_result = validate_requested_metrics(
            question=question.strip(),
            sql=generation_result.sql
        )
    
    if not semantic_result.is_valid:
        missing_metrics = ", ".join(
            semantic_result.missing_metrics
        )
    
        raise FinancialSemanticError(
            "Generated SQL does not reference "
            "the requested financial metric(s): "
            f"{missing_metrics}"
        )
    

    execution = run_validated_query(
        database_path=database_path,
        sql=generation_result.sql
    )

    return FinancialQueryResponse(
        question=question.strip(),
        prompt_version=prompt_config.version,
        generation_result=generation_result,
        execution=execution
    )

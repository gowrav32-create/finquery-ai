from ollama import chat

from src.query_engine.models import SQLGenerationResult
from src.query_engine.prompt_config import SQLPromptConfig


def generate_financial_sql(
    question: str,
    schema_context: str,
    prompt_config: SQLPromptConfig
) -> SQLGenerationResult:
    """
    Generate structured DuckDB SQL for a financial question.

    The model receives:
    - versioned system instructions
    - the real database schema
    - the user's financial question

    The response is validated against SQLGenerationResult.
    """
    user_message = (
        "DATABASE SCHEMA:\n"
        f"{schema_context}\n\n"
        "FINANCIAL QUESTION:\n"
        f"{question}\n\n"
        "Return only valid JSON matching the required schema."
    )

    response = chat(
        model=prompt_config.model,
        messages=[
            {
                "role": "system",
                "content": prompt_config.system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        format=SQLGenerationResult.model_json_schema(),
        options={
            "temperature": prompt_config.temperature
        }
    )

    return SQLGenerationResult.model_validate_json(
        response.message.content
    )

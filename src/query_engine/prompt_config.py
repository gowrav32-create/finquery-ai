from pathlib import Path

import yaml
from pydantic import BaseModel, Field, field_validator


class SQLPromptConfig(BaseModel):
    """
    Validated configuration for a versioned SQL-generation prompt.
    """

    version: str
    feature_name: str
    model: str

    temperature: float = Field(
        ge=0.0,
        le=1.0
    )

    system_prompt: str

    @field_validator(
        "version",
        "feature_name",
        "model",
        "system_prompt"
    )
    @classmethod
    def reject_empty_text(
        cls,
        value: str
    ) -> str:
        """
        Reject required text fields that are empty or only whitespace.
        """
        if not value.strip():
            raise ValueError(
                "Value must not be empty."
            )

        return value.strip()


def load_sql_prompt_config(
    prompt_path: Path
) -> SQLPromptConfig:
    """
    Load and validate a versioned SQL prompt configuration.
    """
    if not prompt_path.exists():
        raise FileNotFoundError(
            f"Prompt configuration not found: {prompt_path}"
        )

    with prompt_path.open(
        "r",
        encoding="utf-8"
    ) as file:
        prompt_data = yaml.safe_load(file)

    if not isinstance(prompt_data, dict):
        raise ValueError(
            "Prompt configuration must contain "
            "a YAML mapping."
        )

    return SQLPromptConfig(
        **prompt_data
    )

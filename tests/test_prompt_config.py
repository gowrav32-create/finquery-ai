from pathlib import Path

import pytest
from pydantic import ValidationError

from src.query_engine.prompt_config import (
    SQLPromptConfig,
    load_sql_prompt_config
)


def test_loads_valid_sql_prompt_config():
    prompt_path = Path(
        "prompts/sql_generation_v1.yaml"
    )

    config = load_sql_prompt_config(prompt_path)

    assert config.version == "v1"
    assert config.feature_name == "financial_sql_generation"
    assert config.model == "llama3.2:3b"
    assert config.temperature == 0.0
    assert "SQL RULES:" in config.system_prompt


def test_rejects_invalid_temperature():
    with pytest.raises(ValidationError):
        SQLPromptConfig(
            version="v1",
            feature_name="financial_sql_generation",
            model="llama3.2:3b",
            temperature=1.5,
            system_prompt="Generate safe financial SQL."
        )


def test_rejects_empty_system_prompt():
    with pytest.raises(ValidationError):
        SQLPromptConfig(
            version="v1",
            feature_name="financial_sql_generation",
            model="llama3.2:3b",
            temperature=0.0,
            system_prompt="   "
        )


def test_rejects_missing_prompt_file(
    tmp_path: Path
):
    missing_path = tmp_path / "missing.yaml"

    with pytest.raises(
        FileNotFoundError,
        match="Prompt configuration not found"
    ):
        load_sql_prompt_config(missing_path)
        
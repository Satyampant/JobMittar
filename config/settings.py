"""Pydantic-based configuration with validation and environment support."""

import os
import yaml
from pathlib import Path
from functools import lru_cache
from typing import Dict, Any, List
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings


class PromptConfig(BaseModel):
    """Prompt configuration with validation."""
    # Agent prompts (for decision-making)
    job_search_agent: str
    match_analysis_agent: str
    interview_prep_agent: str
    
    # Execution prompts (for actual LLM calls)
    resume_extraction: str
    job_match_analysis: str
    interview_questions_generation: str


class APIConfig(BaseModel):
    """API configuration with validation."""
    groq_model: str = Field(default="llama-3.3-70b-versatile")
    serp_engine: str = Field(default="google_jobs")
    max_tokens: int = Field(default=2500, ge=100, le=10000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class Settings(BaseSettings):
    """Main settings with environment variable support."""
    groq_api_key: str = Field(alias="GROQ_API_KEY")
    serpapi_api_key: str = Field(alias="SERPAPI_API_KEY")
    environment: str = Field(default="dev", pattern="^(dev|prod)$")
    prompts: PromptConfig
    api: APIConfig

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Load and cache settings from YAML + environment."""
    env = os.getenv("ENVIRONMENT", "dev")
    config_path = Path(__file__).parent / f"{env}.yaml"
    with open(config_path) as f:
        config_data = yaml.safe_load(f)
    return Settings(**config_data, groq_api_key=os.getenv("GROQ_API_KEY", ""), 
                    serpapi_api_key=os.getenv("SERPAPI_API_KEY", ""))
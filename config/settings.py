"""Centralized configuration for the research agent."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- API Keys ---
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    tavily_api_key: str = Field(default="", alias="TAVILY_API_KEY")

    # --- LangSmith ---
    langchain_tracing_v2: bool = Field(default=True, alias="LANGCHAIN_TRACING_V2")
    langchain_api_key: str = Field(default="", alias="LANGCHAIN_API_KEY")
    langchain_project: str = Field(default="masst-spy", alias="LANGCHAIN_PROJECT")

    # --- Model Configuration ---
    groq_model: str = "llama-3.3-70b-versatile"
    gemini_model: str = "gemini-2.0-flash"

    # --- Agent Parameters ---
    max_search_iterations: int = 5
    max_queries_per_iteration: int = 5
    search_rate_limit_seconds: float = 0.2
    min_confidence_threshold: float = 0.3
    max_facts_per_extraction: int = 30

    # --- Output Paths ---
    output_dir: str = "outputs"
    graphs_dir: str = "outputs/graphs"
    reports_dir: str = "outputs/reports"
    logs_dir: str = "outputs/logs"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()

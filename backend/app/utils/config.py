"""Configuration management using Pydantic settings."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str
    
    # LLM Provider
    llm_provider: str = "openai"
    llm_model: str = "gpt-4-turbo-preview"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    
    # Embeddings
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536
    
    # Application
    log_level: str = "INFO"
    environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    # Guardrails
    guardrail_strict_mode: bool = True
    max_conversation_history: int = 10
    
    # Analytics
    enable_metrics: bool = True
    metrics_retention_days: int = 90
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

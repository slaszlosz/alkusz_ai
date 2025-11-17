from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    # OpenAI
    openai_api_key: str

    # Database
    database_url: str = "sqlite+aiosqlite:///./alkusz_ai.db"

    # Chroma
    chroma_persist_directory: str = "./chroma_db"

    # Upload
    upload_dir: str = "./uploads"
    max_upload_size: int = 10485760  # 10MB

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

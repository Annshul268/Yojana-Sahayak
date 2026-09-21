"""Configuration management using Pydantic Settings."""

from typing import List, Optional, Union
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Application Information
    PROJECT_NAME: str = "Yojana Sahayak"
    VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api"

    # Server Settings
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 8501
    BACKEND_API_URL: str = "http://localhost:8000"

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:3000",
    ]

    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, str):
            return [i.strip() for i in self.CORS_ORIGINS.split(",") if i.strip()]
        return list(self.CORS_ORIGINS)

    # Infrastructure placeholders for future phases
    DATABASE_URL: Optional[str] = None
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_data"
    GROQ_API_KEY: Optional[str] = None
    DATAGOV_API_KEY: Optional[str] = None


settings = Settings()

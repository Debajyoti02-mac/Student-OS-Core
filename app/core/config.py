import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Student OS AI"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = os.getenv("LLM_model", "openai/gpt-oss-20b")
    GROQ_FALLBACK_MODEL: str = "openai/gpt-oss-120b"
    
    DB_PATH: str = "student_memory.db"
    
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", "8000"))
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/aspen_dental"
    TEST_DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/aspen_dental_test"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # JWT
    SECRET_KEY: str = "9b3S2RCSBmgUJ01Z65TROGWiIN0aUu795VNydVz37SA"
    JWT_SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT_NAME: Optional[str] = None
    LANGSMITH_TRACING: Optional[str] = None
    LANGSMITH_ENDPOINT: Optional[str] = None

    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_TEMPERATURE: float = 0.1

    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

    load_sample_data: bool = os.getenv("LOAD_SAMPLE_DATA", True)

    # # Email Configuration
    # EMAIL_HOST: Optional[str] = None
    # EMAIL_PORT: Optional[str] = None
    # EMAIL_USERNAME: Optional[str] = None
    # EMAIL_PASSWORD: Optional[str] = None
    # EMAIL_FROM_ADDRESS: Optional[str] = None
    # EMAIL_USE_TLS: bool = True
    # EMAIL_USE_SSL: bool = False

    # Sentry
    # SENTRY_DSN: Optional[str] = None

    # App
    APP_NAME: str = "Assist"
    DEBUG: bool = True
    VERSION: str = "1.0.0"

    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3001", "http://localhost:5173","http://localhost:3002", "http://localhost:3000"]


    class Config:
        env_file = ".env"

settings = Settings()

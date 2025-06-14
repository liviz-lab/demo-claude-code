from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "Demo FastAPI Application"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Authentication
    AUTH_HEADER_NAME: str = "X-API-Key"
    AUTH_HEADER_VALUE: str = "demo-api-key-123"

    # Database
    DATABASE_URL: str = "sqlite:///:memory:"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()

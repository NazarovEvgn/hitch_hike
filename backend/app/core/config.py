from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # Database
    database_url: str

    # Redis
    redis_url: str

    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # 2GIS API
    dgis_api_key: str

    # CORS
    allowed_origins: str = "http://localhost:9000,http://localhost:9001"

    # Environment
    environment: str = "development"

    @property
    def allowed_origins_list(self) -> list[str]:
        """Convert comma-separated origins to list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


settings = Settings()

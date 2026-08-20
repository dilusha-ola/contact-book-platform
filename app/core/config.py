from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=True)

    PROJECT_NAME: str = "Contact Book Platform"
    API_V1_STR: str = "/api/v1"
    PORT: int = 8005
    MONGODB_URL: str = ""
    DATABASE_NAME: str = "contact_book_db"
    API_KEY: str = ""
    ENVIRONMENT: str = "development"
    MUDRAID_JWKS_URL: str = "https://api.staging.mudraid.ai/.well-known/jwks.json"
    MUDRAID_PLATFORM_API_KEY: str = ""
    MUDRAID_PLATFORM_SECRET: str = ""
    MUDRAID_WEBHOOK_SECRET: str = ""
    MUDRAID_DELIVERY_DESTINATION_SECRET: str = ""

settings = Settings()

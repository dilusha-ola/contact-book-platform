from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=True)

    PROJECT_NAME: str = "Contact Book Platform"
    API_V1_STR: str = "/api/v1"
    PORT: int = 8000
    MONGODB_URL: str = ""
    DATABASE_NAME: str = "contact_book_db"
    API_KEY: str = ""
    ENVIRONMENT: str = "development"

settings = Settings()

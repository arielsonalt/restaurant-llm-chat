from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "restaurant-llm-chat"
    ENV: str = "local"

    DATABASE_URL: str
    REDIS_URL: str

    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_CLIENT_ID: str = "restaurant-api"

    JWT_SECRET: str
    JWT_ISSUER: str = "restaurant-llm-chat"
    ACCESS_TOKEN_TTL_MIN: int = 15
    REFRESH_TOKEN_TTL_DAYS: int = 14

    OPENAI_API_KEY: str | None = None
    LANGSMITH_API_KEY: str | None = None
    LANGSMITH_PROJECT: str = "restaurant-llm-chat"
    LANGCHAIN_TRACING_V2: str | None = None
    LANGCHAIN_PROJECT: str | None = None

settings = Settings()

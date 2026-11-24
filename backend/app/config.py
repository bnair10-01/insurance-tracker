from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = ""  # required, e.g. postgresql+asyncpg://user:pass@host:5433/db (set in .env)
    anthropic_api_key: str = ""
    claude_model: str = "claude-opus-5"

    jwt_secret_key: str = ""  # required: >= 32 random chars (openssl rand -hex 32)
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7

    uploads_dir: str = "./uploads"
    max_upload_mb: int = 20

    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]


settings = Settings()

if len(settings.jwt_secret_key) < 32:
    raise RuntimeError("JWT_SECRET_KEY must be set to a random string of at least 32 characters (openssl rand -hex 32).")
if not settings.database_url:
    raise RuntimeError("DATABASE_URL must be set (see .env.example).")

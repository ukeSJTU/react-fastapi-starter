from app.core.config import Environment, Settings


def build_settings(
    *,
    environment: Environment = Environment.TEST,
    database_url: str = "postgresql+psycopg://postgres:postgres@127.0.0.1:1/app",
) -> Settings:
    return Settings.model_validate(
        {
            "environment": environment,
            "log_level": "CRITICAL",
            "database_url": database_url,
            "cors_origins": ["http://localhost:5173"],
            "database_pool_size": 1,
            "database_max_overflow": 0,
            "database_pool_timeout_seconds": 1,
            "database_pool_recycle_seconds": 60,
        }
    )

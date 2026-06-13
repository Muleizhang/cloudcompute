from dataclasses import dataclass
import os


def _split_origins(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_name: str
    database_host: str
    database_port: int
    database_name: str
    database_user: str
    database_password: str
    database_sslmode: str
    cors_origins: list[str]


def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "GaussOps API"),
        database_host=os.getenv("DATABASE_HOST", "localhost"),
        database_port=int(os.getenv("DATABASE_PORT", "5432")),
        database_name=os.getenv("DATABASE_NAME", "postgres"),
        database_user=os.getenv("DATABASE_USER", "gaussdb"),
        database_password=os.getenv("DATABASE_PASSWORD", "Gauss@2026"),
        database_sslmode=os.getenv("DATABASE_SSLMODE", "disable"),
        cors_origins=_split_origins(
            os.getenv(
                "APP_CORS_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080",
            )
        ),
    )


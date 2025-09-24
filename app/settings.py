import enum
from pathlib import Path
from tempfile import gettempdir
from typing import Annotated, Any

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field, BeforeValidator, AnyUrl
from app.utils.credentials import DynamoDBCredentials

TEMP_DIR = Path(gettempdir())


def parse_cors(v: Any) -> list[str] | str:
    """
    Parse CORS origins from environment variable.

    Accepts either:
    - Comma-separated string: "http://localhost:3000,https://app.com"
    - List of strings: ["http://localhost:3000", "https://app.com"]

    :param v: Raw value from environment variable
    :return: List of origin strings or original value
    :raises ValueError: If value type is not supported
    """
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class LogLevel(str, enum.Enum):
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    host: str = "127.0.0.1"
    port: int = 8000
    environment: str = "dev"

    log_level: LogLevel = LogLevel.INFO

    @property
    def is_lambda(self) -> bool:
        """Check if running in AWS Lambda environment."""
        return (
            self.environment == "lambda"
            or "AWS_LAMBDA_FUNCTION_NAME" in __import__("os").environ
        )

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment in ["dev", "development"]

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = (
        []
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS]

    # Variables for DynamoDB
    dynamodb_endpoint_url: str = "http://localhost:8001"  # DynamoDB Local
    aws_region: str = "eu-west-1"

    # AWS Secrets Manager configuration
    dynamodb_secret_name: str = ""  # Secret name in AWS Secrets Manager (from env)
    use_secrets_manager: bool = True  # Enable/disable Secrets Manager for credentials

    @property
    def dynamodb_config(self) -> dict:
        """
        Get DynamoDB configuration for local development or AWS.

        :return: DynamoDB configuration dict.
        """

        credentials_manager = DynamoDBCredentials(self)
        return credentials_manager.get_config()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        env_file_encoding="utf-8",
    )


settings = Settings()

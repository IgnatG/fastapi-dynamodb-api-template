"""DynamoDB credentials management utility."""

import os
import logging
from typing import Dict
from app.utils.secrets import secrets_manager

logger = logging.getLogger(__name__)


class DynamoDBCredentials:
    """Manages DynamoDB credentials from various sources."""

    def __init__(self, settings):
        """Initialize with settings object."""
        self.settings = settings

    def get_config(self) -> Dict[str, str]:
        """
        Get DynamoDB configuration with credentials.

        :return: DynamoDB configuration dict
        """
        if self.settings.is_lambda:
            return self._get_lambda_config()
        return self._get_local_config()

    def _get_lambda_config(self) -> Dict[str, str]:
        """Get configuration for Lambda environment."""
        config = {"region_name": self.settings.aws_region}

        if self.settings.use_secrets_manager:
            # Try Secrets Manager first
            credentials = self._get_secrets_manager_credentials()
            if credentials and self._are_real_credentials(credentials):
                config.update(
                    {
                        "aws_access_key_id": credentials["aws_access_key_id"],
                        "aws_secret_access_key": credentials["aws_secret_access_key"],
                    }
                )
                if credentials.get("region"):
                    config["region_name"] = credentials["region"]
                logger.info("Using AWS Secrets Manager credentials for Lambda")
            else:
                logger.error(
                    "Failed to retrieve credentials from Secrets Manager in Lambda environment"
                )
                raise RuntimeError(
                    "AWS Secrets Manager credentials required for Lambda not available"
                )
        else:
            # When Secrets Manager is disabled, try environment variables or use IAM roles
            credentials = self._get_env_credentials()
            if credentials and self._are_real_credentials(credentials):
                config.update(
                    {
                        "aws_access_key_id": credentials["aws_access_key_id"],
                        "aws_secret_access_key": credentials["aws_secret_access_key"],
                    }
                )
                logger.info("Using environment variable credentials for Lambda")

        return config

    def _get_local_config(self) -> Dict[str, str]:
        """Get configuration for local development."""
        config = {
            "endpoint_url": self.settings.dynamodb_endpoint_url,
            "region_name": self.settings.aws_region,
        }

        # For local development, always use fake credentials for DynamoDB Local
        # No need to try Secrets Manager or environment variables locally
        credentials = self._get_default_credentials()

        config.update(
            {
                "aws_access_key_id": credentials["aws_access_key_id"],
                "aws_secret_access_key": credentials["aws_secret_access_key"],
            }
        )

        logger.info(
            "Using default fake credentials for local DynamoDB Local development"
        )
        return config

    def _get_secrets_manager_credentials(self) -> Dict[str, str]:
        """Get credentials from AWS Secrets Manager."""
        try:
            return secrets_manager.get_dynamodb_credentials(
                self.settings.dynamodb_secret_name
            )
        except Exception:
            logger.info("Secrets Manager not available")
            return {}

    def _get_env_credentials(self) -> Dict[str, str]:
        """Get credentials from environment variables."""

        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

        if access_key and secret_key:
            return {
                "aws_access_key_id": access_key,
                "aws_secret_access_key": secret_key,
                "region": self.settings.aws_region,
            }
        return {}

    def _get_default_credentials(self) -> Dict[str, str]:
        """Get default credentials for local development."""
        return {
            "aws_access_key_id": "fakeLocalKey",
            "aws_secret_access_key": "fakeLocalSecret",
            "region": self.settings.aws_region,
        }

    def _are_real_credentials(self, credentials: Dict[str, str]) -> bool:
        """Check if credentials are real (not default fake ones)."""
        return (
            credentials.get("aws_access_key_id") != "fakeLocalKey"
            and credentials.get("aws_secret_access_key") != "fakeLocalSecret"
            and bool(credentials.get("aws_access_key_id"))
            and bool(credentials.get("aws_secret_access_key"))
        )

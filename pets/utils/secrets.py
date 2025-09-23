"""AWS Secrets Manager utilities."""

import json
import logging
import boto3
from typing import Dict, Optional
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class SecretsManager:
    """AWS Secrets Manager client wrapper."""

    def __init__(self, region_name: str = "eu-west-1"):
        """
        Initialize Secrets Manager client.

        :param region_name: AWS region for Secrets Manager
        """
        self.region_name = region_name
        self._client = None

    def _get_client(self):
        """Get or create boto3 Secrets Manager client."""
        if self._client is None:
            try:
                self._client = boto3.client(
                    "secretsmanager", region_name=self.region_name
                )
            except Exception as e:
                logger.warning(f"Failed to create Secrets Manager client: {e}")
                return None
        return self._client

    def get_secret(self, secret_name: str) -> Optional[Dict]:
        """
        Retrieve a secret from AWS Secrets Manager.

        :param secret_name: Name of the secret to retrieve
        :return: Secret value as dictionary, or None if not found/accessible
        """
        client = self._get_client()
        if not client:
            logger.warning("Secrets Manager client not available")
            return None

        try:
            response = client.get_secret_value(SecretId=secret_name)

            # Parse the secret value (assuming JSON format)
            if "SecretString" in response:
                return json.loads(response["SecretString"])
            else:
                logger.warning(f"Secret {secret_name} is binary, expected JSON string")
                return None

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "DecryptionFailureException":
                logger.error(f"Secrets Manager can't decrypt the secret {secret_name}")
            elif error_code == "InternalServiceErrorException":
                logger.error(f"Internal service error retrieving secret {secret_name}")
            elif error_code == "InvalidParameterException":
                logger.error(f"Invalid parameter for secret {secret_name}")
            elif error_code == "InvalidRequestException":
                logger.error(f"Invalid request for secret {secret_name}")
            elif error_code == "ResourceNotFoundException":
                logger.info(
                    f"Secret {secret_name} not found - this is normal for local development"
                )
            else:
                logger.error(f"Unexpected error retrieving secret {secret_name}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse secret {secret_name} as JSON: {e}")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error retrieving secret {secret_name}: {e}")
            return None

    def get_dynamodb_credentials(
        self, secret_name: str = "pets/dynamodb"
    ) -> Dict[str, str]:
        """
        Get DynamoDB credentials from Secrets Manager.

        Expected secret format:
        {
            "aws_access_key_id": "AKIA...",
            "aws_secret_access_key": "...",
            "region": "eu-west-1"
        }

        :param secret_name: Name of the secret containing DynamoDB credentials
        :return: Dictionary with credentials, using defaults if secret not found
        """
        secret = self.get_secret(secret_name)

        if secret:
            logger.info(
                f"Successfully retrieved DynamoDB credentials from secret {secret_name}"
            )
            return {
                "aws_access_key_id": secret.get("aws_access_key_id", ""),
                "aws_secret_access_key": secret.get("aws_secret_access_key", ""),
                "region": secret.get("region", self.region_name),
            }
        else:
            logger.info(
                f"Using default DynamoDB credentials (secret {secret_name} not found)"
            )
            return {
                "aws_access_key_id": "fakeLocalKey",
                "aws_secret_access_key": "fakeLocalSecret",
                "region": self.region_name,
            }


# Global instance
secrets_manager = SecretsManager()

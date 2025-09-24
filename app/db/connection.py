"""DynamoDB connection utilities."""

import aioboto3
from app.settings import settings


class DynamoDBConnection:
    """DynamoDB connection manager."""

    def __init__(self):
        """Initialize DynamoDB connection."""
        self._session = None

    async def get_dynamodb_resource(self):
        """
        Get DynamoDB resource (async).

        :return: DynamoDB resource
        """
        if self._session is None:
            self._session = aioboto3.Session()

        return self._session.resource("dynamodb", **settings.dynamodb_config)

    async def get_dynamodb_client(self):
        """
        Get DynamoDB client (async).

        :return: DynamoDB client
        """
        if self._session is None:
            self._session = aioboto3.Session()

        return self._session.client("dynamodb", **settings.dynamodb_config)

    async def close(self):
        """Close DynamoDB connections."""
        self._session = None


# Global connection instance
dynamodb_connection = DynamoDBConnection()


async def get_dynamodb_resource():
    """
    Dependency function to get DynamoDB resource.

    :return: DynamoDB resource
    """
    return await dynamodb_connection.get_dynamodb_resource()


async def get_dynamodb_client():
    """
    Dependency function to get DynamoDB client.

    :return: DynamoDB client
    """
    return await dynamodb_connection.get_dynamodb_client()

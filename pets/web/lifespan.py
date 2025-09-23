from contextlib import asynccontextmanager
from typing import AsyncGenerator

import asyncio
from fastapi import FastAPI

from pets.db.connection import dynamodb_connection
from pets.settings import settings
from pets.db.dao.note_dao import note_dao
from pets.db.models.note import NoteCreate


async def _setup_db(app: FastAPI) -> None:
    """Setup DynamoDB connection."""
    # Test DynamoDB connection - don't store the resource yet
    async with await dynamodb_connection.get_dynamodb_resource() as dynamodb:
        # Just test the connection works
        pass

    # Store connection in app state for access in routes
    app.state.dynamodb_connection = dynamodb_connection

    # Create tables if needed (for local development) - don't block startup
    if settings.is_development:
        # Run table creation in background, don't wait
        asyncio.create_task(_create_tables_if_needed())


async def _create_tables_if_needed():
    """Create DynamoDB tables for local development."""

    # Wait a bit for DynamoDB Local to start
    await asyncio.sleep(2)

    try:
        client = await dynamodb_connection.get_dynamodb_client()
        async with client as dynamo_client:
            # List existing tables
            response = await dynamo_client.list_tables()
            existing_tables = response.get("TableNames", [])

            # Create notes table if it doesn't exist
            if "notes" not in existing_tables:
                await dynamo_client.create_table(
                    TableName="notes",
                    KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
                    AttributeDefinitions=[
                        {"AttributeName": "id", "AttributeType": "S"}
                    ],
                    BillingMode="PAY_PER_REQUEST",
                )
                print("✅ Created DynamoDB table: notes")

                # Wait for table to be active, then add sample data
                await asyncio.sleep(3)
                await _insert_sample_data()
    except Exception as e:
        # In development, table creation errors are not critical
        print(f"⚠️  Warning: Could not create DynamoDB tables: {e}")
        print("   This is normal if DynamoDB Local is still starting up.")


async def _insert_sample_data():
    """Insert sample data into the notes table."""
    try:

        # Sample notes to demonstrate functionality
        sample_notes = [
            NoteCreate(
                title="Welcome to DynamoDB",
                content="This is a sample note to demonstrate DynamoDB connectivity. You can create, read, update, and delete notes through the API.",
                tags=["sample", "welcome", "dynamodb"],
                completed=False,
            ),
            NoteCreate(
                title="API Testing Guide",
                content="Use the following endpoints to test the API:\n- GET /api/notes - List all notes\n- POST /api/notes - Create a new note\n- GET /api/notes/{id} - Get a specific note\n- PUT /api/notes/{id} - Update a note\n- DELETE /api/notes/{id} - Delete a note",
                tags=["api", "testing", "guide"],
                completed=False,
            ),
            NoteCreate(
                title="DynamoDB Connection Test",
                content="If you can see this note, the DynamoDB connection is working correctly! The application successfully connected to DynamoDB Local and created sample data.",
                tags=["connection", "test", "success"],
                completed=True,
            ),
        ]

        for note_data in sample_notes:
            await note_dao.create_note(note_data)

        print("✅ Inserted sample data into notes table")

    except Exception as e:
        print(f"⚠️  Warning: Could not insert sample data: {e}")


@asynccontextmanager
async def lifespan_setup(
    app: FastAPI,
) -> AsyncGenerator[None, None]:  # pragma: no cover
    """
    Actions to run on application startup.

    This function uses fastAPI app to store data
    in the state, such as db connection.

    :param app: the fastAPI application.
    :return: function that actually performs actions.
    """

    app.middleware_stack = None
    await _setup_db(app)
    app.middleware_stack = app.build_middleware_stack()

    yield

    # Cleanup on shutdown
    await dynamodb_connection.close()

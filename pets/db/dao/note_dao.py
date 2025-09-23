"""Note Data Access Object for DynamoDB operations."""

from datetime import datetime
from typing import List, Optional

from botocore.exceptions import ClientError
from pets.db.connection import dynamodb_connection
from pets.db.models.note import Note, NoteCreate, NoteUpdate


class NoteDAO:
    """Data Access Object for Note operations in DynamoDB."""

    TABLE_NAME = "notes"

    async def create_note(self, note_data: NoteCreate) -> Note:
        """
        Create a new note in DynamoDB.

        :param note_data: Note creation data
        :return: Created note
        """
        # Create note with auto-generated ID and timestamps
        note = Note(**note_data.dict())

        dynamodb = await dynamodb_connection.get_dynamodb_resource()
        async with dynamodb as resource:
            table = await resource.Table(self.TABLE_NAME)

            # Convert datetime objects to ISO strings for DynamoDB
            item = note.dict()
            item["created_at"] = note.created_at.isoformat()
            item["updated_at"] = note.updated_at.isoformat()

            await table.put_item(Item=item)

        return note

    async def get_note(self, note_id: str) -> Optional[Note]:
        """
        Get a note by ID.

        :param note_id: Note ID to retrieve
        :return: Note if found, None otherwise
        """
        dynamodb = await dynamodb_connection.get_dynamodb_resource()
        async with dynamodb as resource:
            table = await resource.Table(self.TABLE_NAME)

            try:
                response = await table.get_item(Key={"id": note_id})
                if "Item" in response:
                    item = response["Item"]
                    # Convert ISO strings back to datetime objects
                    item["created_at"] = datetime.fromisoformat(item["created_at"])
                    item["updated_at"] = datetime.fromisoformat(item["updated_at"])
                    return Note(**item)
                return None
            except ClientError:
                return None

    async def list_notes(self, limit: int = 50) -> List[Note]:
        """
        List all notes with optional limit.

        :param limit: Maximum number of notes to return
        :return: List of notes
        """
        dynamodb = await dynamodb_connection.get_dynamodb_resource()
        async with dynamodb as resource:
            table = await resource.Table(self.TABLE_NAME)

            try:
                response = await table.scan(Limit=limit)
                notes = []
                for item in response.get("Items", []):
                    # Convert ISO strings back to datetime objects
                    item["created_at"] = datetime.fromisoformat(item["created_at"])
                    item["updated_at"] = datetime.fromisoformat(item["updated_at"])
                    notes.append(Note(**item))

                # Sort by creation date (newest first)
                notes.sort(key=lambda x: x.created_at, reverse=True)
                return notes
            except ClientError:
                return []

    async def update_note(
        self, note_id: str, note_update: NoteUpdate
    ) -> Optional[Note]:
        """
        Update an existing note.

        :param note_id: Note ID to update
        :param note_update: Update data
        :return: Updated note if found and updated, None otherwise
        """
        # First, get the existing note
        existing_note = await self.get_note(note_id)
        if not existing_note:
            return None

        # Update only provided fields
        update_data = note_update.dict(exclude_unset=True)
        if not update_data:
            return existing_note

        update_data["updated_at"] = datetime.utcnow()

        dynamodb = await dynamodb_connection.get_dynamodb_resource()
        async with dynamodb as resource:
            table = await resource.Table(self.TABLE_NAME)

            # Build update expression
            update_expression = "SET "
            expression_attribute_values = {}
            expression_attribute_names = {}

            for key, value in update_data.items():
                attr_name = f"#{key}"
                attr_value = f":{key}"

                expression_attribute_names[attr_name] = key

                if isinstance(value, datetime):
                    expression_attribute_values[attr_value] = value.isoformat()
                else:
                    expression_attribute_values[attr_value] = value

                update_expression += f"{attr_name} = {attr_value}, "

            update_expression = update_expression.rstrip(", ")

            try:
                await table.update_item(
                    Key={"id": note_id},
                    UpdateExpression=update_expression,
                    ExpressionAttributeNames=expression_attribute_names,
                    ExpressionAttributeValues=expression_attribute_values,
                )

                # Return updated note
                return await self.get_note(note_id)
            except ClientError:
                return None

    async def delete_note(self, note_id: str) -> bool:
        """
        Delete a note by ID.

        :param note_id: Note ID to delete
        :return: True if deleted, False if not found
        """
        dynamodb = await dynamodb_connection.get_dynamodb_resource()
        async with dynamodb as resource:
            table = await resource.Table(self.TABLE_NAME)

            try:
                # Check if note exists first
                existing_note = await self.get_note(note_id)
                if not existing_note:
                    return False

                await table.delete_item(Key={"id": note_id})
                return True
            except ClientError:
                return False

    async def get_notes_by_tag(self, tag: str) -> List[Note]:
        """
        Get notes that contain a specific tag.

        :param tag: Tag to search for
        :return: List of notes with the tag
        """
        dynamodb = await dynamodb_connection.get_dynamodb_resource()
        async with dynamodb as resource:
            table = await resource.Table(self.TABLE_NAME)

            try:
                response = await table.scan(
                    FilterExpression="contains(tags, :tag)",
                    ExpressionAttributeValues={":tag": tag},
                )

                notes = []
                for item in response.get("Items", []):
                    # Convert ISO strings back to datetime objects
                    item["created_at"] = datetime.fromisoformat(item["created_at"])
                    item["updated_at"] = datetime.fromisoformat(item["updated_at"])
                    notes.append(Note(**item))

                # Sort by creation date (newest first)
                notes.sort(key=lambda x: x.created_at, reverse=True)
                return notes
            except ClientError:
                return []


# Global DAO instance
note_dao = NoteDAO()

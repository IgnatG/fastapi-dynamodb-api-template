"""Notes API views for DynamoDB demonstration."""

from typing import List

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from pets.db.dao.note_dao import note_dao
from pets.db.models.note import Note, NoteCreate, NoteUpdate


router = APIRouter()


@router.get("/", response_model=List[Note])
async def list_notes(limit: int = 50) -> List[Note]:
    """
    List all notes.

    :param limit: Maximum number of notes to return (default: 50)
    :return: List of notes
    """
    notes = await note_dao.list_notes(limit=limit)
    return notes


@router.post("/", response_model=Note, status_code=status.HTTP_201_CREATED)
async def create_note(note_data: NoteCreate) -> Note:
    """
    Create a new note.

    :param note_data: Note creation data
    :return: Created note
    """
    try:
        note = await note_dao.create_note(note_data)
        return note
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create note: {str(e)}",
        )


@router.get("/{note_id}", response_model=Note)
async def get_note(note_id: str) -> Note:
    """
    Get a specific note by ID.

    :param note_id: Note ID to retrieve
    :return: Note details
    """
    note = await note_dao.get_note(note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID '{note_id}' not found",
        )
    return note


@router.put("/{note_id}", response_model=Note)
async def update_note(note_id: str, note_update: NoteUpdate) -> Note:
    """
    Update an existing note.

    :param note_id: Note ID to update
    :param note_update: Update data
    :return: Updated note
    """
    note = await note_dao.update_note(note_id, note_update)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID '{note_id}' not found",
        )
    return note


@router.delete("/{note_id}")
async def delete_note(note_id: str) -> JSONResponse:
    """
    Delete a note.

    :param note_id: Note ID to delete
    :return: Success message
    """
    success = await note_dao.delete_note(note_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID '{note_id}' not found",
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Note '{note_id}' deleted successfully"},
    )


@router.get("/tags/{tag}", response_model=List[Note])
async def get_notes_by_tag(tag: str) -> List[Note]:
    """
    Get notes that contain a specific tag.

    :param tag: Tag to search for
    :return: List of notes with the tag
    """
    notes = await note_dao.get_notes_by_tag(tag)
    return notes


@router.get("/health/check")
async def health_check() -> JSONResponse:
    """
    Health check endpoint that tests DynamoDB connectivity.

    :return: Health status
    """
    try:
        # Try to list notes (this tests DynamoDB connection)
        notes = await note_dao.list_notes(limit=1)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "message": "DynamoDB connection is working",
                "notes_count": len(notes),
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "message": "DynamoDB connection failed",
            },
        )

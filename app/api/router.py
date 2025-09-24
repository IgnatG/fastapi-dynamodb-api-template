from fastapi.routing import APIRouter

from app.api import docs, notes

api_router = APIRouter()
api_router.include_router(docs.router)
api_router.include_router(notes.router, prefix="/notes", tags=["notes"])

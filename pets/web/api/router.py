from fastapi.routing import APIRouter

from pets.web.api import docs, test, monitoring, notes

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(docs.router)
api_router.include_router(test.router, prefix="/test", tags=["test"])
api_router.include_router(notes.router, prefix="/notes", tags=["notes"])

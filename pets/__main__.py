import uvicorn

from pets.settings import settings


def main() -> None:
    """Entrypoint of the application for local development."""
    # Use Uvicorn for local development - simpler and better for development
    uvicorn.run(
        "pets.web.application:get_app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.value.lower(),
        reload=True,
        factory=True,
        workers=1,
    )


if __name__ == "__main__":
    main()

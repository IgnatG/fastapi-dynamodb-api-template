from importlib import metadata
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from app.settings import settings
from app.api.router import api_router
from app.lifespan import lifespan_setup
from app.middleware import SecurityHeadersMiddleware

APP_ROOT = Path(__file__).parent


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="APP API",
        version=metadata.version("app"),
        lifespan=lifespan_setup,
        docs_url=None,
        redoc_url=None,
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    # Add security headers middleware to enhance security
    app.add_middleware(
        SecurityHeadersMiddleware,
        # Customize security headers as needed
        hsts_max_age=31536000,  # 1 year
        hsts_include_subdomains=True,
        x_frame_options="DENY",  # Prevent embedding in frames
        referrer_policy="strict-origin-when-cross-origin",
        # Custom CSP for API with Swagger UI support
        csp_policy=(
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "  # Swagger UI needs unsafe-inline
            "style-src 'self' 'unsafe-inline'; "  # Swagger UI needs unsafe-inline
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "form-action 'self'; "
            "base-uri 'self'; "
            "object-src 'none'"
        ),
    )

    # Set all CORS enabled origins
    if settings.all_cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.all_cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api/v1")
    # Adds static directory.
    # This directory is used to access swagger files.
    app.mount("/static", StaticFiles(directory=APP_ROOT / "static"), name="static")

    return app

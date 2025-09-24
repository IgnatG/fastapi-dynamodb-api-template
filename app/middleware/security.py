"""Security headers middleware for FastAPI."""

from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add comprehensive security headers to all HTTP responses.

    This middleware implements security best practices by adding headers that:
    - Prevent XSS attacks
    - Disable content sniffing
    - Control framing
    - Enforce HTTPS
    - Control referrer information
    - Limit permissions
    """

    def __init__(
        self,
        app,
        hsts_max_age: int = 31536000,  # 1 year
        hsts_include_subdomains: bool = True,
        hsts_preload: bool = True,
        content_type_nosniff: bool = True,
        x_frame_options: str = "DENY",  # DENY, SAMEORIGIN, or ALLOW-FROM
        x_xss_protection: str = "1; mode=block",
        referrer_policy: str = "strict-origin-when-cross-origin",
        permissions_policy: Optional[str] = None,
        csp_policy: Optional[str] = None,
        hide_server_header: bool = True,
    ):
        """
        Initialize security headers middleware.

        :param app: FastAPI application
        :param hsts_max_age: HSTS max age in seconds
        :param hsts_include_subdomains: Include subdomains in HSTS
        :param hsts_preload: Enable HSTS preload
        :param content_type_nosniff: Enable X-Content-Type-Options
        :param x_frame_options: X-Frame-Options value
        :param x_xss_protection: X-XSS-Protection value
        :param referrer_policy: Referrer-Policy value
        :param permissions_policy: Permissions-Policy value
        :param csp_policy: Content-Security-Policy value
        :param hide_server_header: Remove server identification header
        """
        super().__init__(app)
        self.hsts_max_age = hsts_max_age
        self.hsts_include_subdomains = hsts_include_subdomains
        self.hsts_preload = hsts_preload
        self.content_type_nosniff = content_type_nosniff
        self.x_frame_options = x_frame_options
        self.x_xss_protection = x_xss_protection
        self.referrer_policy = referrer_policy
        self.permissions_policy = (
            permissions_policy or self._default_permissions_policy()
        )
        self.csp_policy = csp_policy or self._default_csp_policy()
        self.hide_server_header = hide_server_header

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add security headers to the response.

        :param request: HTTP request
        :param call_next: Next middleware/handler
        :return: HTTP response with security headers
        """
        response = await call_next(request)

        # Add security headers
        self._add_security_headers(response, request)

        return response

    def _add_security_headers(self, response: Response, request: Request):
        """Add all security headers to the response."""

        # X-Content-Type-Options: Prevent MIME type sniffing
        if self.content_type_nosniff:
            response.headers["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options: Control framing to prevent clickjacking
        response.headers["X-Frame-Options"] = self.x_frame_options

        # X-XSS-Protection: Enable XSS filtering
        response.headers["X-XSS-Protection"] = self.x_xss_protection

        # Strict-Transport-Security: Enforce HTTPS
        if request.url.scheme == "https" or self._is_behind_proxy(request):
            hsts_value = f"max-age={self.hsts_max_age}"
            if self.hsts_include_subdomains:
                hsts_value += "; includeSubDomains"
            if self.hsts_preload:
                hsts_value += "; preload"
            response.headers["Strict-Transport-Security"] = hsts_value

        # Referrer-Policy: Control referrer information
        response.headers["Referrer-Policy"] = self.referrer_policy

        # Permissions-Policy: Control browser features
        if self.permissions_policy:
            response.headers["Permissions-Policy"] = self.permissions_policy

        # Content-Security-Policy: Prevent XSS and injection attacks
        if self.csp_policy:
            response.headers["Content-Security-Policy"] = self.csp_policy

        # Cross-Origin-Opener-Policy: Prevent cross-origin attacks
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"

        # Cross-Origin-Embedder-Policy: Control cross-origin embedding
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"

        # Cross-Origin-Resource-Policy: Control cross-origin resource sharing
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

        # Hide server information for security
        if self.hide_server_header:
            # Use del instead of pop for MutableHeaders
            if "Server" in response.headers:
                del response.headers["Server"]

    def _is_behind_proxy(self, request: Request) -> bool:
        """Check if request is behind a proxy/load balancer with HTTPS termination."""
        # Check common proxy headers
        forwarded_proto = request.headers.get("X-Forwarded-Proto")
        forwarded_ssl = request.headers.get("X-Forwarded-SSL")

        return (
            forwarded_proto == "https"
            or forwarded_ssl == "on"
            or request.headers.get("X-Forwarded-Port") == "443"
        )

    def _default_permissions_policy(self) -> str:
        """Default restrictive permissions policy."""
        return (
            "accelerometer=(), "
            "autoplay=(), "
            "camera=(), "
            "cross-origin-isolated=(), "
            "display-capture=(), "
            "encrypted-media=(), "
            "fullscreen=(), "
            "geolocation=(), "
            "gyroscope=(), "
            "magnetometer=(), "
            "microphone=(), "
            "midi=(), "
            "payment=(), "
            "picture-in-picture=(), "
            "publickey-credentials-get=(), "
            "screen-wake-lock=(), "
            "sync-xhr=(), "
            "usb=(), "
            "web-share=(), "
            "xr-spatial-tracking=()"
        )

    def _default_csp_policy(self) -> str:
        """Default Content Security Policy for API applications."""
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "  # Needed for Swagger UI
            "style-src 'self' 'unsafe-inline'; "  # Needed for Swagger UI
            "img-src 'self' data:; "  # Allow data URLs for images
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "  # Prevent framing
            "form-action 'self'; "
            "base-uri 'self'; "
            "object-src 'none'"  # Block plugins
        )

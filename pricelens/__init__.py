"""PriceLens application factory."""

from pathlib import Path
from typing import Mapping, Optional

from flask import Flask, jsonify, request

from pricelens.data import build_default_service
from pricelens.service import PriceComparisonService
from pricelens.web import web


def create_app(
    config: Optional[Mapping[str, object]] = None,
    service: Optional[PriceComparisonService] = None,
) -> Flask:
    """Create an isolated Flask application with injectable dependencies."""

    project_root = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        template_folder=str(project_root / "templates"),
        static_folder=str(project_root / "static"),
    )
    app.config.from_mapping(MAX_CONTENT_LENGTH=64 * 1024)

    if config:
        app.config.update(config)

    app.extensions["price_lens_service"] = service or build_default_service()
    app.register_blueprint(web)

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' blob:; object-src 'none'; "
            "base-uri 'self'; frame-ancestors 'none'; form-action 'self'",
        )
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(self), geolocation=(), microphone=(), payment=()",
        )
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")

        if request.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"

        return response

    @app.errorhandler(413)
    def request_too_large(_error):
        return jsonify({
            "error": {
                "code": "request_too_large",
                "message": "Request is too large.",
            }
        }), 413

    return app


__all__ = ["create_app"]

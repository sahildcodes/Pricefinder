"""Thin Flask transport adapter for the PriceLens service."""

from typing import Tuple

from flask import Blueprint, Response, current_app, jsonify, render_template, request

from pricelens.presenter import present_analysis
from pricelens.service import (
    IncompleteOfferDataError,
    PriceComparisonService,
    UnknownProductError,
)


MAX_QUERY_LENGTH = 200
web = Blueprint("web", __name__)


def error_response(code: str, message: str, status: int) -> Tuple[Response, int]:
    return jsonify({"error": {"code": code, "message": message}}), status


def get_service() -> PriceComparisonService:
    return current_app.extensions["price_lens_service"]


@web.get("/")
def index():
    return render_template("index.html")


@web.get("/health")
def health():
    return jsonify({"status": "ok", "service": "price-lens-mvp"})


@web.post("/api/v1/analyze")
def analyze():
    if not request.is_json:
        return error_response(
            "unsupported_media_type", "Expected a JSON request body.", 415
        )

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return error_response(
            "invalid_request", "Request body must be a JSON object.", 400
        )

    query = payload.get("query", "")
    if not isinstance(query, str):
        return error_response("invalid_query", "Query must be a string.", 400)

    query = query.strip()
    if not query:
        return error_response(
            "missing_query", "Enter a product hint to run the demo.", 400
        )
    if len(query) > MAX_QUERY_LENGTH:
        return error_response(
            "query_too_long",
            f"Query must be {MAX_QUERY_LENGTH} characters or fewer.",
            400,
        )

    try:
        result = get_service().analyze(query)
    except UnknownProductError:
        return error_response(
            "no_match",
            "No sample match. Try a hint containing bike, bicycle, shoe, sneaker, or running.",
            422,
        )
    except IncompleteOfferDataError:
        current_app.logger.exception("Fixture data is incomplete.")
        return error_response(
            "incomplete_fixture_data", "The sample data is temporarily unavailable.", 500
        )

    return jsonify(present_analysis(result))

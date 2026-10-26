from copy import deepcopy
import os

from flask import Flask, jsonify, render_template, request

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024

MAX_QUERY_LENGTH = 200

PRODUCTS = {
    "specialized-allez-comp-2024": {
        "id": "specialized-allez-comp-2024",
        "name": "Specialized Allez Comp 2024",
        "brand": "Specialized",
        "category": "Bike",
        "description": "A lightweight endurance road bike built for daily riding, fitness, and fast recreational miles.",
        "price": 2299,
        "currency": "USD",
        "confidence": 0.94,
        "attributes": {
            "frame_size": "54cm",
            "color": "Blue",
            "type": "Road bike",
            "wheel_size": "700c",
            "groupset": "Shimano 105"
        }
    },
    "nike-pegasus-41": {
        "id": "nike-pegasus-41",
        "name": "Nike Pegasus 41",
        "brand": "Nike",
        "category": "Running shoes",
        "description": "Responsive daily trainer with cushioned support and a versatile road-running feel.",
        "price": 160,
        "currency": "USD",
        "confidence": 0.91,
        "attributes": {
            "size": "10",
            "color": "Black / White",
            "type": "Road running shoe"
        }
    }
}


def best_match_for_query(query: str = ""):
    q = (query or "").lower()
    if "shoe" in q or "sneaker" in q or "running" in q:
        return PRODUCTS["nike-pegasus-41"]
    if "bike" in q or "road" in q or "bicycle" in q:
        return PRODUCTS["specialized-allez-comp-2024"]
    return None


def build_search_results(product):
    if product["id"] == "specialized-allez-comp-2024":
        online = [
            {
                "merchant": "Amazon",
                "price": 2199,
                "shipping": 19,
                "total": 2218,
                "link": "https://www.amazon.com/s?k=Specialized+Allez+Comp+2024",
                "availability": "In stock"
            },
            {
                "merchant": "Walmart",
                "price": 2349,
                "shipping": 0,
                "total": 2349,
                "link": "https://www.walmart.com/search?q=Specialized+Allez+Comp+2024",
                "availability": "Ships in 2 days"
            },
            {
                "merchant": "REI",
                "price": 2399,
                "shipping": 0,
                "total": 2399,
                "link": "https://www.rei.com/search?q=Specialized%20Allez%20Comp%202024",
                "availability": "Pickup available"
            }
        ]
        local = [
            {
                "store": "REI Downtown",
                "price": 2399,
                "distance_miles": 3.4,
                "address": "1200 Market St, San Francisco, CA",
                "link": "https://www.google.com/maps/search/REI+Downtown+San+Francisco",
                "inventory": "1 in stock"
            },
            {
                "store": "Bike Shop Collective",
                "price": 2299,
                "distance_miles": 6.1,
                "address": "842 Valencia St, San Francisco, CA",
                "link": "https://www.google.com/maps/search/Bike+Shop+Collective+San+Francisco",
                "inventory": "2 in stock"
            },
            {
                "store": "Pedal Works",
                "price": 2450,
                "distance_miles": 8.3,
                "address": "44 7th St, San Francisco, CA",
                "link": "https://www.google.com/maps/search/Pedal+Works+San+Francisco",
                "inventory": "3 in stock"
            }
        ]
    else:
        online = [
            {
                "merchant": "Nike",
                "price": 160,
                "shipping": 0,
                "total": 160,
                "link": "https://www.nike.com/w/mens-running-shoes-37i7ok",
                "availability": "In stock"
            },
            {
                "merchant": "Dick's Sporting Goods",
                "price": 174,
                "shipping": 0,
                "total": 174,
                "link": "https://www.dickssportinggoods.com/search/SearchDisplay?searchTerm=Pegasus%2041",
                "availability": "Pickup available"
            }
        ]
        local = [
            {
                "store": "Nike Store Union Square",
                "price": 170,
                "distance_miles": 2.3,
                "address": "130 Sutter St, San Francisco, CA",
                "link": "https://www.google.com/maps/search/Nike+Store+Union+Square+San+Francisco",
                "inventory": "4 in stock"
            },
            {
                "store": "Foot Locker",
                "price": 179,
                "distance_miles": 4.5,
                "address": "245 Stockton St, San Francisco, CA",
                "link": "https://www.google.com/maps/search/Foot+Locker+San+Francisco",
                "inventory": "2 in stock"
            }
        ]

    best_online = min(online, key=lambda x: x["total"])
    best_local = min(local, key=lambda x: x["price"])
    return {
        "online": online,
        "local": local,
        "best_online": best_online,
        "best_local": best_local,
        "cheapest_total": min([item["total"] for item in online] + [item["price"] for item in local]),
    }


@app.route("/")
def index():
    return render_template("index.html")


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
    return jsonify({"error": "Request is too large."}), 413


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "price-lens-mvp"})


@app.route("/api/analyze", methods=["POST"])
def analyze():
    if not request.is_json:
        return jsonify({"error": "Expected a JSON request body."}), 415

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    query = payload.get("query", "")
    if not isinstance(query, str):
        return jsonify({"error": "Query must be a string."}), 400

    query = query.strip()
    if not query:
        return jsonify({"error": "Enter a product hint to run the demo."}), 400
    if len(query) > MAX_QUERY_LENGTH:
        return jsonify({"error": f"Query must be {MAX_QUERY_LENGTH} characters or fewer."}), 400

    matched_product = best_match_for_query(query)
    if matched_product is None:
        return jsonify({
            "error": "No sample match. Try a hint containing bike, bicycle, shoe, sneaker, or running."
        }), 422

    product = deepcopy(matched_product)
    search_results = build_search_results(product)

    match_note = "Demo result selected from the product hint using a small keyword matcher. The image preview is not analyzed or uploaded."

    response = {
        "demo": {
            "enabled": True,
            "notice": "Sample products, prices, availability, distances, and recommendations. Not live merchant data."
        },
        "product": {
            "id": product["id"],
            "name": product["name"],
            "brand": product["brand"],
            "category": product["category"],
            "description": product["description"],
            "price": product["price"],
            "currency": product["currency"],
            "confidence": product["confidence"],
            "attributes": product["attributes"],
            "match_note": match_note
        },
        "results": {
            "online": search_results["online"],
            "local": search_results["local"],
            "best_online": search_results["best_online"],
            "best_local": search_results["best_local"],
            "cheapest_total": search_results["cheapest_total"]
        },
        "recommendation": {
            "title": "Best overall deal",
            "merchant": search_results["best_online"]["merchant"],
            "price": search_results["best_online"]["total"],
            "link": search_results["best_online"]["link"],
            "reason": "Lowest sample online total including the sample shipping amount."
        }
    }

    return jsonify(response)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    debug = os.environ.get("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}
    app.run(host=host, port=port, debug=debug)

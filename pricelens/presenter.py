"""Translate domain results into the public JSON representation."""

from typing import Dict, Union

from pricelens.domain import AnalysisResult, Offer, Product, SalesChannel


Money = Union[int, float]


def dollars(cents: int) -> Money:
    """Convert fixed-point cents to a JSON-friendly dollar amount."""

    return cents // 100 if cents % 100 == 0 else cents / 100


def present_product(product: Product) -> Dict[str, object]:
    return {
        "id": product.id,
        "name": product.name,
        "brand": product.brand,
        "category": product.category,
        "description": product.description,
        "price": dollars(product.price_cents),
        "currency": product.currency,
        "confidence": product.confidence_basis_points / 10_000,
        "attributes": dict(product.attributes),
        "match_note": (
            "Demo result selected from the product hint using a deterministic "
            "keyword-overlap matcher. The image preview is not analyzed or uploaded."
        ),
    }


def present_offer(offer: Offer) -> Dict[str, object]:
    if offer.channel is SalesChannel.ONLINE:
        return {
            "merchant": offer.seller,
            "price": dollars(offer.price_cents),
            "shipping": dollars(offer.shipping_cents),
            "total": dollars(offer.total_cents),
            "link": offer.link,
            "availability": offer.availability,
        }

    return {
        "store": offer.seller,
        "price": dollars(offer.price_cents),
        "distance_miles": offer.distance_miles,
        "address": offer.address,
        "link": offer.link,
        "inventory": offer.availability,
    }


def present_analysis(result: AnalysisResult) -> Dict[str, object]:
    online = [present_offer(offer) for offer in result.online_offers]
    local = [present_offer(offer) for offer in result.local_offers]
    best_online = present_offer(result.best_online)
    best_local = present_offer(result.best_local)

    return {
        "meta": {"api_version": "1", "data_source": "fixtures"},
        "demo": {
            "enabled": True,
            "notice": (
                "Sample products, prices, availability, distances, and "
                "recommendations. Not live merchant data."
            ),
        },
        "product": present_product(result.product),
        "results": {
            "online": online,
            "local": local,
            "best_online": best_online,
            "best_local": best_local,
        },
        "recommendation": {
            "title": "Best sample online deal",
            "merchant": result.best_online.seller,
            "price": dollars(result.best_online.total_cents),
            "link": result.best_online.link,
            "reason": "Lowest sample online total, including sample shipping.",
        },
    }

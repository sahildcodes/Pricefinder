"""Immutable fixture data and default dependency wiring for the demo."""

from types import MappingProxyType
from typing import Mapping, Tuple

from pricelens.catalog import ProductCatalog
from pricelens.domain import Offer, Product, SalesChannel
from pricelens.repository import InMemoryOfferRepository
from pricelens.service import PriceComparisonService


PRODUCTS: Tuple[Product, ...] = (
    Product(
        id="specialized-allez-comp-2024",
        name="Specialized Allez Comp 2024",
        brand="Specialized",
        category="Bike",
        description=(
            "A lightweight endurance road bike built for daily riding, fitness, "
            "and fast recreational miles."
        ),
        price_cents=229_900,
        currency="USD",
        confidence_basis_points=9_400,
        attributes=(
            ("frame_size", "54cm"),
            ("color", "Blue"),
            ("type", "Road bike"),
            ("wheel_size", "700c"),
            ("groupset", "Shimano 105"),
        ),
        keywords=frozenset({"bike", "bicycle", "cycling", "road"}),
    ),
    Product(
        id="nike-pegasus-41",
        name="Nike Pegasus 41",
        brand="Nike",
        category="Running shoes",
        description=(
            "Responsive daily trainer with cushioned support and a versatile "
            "road-running feel."
        ),
        price_cents=16_000,
        currency="USD",
        confidence_basis_points=9_100,
        attributes=(
            ("size", "10"),
            ("color", "Black / White"),
            ("type", "Road running shoe"),
        ),
        keywords=frozenset({"shoe", "shoes", "sneaker", "sneakers", "running"}),
    ),
)


_OFFERS_BY_PRODUCT = {
    "specialized-allez-comp-2024": (
        Offer(
            seller="Amazon",
            channel=SalesChannel.ONLINE,
            price_cents=219_900,
            shipping_cents=1_900,
            link="https://www.amazon.com/s?k=Specialized+Allez+Comp+2024",
            availability="Sample: in stock",
        ),
        Offer(
            seller="Walmart",
            channel=SalesChannel.ONLINE,
            price_cents=234_900,
            shipping_cents=0,
            link="https://www.walmart.com/search?q=Specialized+Allez+Comp+2024",
            availability="Sample: ships in 2 days",
        ),
        Offer(
            seller="REI",
            channel=SalesChannel.ONLINE,
            price_cents=239_900,
            shipping_cents=0,
            link="https://www.rei.com/search?q=Specialized%20Allez%20Comp%202024",
            availability="Sample: pickup available",
        ),
        Offer(
            seller="Demo Cycle Shop",
            channel=SalesChannel.LOCAL,
            price_cents=229_900,
            shipping_cents=0,
            link="https://www.google.com/maps/search/bike+shops+San+Francisco",
            availability="Sample: 2 in stock",
            distance_miles=3.4,
            address="San Francisco, CA (sample location)",
        ),
        Offer(
            seller="Demo Pedal Works",
            channel=SalesChannel.LOCAL,
            price_cents=245_000,
            shipping_cents=0,
            link="https://www.google.com/maps/search/bike+shops+San+Francisco",
            availability="Sample: 3 in stock",
            distance_miles=8.3,
            address="San Francisco, CA (sample location)",
        ),
    ),
    "nike-pegasus-41": (
        Offer(
            seller="Nike",
            channel=SalesChannel.ONLINE,
            price_cents=16_000,
            shipping_cents=0,
            link="https://www.nike.com/w/mens-running-shoes-37i7ok",
            availability="Sample: in stock",
        ),
        Offer(
            seller="Dick's Sporting Goods",
            channel=SalesChannel.ONLINE,
            price_cents=17_400,
            shipping_cents=0,
            link=(
                "https://www.dickssportinggoods.com/search/"
                "SearchDisplay?searchTerm=Pegasus%2041"
            ),
            availability="Sample: pickup available",
        ),
        Offer(
            seller="Demo Running Store",
            channel=SalesChannel.LOCAL,
            price_cents=17_000,
            shipping_cents=0,
            link="https://www.google.com/maps/search/running+stores+San+Francisco",
            availability="Sample: 4 in stock",
            distance_miles=2.3,
            address="San Francisco, CA (sample location)",
        ),
        Offer(
            seller="Demo Footwear Shop",
            channel=SalesChannel.LOCAL,
            price_cents=17_900,
            shipping_cents=0,
            link="https://www.google.com/maps/search/shoe+stores+San+Francisco",
            availability="Sample: 2 in stock",
            distance_miles=4.5,
            address="San Francisco, CA (sample location)",
        ),
    ),
}

OFFERS_BY_PRODUCT: Mapping[str, Tuple[Offer, ...]] = MappingProxyType(
    _OFFERS_BY_PRODUCT
)


def build_default_service() -> PriceComparisonService:
    """Compose production defaults while keeping adapters replaceable."""

    return PriceComparisonService(
        catalog=ProductCatalog(PRODUCTS),
        offers=InMemoryOfferRepository(OFFERS_BY_PRODUCT),
    )

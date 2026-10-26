"""Immutable domain types for products, offers, and comparisons."""

from dataclasses import dataclass
from enum import Enum
from typing import FrozenSet, Optional, Tuple


class SalesChannel(str, Enum):
    ONLINE = "online"
    LOCAL = "local"


@dataclass(frozen=True)
class Product:
    id: str
    name: str
    brand: str
    category: str
    description: str
    price_cents: int
    currency: str
    confidence_basis_points: int
    attributes: Tuple[Tuple[str, str], ...]
    keywords: FrozenSet[str]

    def __post_init__(self) -> None:
        if self.price_cents < 0:
            raise ValueError("Product price cannot be negative.")
        if not 0 <= self.confidence_basis_points <= 10_000:
            raise ValueError("Confidence must be between 0 and 10,000 basis points.")


@dataclass(frozen=True)
class Offer:
    seller: str
    channel: SalesChannel
    price_cents: int
    shipping_cents: int
    link: str
    availability: str
    distance_miles: Optional[float] = None
    address: Optional[str] = None

    def __post_init__(self) -> None:
        if self.price_cents < 0 or self.shipping_cents < 0:
            raise ValueError("Offer amounts cannot be negative.")
        if self.channel is SalesChannel.ONLINE and self.distance_miles is not None:
            raise ValueError("Online offers cannot have a local distance.")
        if self.channel is SalesChannel.LOCAL and self.distance_miles is None:
            raise ValueError("Local offers require a distance.")

    @property
    def total_cents(self) -> int:
        return self.price_cents + self.shipping_cents


@dataclass(frozen=True)
class AnalysisResult:
    product: Product
    online_offers: Tuple[Offer, ...]
    local_offers: Tuple[Offer, ...]
    best_online: Offer
    best_local: Offer

"""Offer repository boundaries and an in-memory adapter."""

from typing import Mapping, Protocol, Tuple

from pricelens.domain import Offer


class OfferRepository(Protocol):
    def for_product(self, product_id: str) -> Tuple[Offer, ...]:
        """Return all known offers for a product."""

        ...


class InMemoryOfferRepository:
    def __init__(self, offers_by_product: Mapping[str, Tuple[Offer, ...]]) -> None:
        self._offers_by_product = dict(offers_by_product)

    def for_product(self, product_id: str) -> Tuple[Offer, ...]:
        return self._offers_by_product.get(product_id, ())

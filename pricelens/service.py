"""Application service that orchestrates matching and offer comparison."""

from pricelens.catalog import ProductCatalog
from pricelens.domain import AnalysisResult, SalesChannel
from pricelens.repository import OfferRepository


class UnknownProductError(ValueError):
    """Raised when no catalog product matches a query."""


class IncompleteOfferDataError(RuntimeError):
    """Raised when a matched product lacks a required offer channel."""


class PriceComparisonService:
    def __init__(self, catalog: ProductCatalog, offers: OfferRepository) -> None:
        self._catalog = catalog
        self._offers = offers

    def analyze(self, query: str) -> AnalysisResult:
        product = self._catalog.match(query)
        if product is None:
            raise UnknownProductError(query)

        product_offers = self._offers.for_product(product.id)
        online = tuple(
            offer for offer in product_offers if offer.channel is SalesChannel.ONLINE
        )
        local = tuple(
            offer for offer in product_offers if offer.channel is SalesChannel.LOCAL
        )

        if not online or not local:
            raise IncompleteOfferDataError(product.id)

        # Seller name is a deterministic secondary key when prices tie.
        best_online = min(online, key=lambda offer: (offer.total_cents, offer.seller))
        best_local = min(local, key=lambda offer: (offer.price_cents, offer.seller))

        return AnalysisResult(
            product=product,
            online_offers=online,
            local_offers=local,
            best_online=best_online,
            best_local=best_local,
        )

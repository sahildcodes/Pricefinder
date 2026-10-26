"""Deterministic product matching over an in-memory catalog."""

import re
from typing import Iterable, Optional, Tuple

from pricelens.domain import Product


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def tokenize(value: str) -> frozenset:
    """Normalize a query into a case-insensitive set of alphanumeric tokens."""

    return frozenset(TOKEN_PATTERN.findall(value.lower()))


class ProductCatalog:
    """Rank products by keyword overlap with stable catalog-order tie breaking."""

    def __init__(self, products: Iterable[Product]) -> None:
        self._products: Tuple[Product, ...] = tuple(products)

    def match(self, query: str) -> Optional[Product]:
        query_tokens = tokenize(query)
        best_product: Optional[Product] = None
        best_score = 0

        for product in self._products:
            score = len(query_tokens.intersection(product.keywords))
            if score > best_score:
                best_product = product
                best_score = score

        return best_product

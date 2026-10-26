import unittest
from dataclasses import FrozenInstanceError

from pricelens.catalog import ProductCatalog, tokenize
from pricelens.data import PRODUCTS


class ProductCatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = ProductCatalog(PRODUCTS)

    def test_tokenizer_normalizes_case_and_punctuation(self):
        self.assertEqual(
            tokenize("Road-Running SHOE!!!"),
            frozenset({"road", "running", "shoe"}),
        )

    def test_more_keyword_overlap_wins(self):
        result = self.catalog.match("road running shoe")

        self.assertIsNotNone(result)
        self.assertEqual(result.id, "nike-pegasus-41")

    def test_catalog_order_breaks_equal_scores_deterministically(self):
        result = self.catalog.match("road running")

        self.assertIsNotNone(result)
        self.assertEqual(result.id, "specialized-allez-comp-2024")

    def test_unknown_query_returns_none(self):
        self.assertIsNone(self.catalog.match("laptop"))

    def test_domain_products_are_immutable(self):
        with self.assertRaises(FrozenInstanceError):
            PRODUCTS[0].name = "Changed"


if __name__ == "__main__":
    unittest.main()

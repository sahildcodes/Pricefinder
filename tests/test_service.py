import unittest

from pricelens.catalog import ProductCatalog
from pricelens.data import OFFERS_BY_PRODUCT, PRODUCTS, build_default_service
from pricelens.presenter import dollars, present_analysis
from pricelens.repository import InMemoryOfferRepository
from pricelens.service import IncompleteOfferDataError, UnknownProductError


class PriceComparisonServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = build_default_service()

    def test_best_online_offer_uses_landed_total(self):
        result = self.service.analyze("bike")

        self.assertEqual(result.best_online.seller, "Amazon")
        self.assertEqual(result.best_online.total_cents, 221_800)

    def test_best_local_offer_uses_listed_price(self):
        result = self.service.analyze("running shoe")

        self.assertEqual(result.best_local.seller, "Demo Running Store")
        self.assertEqual(result.best_local.price_cents, 17_000)

    def test_unknown_query_raises_domain_specific_error(self):
        with self.assertRaises(UnknownProductError):
            self.service.analyze("camera")

    def test_incomplete_repository_data_fails_closed(self):
        incomplete_service = type(self.service)(
            catalog=ProductCatalog(PRODUCTS),
            offers=InMemoryOfferRepository({PRODUCTS[0].id: ()}),
        )

        with self.assertRaises(IncompleteOfferDataError):
            incomplete_service.analyze("bike")

    def test_presenter_keeps_money_exact_until_boundary(self):
        self.assertEqual(dollars(12_345), 123.45)
        payload = present_analysis(self.service.analyze("shoe"))
        self.assertEqual(payload["results"]["best_online"]["total"], 160)

    def test_fixture_repository_is_complete_for_every_product(self):
        for product in PRODUCTS:
            with self.subTest(product=product.id):
                self.assertTrue(OFFERS_BY_PRODUCT[product.id])


if __name__ == "__main__":
    unittest.main()

import unittest

from pricelens import create_app
from pricelens.web import MAX_QUERY_LENGTH


class PriceLensWebTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()

    def post_query(self, query):
        return self.client.post("/api/v1/analyze", json={"query": query})

    def test_index_loads_with_security_headers(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"PriceLens", response.data)
        self.assertIn("default-src 'self'", response.headers["Content-Security-Policy"])
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")

    def test_health(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"service": "price-lens-mvp", "status": "ok"})

    def test_versioned_api_returns_sample_shoe(self):
        response = self.post_query("running shoe")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["meta"]["api_version"], "1")
        self.assertEqual(data["meta"]["data_source"], "fixtures")
        self.assertTrue(data["demo"]["enabled"])
        self.assertEqual(data["product"]["id"], "nike-pegasus-41")
        self.assertEqual(response.headers["Cache-Control"], "no-store")

    def test_bike_query_returns_sample_bike(self):
        response = self.post_query("road bicycle")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["product"]["id"], "specialized-allez-comp-2024"
        )

    def test_query_is_required(self):
        response = self.post_query("  ")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "missing_query")

    def test_query_must_be_a_string(self):
        response = self.post_query(["bike"])

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "invalid_query")

    def test_query_length_is_limited(self):
        response = self.post_query("x" * (MAX_QUERY_LENGTH + 1))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "query_too_long")

    def test_unknown_product_does_not_invent_a_match(self):
        response = self.post_query("laptop")

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.get_json()["error"]["code"], "no_match")

    def test_non_json_request_is_rejected(self):
        response = self.client.post("/api/v1/analyze", data={"query": "bike"})

        self.assertEqual(response.status_code, 415)
        self.assertEqual(
            response.get_json()["error"]["code"], "unsupported_media_type"
        )

    def test_request_body_size_is_limited(self):
        response = self.client.post(
            "/api/v1/analyze",
            data='{"query":"' + ("x" * 70_000) + '"}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.get_json()["error"]["code"], "request_too_large")


if __name__ == "__main__":
    unittest.main()

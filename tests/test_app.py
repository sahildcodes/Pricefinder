import unittest

from app import MAX_QUERY_LENGTH, app


class PriceLensAppTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

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

    def test_running_shoe_query_returns_sample_shoe(self):
        response = self.client.post("/api/analyze", json={"query": "running shoe"})
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["demo"]["enabled"])
        self.assertEqual(data["product"]["id"], "nike-pegasus-41")
        self.assertEqual(response.headers["Cache-Control"], "no-store")

    def test_bike_query_returns_sample_bike(self):
        response = self.client.post("/api/analyze", json={"query": "road bicycle"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["product"]["id"], "specialized-allez-comp-2024")

    def test_query_is_required(self):
        response = self.client.post("/api/analyze", json={"query": "  "})

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_query_must_be_a_string(self):
        response = self.client.post("/api/analyze", json={"query": ["bike"]})

        self.assertEqual(response.status_code, 400)

    def test_query_length_is_limited(self):
        response = self.client.post(
            "/api/analyze",
            json={"query": "x" * (MAX_QUERY_LENGTH + 1)},
        )

        self.assertEqual(response.status_code, 400)

    def test_unknown_product_does_not_invent_a_match(self):
        response = self.client.post("/api/analyze", json={"query": "laptop"})

        self.assertEqual(response.status_code, 422)
        self.assertIn("No sample match", response.get_json()["error"])

    def test_shoe_keyword_wins_when_query_also_contains_road(self):
        response = self.client.post("/api/analyze", json={"query": "road running shoe"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["product"]["id"], "nike-pegasus-41")

    def test_non_json_request_is_rejected(self):
        response = self.client.post("/api/analyze", data={"query": "bike"})

        self.assertEqual(response.status_code, 415)


if __name__ == "__main__":
    unittest.main()

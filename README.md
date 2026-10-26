# PriceLens MVP

PriceLens is a small Flask prototype that demonstrates a product-comparison interface. It includes an optional local image preview and a keyword-driven mock API for two sample products.

> **Demo only:** Product matches, confidence scores, prices, shipping, stock, distances, stores, and recommendations are sample data. PriceLens does not currently perform image recognition, contact merchants, scrape websites, or provide live shopping information.

## How it works

1. Select an optional image. The browser creates a local preview; the image is not uploaded.
2. Enter a supported product hint such as `bike`, `running shoe`, or `sneaker`.
3. The browser sends only the text hint to `POST /api/analyze`.
4. Flask uses a small keyword matcher and returns one of two hard-coded sample result sets.

## Privacy

- Selected images stay in the browser and are never sent to the server.
- The application has no database, user accounts, analytics, advertising, or tracking.
- The API does not intentionally retain queries. Hosting providers or reverse proxies may have their own request-logging policies.

## Local setup

Python 3.12 or newer is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000>.

Optional local environment variables are documented in `.env.example`. The app does not automatically load that file.

## API

`POST /api/analyze`

```json
{
  "query": "running shoe"
}
```

The request must be JSON, the query is required, and its maximum length is 200 characters. Responses contain a `demo` notice identifying the data as non-live sample content.

The mock matcher currently recognizes `bike`, `road`, `bicycle`, `shoe`, `sneaker`, and `running`. Other hints return a validation response instead of inventing a match.

`GET /health` returns basic service health information.

## Tests

```bash
python -m unittest discover -s tests -v
```

GitHub Actions runs the same tests on supported Python versions.

## Deployment

`python app.py` starts Flask's development server and is intended only for local use. For internet deployment, use a maintained production WSGI server and configure TLS, request logging, proxy limits, monitoring, and any platform-specific security controls.

Debug mode is disabled by default. Never enable it on an internet-accessible deployment.

## Data and trademark notice

Merchant names, product names, and trademarks belong to their respective owners. Their appearance in this prototype is for illustrative identification only and does not imply affiliation or endorsement. Sample prices and availability should not be used to make purchasing decisions.

## License

PriceLens is source-available under the PolyForm Noncommercial License 1.0.0. You may use, modify, and share it for permitted noncommercial purposes. Commercial use requires separate permission from the copyright holder. See `LICENSE` for the controlling terms.

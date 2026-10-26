# Architecture notes

## Goals

PriceLens is designed to demonstrate a trustworthy vertical slice rather than simulate production capabilities it does not have. The current system optimizes for:

1. Deterministic and explainable behavior.
2. Isolation between HTTP, application, domain, and data concerns.
3. Easy replacement of fixture adapters with real integrations.
4. Safe handling of untrusted browser input.
5. Fast tests without a network, filesystem fixture, or database.

Live merchant aggregation and computer vision are explicitly out of scope for this iteration.

## Boundaries

### Web adapter

`pricelens.web` owns HTTP-specific concerns: content type, request shape, length validation, status codes, and structured errors. It translates successful results through the presenter and contains no matching or price-comparison rules.

### Application service

`PriceComparisonService` implements the use case. It asks the catalog for a match, retrieves offers through a repository protocol, partitions offers by channel, and selects deterministic minima. Domain-specific exceptions communicate expected failure modes without importing Flask.

### Domain

`Product`, `Offer`, and `AnalysisResult` are immutable. Constructors reject invalid monetary values, confidence ranges, and channel/location combinations. Prices remain integer cents until the presentation boundary; confidence remains integer basis points until serialized.

### Adapters

`ProductCatalog` and `InMemoryOfferRepository` are replaceable adapters. A production catalog could use an inverted index or vector retrieval. A production offer repository could fan out to merchant APIs, normalize currency and shipping, cache results, and apply circuit breakers while preserving the service contract.

## Correctness invariants

- Monetary amounts cannot be negative.
- Online totals include shipping exactly once.
- Local offers require a distance; online offers cannot carry one.
- Confidence lies between 0 and 10,000 basis points.
- A comparison requires at least one online and one local offer.
- Unknown queries fail closed instead of inventing a product match.
- Equal scores and equal prices resolve deterministically.

## Complexity

Let `P` be catalog size, `Q` unique query tokens, `K` maximum keyword count per product, and `O` offers for the matched product.

| Operation | Time | Additional space |
|---|---:|---:|
| Tokenize query | `O(|query|)` | `O(Q)` |
| Rank catalog | `O(P × min(Q, K))` average | `O(1)` beyond tokens |
| Partition offers | `O(O)` | `O(O)` |
| Select minima | `O(O)` | `O(1)` |

The linear scan is preferable at fixture scale because it is transparent and testable. At larger scale, an inverted index reduces candidate retrieval toward `O(Q + matches)` before ranking.

## Failure behavior

Expected client errors use stable codes:

- `unsupported_media_type` — non-JSON input
- `invalid_request` / `invalid_query` — malformed data
- `missing_query` / `query_too_long` — validation failures
- `no_match` — no positive catalog score

Incomplete fixture data is treated as a server invariant failure and returns a generic `500` response while logging server-side detail. Internal identifiers are not exposed to the client.

## Security and privacy model

The primary untrusted boundary is the browser request. Controls include strict JSON parsing, bounded request/query sizes, same-origin defaults, no dynamic backend URLs, no file upload, no persistence, and a restrictive Content Security Policy.

The local image preview intentionally never leaves the browser. This removes an entire server-side attack surface: multipart parsing, file-format confusion, decompression bombs, temporary-file retention, and image metadata exposure.

## Production evolution

A production version would introduce capabilities in this order:

1. Replace fixtures with typed provider adapters behind `OfferRepository`.
2. Add timeouts, retries with jitter, circuit breakers, and cache freshness metadata.
3. Normalize currency, tax, shipping, and pickup costs before ranking.
4. Add persistence for historical prices and auditable recommendation inputs.
5. Add structured logs, traces, service-level indicators, and alerting.
6. Add authenticated saved searches only after threat modeling identity and privacy.
7. Add image recognition as a separate bounded component with file validation, decoding isolation, resource limits, and explicit retention policy.

This sequence preserves the current domain and service contracts while increasing operational complexity only when a capability requires it.

# Spec Delta: extra-source-adapter

## ADDED Requirements

### Requirement: ExtraSourceAdapter interface

The backend SHALL provide an `ExtraSourceAdapter` Protocol at `web/backend/app/services/extra_source/contract.py` declaring `get_meta() -> ExtraSourceMeta` and `fetch(params: dict[str, Any]) -> ExtraSourceResult`. This is the only sanctioned abstraction for consumer-side data sources that supply categories not covered by OpenStock's static inventory.

#### Scenario: Adapter implementing the Protocol

```gherkin
Given a concrete class `MyBigDealAdapter` defines methods `get_meta()` and `fetch(params)`
When `isinstance(MyBigDealAdapter(), ExtraSourceAdapter)` is evaluated with `@runtime_checkable`
Then the check returns True
```

#### Scenario: ExtraSourceMeta immutability

```gherkin
Given an `ExtraSourceMeta(name="big-deal", category="MARKET_BIG_DEAL", expires_on="2026-09-30")` instance
When an attempt is made to assign `meta.name = "other"`
Then `dataclasses.FrozenInstanceError` is raised
So that registered metadata cannot drift at runtime
```

### Requirement: Static category overlap rejection at registration

The `register_extra_source(adapter)` function in `web/backend/app/services/extra_source/registry.py` SHALL reject any adapter whose `get_meta().category` is in `OPENSTOCK_STATIC_CATEGORIES` (a `frozenset[str]` sourced from OpenStock's `DATA_CAPABILITY_SCOPE.md` 2026-07-02 snapshot, 70 entries). The function SHALL raise `ExtraSourceCategoryConflictError` and the application SHALL fail to start.

#### Scenario: Category overlaps OpenStock static inventory

```gherkin
Given `OPENSTOCK_STATIC_CATEGORIES` includes `"FUND_FLOW"`
And an adapter `BadAdapter` declares `get_meta().category == "FUND_FLOW"`
When `register_extra_source(BadAdapter())` is called during FastAPI lifespan startup
Then `ExtraSourceCategoryConflictError` is raised with a message naming both the adapter and the conflicting category
And the FastAPI application fails to start with `ExtraSourceCategoryConflictError` in the startup logs
So that no consumer-side shadow implementation of an OpenStock-managed category can ever run
```

#### Scenario: Category is unique and outside the static inventory

```gherkin
Given `OPENSTOCK_STATIC_CATEGORIES` does NOT include `"SOME_BESPOKE_CATEGORY"`
And an adapter `GoodAdapter` declares `get_meta().category == "SOME_BESPOSE_CATEGORY"` and `expires_on == None`
When `register_extra_source(GoodAdapter())` is called
Then no exception is raised
And the adapter is recorded in the internal registry keyed by `meta.name`
```

#### Scenario: Duplicate adapter name rejected

```gherkin
Given an adapter with `name == "big-deal"` is already registered
And a second adapter also declares `name == "big-deal"` but a different category
When `register_extra_source(second_adapter)` is called
Then `ExtraSourceNameConflictError` is raised
So that registry entries remain uniquely addressable for logging and CI attribution
```

### Requirement: TEMP_OVERRIDE expiration enforcement

Any adapter whose `get_meta().expires_on` is not None is classified as a `TEMP_OVERRIDE`. Such adapters SHALL pass static category registration (Layer 1) but SHALL be subject to CI-time expiration enforcement via `scripts/dev/check_temp_override_expiration.py`. The script SHALL exit non-zero if any TEMP_OVERRIDE's `expires_on` is on or before the current date.

#### Scenario: TEMP_OVERRIDE within expiration window

```gherkin
Given today is 2026-07-15
And a TEMP_OVERRIDE adapter has `expires_on == "2026-09-30"`
When `check_temp_override_expiration.py` runs in CI
Then the script exits 0
And stdout lists the adapter with remaining days
```

#### Scenario: Expired TEMP_OVERRIDE blocks CI

```gherkin
Given today is 2026-10-15
And a TEMP_OVERRIDE adapter has `expires_on == "2026-09-30"`
When `check_temp_override_expiration.py` runs in CI
Then the script exits 1
And stderr lists the expired adapter
And the CI pipeline blocks merge
So that temporary override cannot silently become permanent
```

#### Scenario: TEMP_OVERRIDE approaching expiration warns

```gherkin
Given today is 2026-09-25
And a TEMP_OVERRIDE adapter has `expires_on == "2026-09-30"`
When `check_temp_override_expiration.py` runs in CI
Then the script exits 0 (warn, not fail)
And stderr contains the adapter name and "expiring within 7 days"
```

### Requirement: No consumer-side fallback for OpenStock-managed categories

The backend SHALL NOT implement any fallback logic that, on OpenStock failure for a category inside `OPENSTOCK_STATIC_CATEGORIES`, retries against a consumer-side adapter. Layer 2 (multi-provider fallback within OpenStock) is out of scope for this proposal and is owned by the OpenStock repository.

#### Scenario: OpenStock error propagates without consumer-side retry

```gherkin
Given `OpenStockClient.fetch(category="NORTHBOUND_FLOW", ...)` raises `OpenStockClientError`
And no ExtraSource adapter is registered for `NORTHBOUND_FLOW` (because static overlap is rejected at registration)
When a route handler calls the data-source factory for `NORTHBOUND_FLOW`
Then the error propagates to the handler unchanged
And no second network call to an ExtraSource adapter is made
And the handler maps the error to `DATA_GATEWAY_UNAVAILABLE` in the response envelope
So that consumer-side fallback for OpenStock-managed categories is structurally impossible
```

### Requirement: ExtraSource adapter fetch error handling

When an ExtraSource adapter's `fetch(params)` raises an exception, the routing layer SHALL NOT retry against another adapter, fall back to OpenStockClient, or silently swallow the error. The exception SHALL be caught and mapped to the `DATA_GATEWAY_UNAVAILABLE` error envelope, with the adapter `name` and original exception type included in the error context for diagnosis.

#### Scenario: Adapter fetch exception maps to DATA_GATEWAY_UNAVAILABLE

```gherkin
Given an ExtraSource adapter named `"big-deal"` is registered with category `"MARKET_BIG_DEAL"`
And `"MARKET_BIG_DEAL"` is not in `OPENSTOCK_STATIC_CATEGORIES`
When a route handler requests `"MARKET_BIG_DEAL"` and `adapter.fetch(params)` raises `RuntimeError("upstream timeout")`
Then the routing layer catches the exception
And the handler returns an error envelope with code `DATA_GATEWAY_UNAVAILABLE`
And the error envelope context includes `adapter="big-deal"` and `cause="RuntimeError"`
And no second adapter call is attempted
And `OpenStockClient` is not contacted as a fallback
So that adapter failures fail loudly with enough context to diagnose, without triggering consumer-side cascading retries
```

#### Scenario: Adapter fetch returning partial data is the adapter's responsibility

```gherkin
Given an ExtraSource adapter `MyAdapter` returns `ExtraSourceResult(data={"rows": []}, provider_used="my-adapter")` on upstream outage
When the routing layer receives this result
Then the result is passed through to the handler unchanged
And the routing layer does not inspect `data` contents or second-guess adapter decisions
So that data completeness semantics belong to the adapter contract, not the routing layer
```

### Requirement: HybridDataSource routing precedence

`HybridDataSource` at `web/backend/app/services/data_source_factory/data_source_mode.py` SHALL route data requests in the following order: (1) categories in `OPENSTOCK_STATIC_CATEGORIES` always go to `OpenStockClient`; (2) categories registered with an ExtraSource adapter go to that adapter; (3) categories that match neither fall back to Mock (test only) or return `UNSUPPORTED_CATEGORY` in production mode. The "static category always uses OpenStock" invariant is enforced structurally by Layer 1 registration rejection (see `Static category overlap rejection at registration`), so no runtime routing scenario for static categories is needed.

#### Scenario: ExtraSource category routes to adapter

```gherkin
Given an ExtraSource adapter is registered with category `"SOME_BESPOKE_CATEGORY"` and `expires_on == None`
And `"SOME_BESPOKE_CATEGORY"` is not in `OPENSTOCK_STATIC_CATEGORIES`
When a route handler requests `"SOME_BESPOKE_CATEGORY"`
Then the routing layer invokes `adapter.fetch(params)`
And returns `ExtraSourceResult` to the handler
And `OpenStockClient` is not contacted
```

#### Scenario: Unknown category in test mode falls back to Mock

```gherkin
Given the application is running in test mode
And a category `"UNKNOWN_X"` is requested
And `"UNKNOWN_X"` is not in `OPENSTOCK_STATIC_CATEGORIES`
And no ExtraSource adapter is registered for `"UNKNOWN_X"`
When the routing decision is made
Then the routing layer falls back to `MockDataSource`
So that gaps in coverage are explicit and visible during testing
```

#### Scenario: Unknown category in production returns UNSUPPORTED_CATEGORY

```gherkin
Given the application is running in production mode
And a category `"UNKNOWN_X"` is requested
And `"UNKNOWN_X"` is not in `OPENSTOCK_STATIC_CATEGORIES`
And no ExtraSource adapter is registered for `"UNKNOWN_X"`
When the routing decision is made
Then the routing layer returns the `UNSUPPORTED_CATEGORY` error envelope
And no upstream provider is contacted
So that gaps in coverage fail loudly rather than silently degrading to mock data
```

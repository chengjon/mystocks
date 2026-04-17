## Context
Kronos inference runtime, GPU deployment, and operational ownership will live outside this repository. MyStocks only needs the contract required to call Kronos correctly and to expose Kronos-backed capabilities in a way that stays consistent with existing MyStocks API, response, and integration conventions.

The design must keep boundaries explicit:
- Kronos runtime is external.
- MyStocks only prepares requests, invokes Kronos, and normalizes results.
- MyStocks must not grow a shadow Kronos runtime or hidden operational logic.

## Goals / Non-Goals
- Goals:
  - Define a stable MyStocks-side contract for consuming external Kronos capabilities.
  - Keep client logic thin and adapter logic explicit.
  - Reuse MyStocks unified response and API integration conventions.
  - Define retries, timeouts, degradation flags, and cache usage for Kronos-backed flows.
  - Prevent MyStocks from drifting into primary inference ownership.
- Non-Goals:
  - Implement Kronos runtime internals in this repository.
  - Mirror Kronos-side queue, batch, or GPU policies as local code responsibilities.
  - Support MyStocks-hosted primary forecasting execution.

## Decisions

### Decision: Kronos is an external dependency for MyStocks
MyStocks will treat Kronos as an external inference dependency and will not host a primary Kronos runtime in API or worker processes.

Rationale:
- Preserves system boundaries.
- Prevents compute contention and hidden coupling.
- Matches the intended ownership split between repositories.

### Decision: MyStocks uses a thin client-and-adapter integration pattern
MyStocks will split Kronos integration into:
- a client layer for outbound HTTP requests, timeout, retry, and error parsing
- an API adapter layer for request normalization and response shaping for MyStocks consumers

Rationale:
- Keeps transport concerns separate from business-facing API behavior.
- Avoids duplicating Kronos integration rules across routes or services.

### Decision: HTTP is the required MyStocks integration surface
MyStocks will require HTTP compatibility from Kronos and will not depend on direct MCP invocation from MyStocks business code.

Rationale:
- Keeps MyStocks integration straightforward and framework-neutral.
- Allows Kronos to serve AI tools over MCP without forcing MyStocks to adopt MCP as a business-runtime dependency.

### Decision: MyStocks standardizes outbound OHLCV payloads
Before invoking Kronos, MyStocks will normalize outgoing requests to a canonical schema including:
- timestamp
- open
- high
- low
- close
- volume
- amount

MyStocks must also enforce agreed parameter bounds for:
- model selection
- lookback length
- pred_len
- sample_count

Rationale:
- Prevents malformed requests and duplicated schema drift between callers.

### Decision: MyStocks normalizes Kronos responses into MyStocks conventions
Kronos responses must be converted into MyStocks-compatible response envelopes and consumer-facing data structures.

Rationale:
- Preserves consistency with existing unified response rules.
- Prevents downstream pages or services from consuming Kronos-specific raw transport shapes directly.

### Decision: Retry and timeout behavior is owned by the MyStocks client layer
The client layer will own:
- timeout settings
- bounded retries
- error-code parsing

Initial behavior:
- up to 3 retries
- 100 ms retry interval
- explicit timeout handling

Rationale:
- Keeps outbound resilience concerns centralized.

### Decision: Fallback is heavily restricted
This repository may support only lightweight non-primary local fallback behavior if explicitly approved. Forecasting fallback is not a primary-path requirement for MyStocks.

Rationale:
- Prevents fallback from silently becoming a second primary inference engine.

## Integration Boundary

### Client layer responsibilities
- perform outbound HTTP calls to Kronos
- set timeout and retry behavior
- parse Kronos transport and error payloads
- expose normalized client errors upward

### Client layer non-responsibilities
- request business normalization
- result persistence policy
- scheduler or queue logic
- local forecasting execution

### API adapter responsibilities
- convert MyStocks request inputs into Kronos canonical OHLCV payloads
- invoke the client layer
- map Kronos responses into MyStocks response envelopes
- surface degradation, cache, and availability indicators to consumers

### API adapter non-responsibilities
- hosting inference state
- reimplementing Kronos-side runtime policy
- local primary inference execution

## Response Contract Alignment
MyStocks Kronos-backed endpoints must remain aligned with the repository's unified response format and should include consumer-visible state such as:
- `degraded`
- `cached`
- `request_id`
- `timestamp`

Error mapping should preserve MyStocks conventions while retaining Kronos-origin error meaning.

## Risks / Trade-offs
- If MyStocks embeds too much Kronos-specific transport detail in routes, integration logic will fragment.
  - Mitigation: enforce thin client and adapter separation.
- If fallback behavior is too permissive, MyStocks may accidentally become a second inference host.
  - Mitigation: keep fallback minimal and non-primary.
- If request schema is not centralized, AI/tool/backend callers will drift.
  - Mitigation: define one canonical outbound schema inside MyStocks integration layer.

## Migration Plan
1. Define the MyStocks-side Kronos request and response contract.
2. Add or refactor a dedicated external service client layer.
3. Add or refactor a dedicated Kronos API adapter layer for MyStocks endpoints.
4. Update frontend/backend consumers to use normalized Kronos-backed responses.
5. Verify no primary Kronos runtime responsibilities are added to MyStocks.

## Open Questions
- What exact Kronos HTTP endpoint paths and field names will be finalized by the Kronos repository?
- Should MyStocks expose one combined Kronos analysis endpoint or separate forecasting and encoding endpoints?
- Which degradation details should be visible directly to frontend consumers?

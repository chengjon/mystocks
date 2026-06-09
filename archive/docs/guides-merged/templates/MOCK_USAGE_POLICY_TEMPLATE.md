# Mock Usage Policy Template

> **Template Notice**:
> This file is a reusable template for projects that need a clear Mock data policy.
> Replace example field names, environment variables, and lifecycle labels with your own project terms before adopting it as a current rule document.

## Purpose

This document defines:

1. when Mock data is allowed
2. when Mock data is prohibited or restricted
3. how Mock and Real integration modes are classified
4. what evidence is required before a team may claim real-path verification

## Core Principles

- Mock exists to support development decoupling, test stability, demos, and isolated environments.
- Mock is not the default production success path.
- Real-path failures must be exposed explicitly instead of silently hidden behind Mock data.
- A team must distinguish between "Mock accepted" and "Real path verified".
- Historical Mock documentation must not be presented as current truth without re-verification.

## Lifecycle Classification

Use project-specific labels if needed, but keep the behavior explicit.

### `verified`

- Real API or real backend path is the primary data source.
- Silent Mock fallback is not allowed for the same user path.
- Loading, error, empty, and request-tracing states must be visible.

### `pending`

- The route or feature may remain reachable.
- Shell, loading, error, and empty states are allowed.
- Teams must not fabricate real contract fields.
- The unresolved blocker must be recorded in the project tracker, task report, or optimization list.

### `mock-only`

- Feature is intentionally limited to demo, isolated testing, or development-only use.
- Results from this mode must not be reported as real-path verification.

## Allowed Mock Scenarios

- Backend or upstream dependency is not ready, but frontend or UX work must continue.
- Unit, integration, or component tests need stable deterministic payloads.
- End-to-end automation needs an isolated sandbox mode.
- Demo, training, or workshop environments need predictable data.
- Readiness probes in explicit Mock mode may allow a controlled non-blocking fallback.

## Prohibited or Restricted Scenarios

- A `verified` page silently returns Mock data after a real request fails.
- Business code invents fields that the real contract does not define.
- Large inline fake datasets are scattered directly inside production business modules without clear labeling.
- Mock-based acceptance results are reported as real integration success.
- Historical metrics such as "100% documented" or "N mock endpoints" are presented as current truth without a fresh measurement date.

## Environment Flags

Use names that fit your stack. A common pattern is:

### Backend

```bash
USE_MOCK_DATA=true
USE_MOCK_DATA=false
```

### Frontend

```bash
VITE_USE_MOCK_DATA=true
VITE_USE_MOCK_DATA=false
```

Rules:

- Mock mode must be explicitly enabled.
- Default should normally be real mode for mainline verification and production-like workflows.
- Teams should make the active mode visible in logs, diagnostics, or developer UI.

## Verification Standard

A team may claim "real path verified" only when all of the following are true:

- Mock mode is disabled for the tested path.
- Requests reach the real backend or real external dependency chain.
- The feature consumes real response fields.
- Loading, error, empty, and tracing states are correctly wired.
- There is no silent Mock fallback on the same user path.
- Test or verification reports clearly state the execution mode.

If any item above is missing, the result should be described as partial, pending, mock-only, or isolated verification instead.

## Testing Guidance

### Unit and Integration Tests

- Prefer MSW, fixtures, fakes, or dedicated Mock helpers.
- Keep test Mock payloads centralized.
- Favor deterministic seeds or fixed payloads where reproducibility matters.

### E2E Tests

- Mock E2E proves shell stability, routing, or interaction behavior in isolation.
- Real E2E proves the live integration chain.
- Reports must state whether the run used Mock mode, Real mode, or a mixed controlled fallback mode.

## Implementation Guidance

### Centralize Mock Assets

- Keep Mock payloads in shared modules, fixtures, or test helpers.
- Avoid scattering inline fallback objects across production code.

### Keep Contract Shape Close to Real Data

- Mock structures should remain comparable to the real contract.
- Do not let Mock-only convenience fields leak into production assumptions.

### Prefer Explicit Fallback Surfaces

- If fallback is necessary, make it explicit in UI, logs, or diagnostics.
- Avoid hidden fallback logic that makes failures look like successes.

## Anti-Patterns

- `if request failed -> return mockRows` with no user-visible indication
- page-level fake fields that have no real contract equivalent
- direct imports of old page Mock files into current verified business flows
- documentation that mixes current rules with historical implementation notes without labeling them
- environment switching docs that do not match the current code or scripts

## Documentation Structure Recommendation

For projects that want a clean Mock policy, a practical document family is:

- `MOCK_USAGE_RULES.md`
  - current rules, lifecycle boundaries, allowed vs prohibited scenarios
- `MOCK_REAL_SWITCHING_GUIDE.md`
  - environment flags, readiness behavior, switching steps, verification method
- `INDEX.md`
  - current entrypoint and routing between current docs and historical docs
- `README_MOCK_DATA.md`
  - historical context only, if retention is necessary

## Adoption Checklist

- [ ] The project defines explicit lifecycle labels such as `verified`, `pending`, or equivalent.
- [ ] The project distinguishes Mock acceptance from real-path verification.
- [ ] Silent fallback behavior is either prohibited or tightly scoped and visible.
- [ ] Environment flags are documented and match the current code.
- [ ] Historical Mock docs are labeled as historical if still retained.
- [ ] Test reports state the execution mode clearly.

## Example Closeout Language

Use wording like:

- "Mock acceptance passed; real-path verification still pending."
- "Real-path verification passed with Mock mode disabled."
- "Feature remains pending because backend contract fields are not yet available."

Avoid wording like:

- "Passed" when the run depended on hidden Mock fallback
- "Real integration complete" when only Mock mode was exercised

## Related Project Inputs

When adapting this template, point readers to:

- your project-wide engineering standards
- your API or contract truth source
- your testing guide
- your environment switching guide

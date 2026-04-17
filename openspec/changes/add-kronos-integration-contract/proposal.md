# Change: Add Kronos Integration Contract

## Why
MyStocks needs to consume Kronos capabilities for K-line forecasting and tokenized K-line analysis, but Kronos runtime development and deployment will be owned by the external `/opt/claude/Kronos` project. This repository therefore needs a clear integration contract that defines only MyStocks-side responsibilities: what request shape MyStocks must send, what response shape it must accept, where the client boundary lives, how fallback and retries behave, and what is explicitly out of scope for this repository.

Without this contract, MyStocks risks hidden coupling to Kronos internals, duplicate request normalization logic, inconsistent frontend/backend behavior, and accidental leakage of primary inference responsibilities back into this codebase.

## Decision Summary
- MyStocks SHALL treat Kronos as an external inference dependency and SHALL NOT implement or host any primary Kronos runtime in this repository.
- MyStocks SHALL integrate with Kronos through a thin client-and-adapter boundary only.
- MyStocks SHALL support HTTP as the required business integration surface and SHALL remain compatible with a shared MCP-facing Kronos deployment without duplicating runtime logic locally.
- MyStocks SHALL standardize outgoing OHLCV requests and normalize incoming Kronos responses into MyStocks unified response conventions.
- Any local fallback in this repository SHALL be limited to lightweight non-primary scenarios and SHALL NOT become a secondary primary inference path.

## What Changes
- Add a new `kronos-integration-contract` capability spec focused only on MyStocks-side integration requirements.
- Define the canonical request requirements MyStocks must satisfy before calling Kronos.
- Define MyStocks-side timeout, retry, error mapping, degradation, and cache handling behavior.
- Define the integration boundary between the Kronos client layer and MyStocks API adapter layer.
- Explicitly prohibit primary Kronos inference, training, fine-tuning, and backtesting execution inside MyStocks runtime processes.

## Scope
This change covers only MyStocks-side contract and integration requirements for consuming Kronos as an external service.

Initial in-scope MyStocks-side capabilities:
- outbound request normalization for Kronos forecasting and encoding calls
- thin HTTP client integration
- MyStocks API adapter behavior for Kronos-backed endpoints
- error/degradation/caching behavior exposed to MyStocks consumers

## Non-Goals
- Implementing the Kronos runtime, scheduler, MCP server, or GPU service in this repository
- Defining Kronos internal batching, queueing, or GPU memory policies as MyStocks implementation work
- Running Kronos training, fine-tuning, or backtesting inside MyStocks
- Creating a local MyStocks-hosted primary inference engine

## Impact
- Affected specs:
  - `kronos-integration-contract` (new)
- Affected code areas:
  - MyStocks external service client layer
  - MyStocks API adapter layer for Kronos-backed endpoints
  - frontend/backend consumers that display Kronos-backed results or degradation states

## ADDED Requirements

### Requirement: Data Source Runtime Realtime Stream Pilot

The market-data capability SHALL support a phased realtime stream pilot from the data-source runtime only after REST/pull migration is stable.

#### Scenario: Runtime stream defines subscription lifecycle

- **WHEN** the realtime pilot is enabled
- **THEN** the data-source runtime SHALL expose a WebSocket stream with `subscribe`, `unsubscribe`, `snapshot`, `quote.update`, `heartbeat`, and `error` message types
- **AND** the stream contract SHALL define reconnect, stale quote, duplicate message, out-of-order message, slow consumer, market open, and market close behavior

#### Scenario: Main backend may proxy existing frontend channel

- **WHEN** frontend compatibility is required during the realtime pilot
- **THEN** the main backend MAY bridge or proxy the data-source runtime stream into the existing `/ws/events` consumer path
- **AND** the proxy SHALL preserve message freshness and error semantics required by the stream contract

#### Scenario: MCP is excluded from market-data hot paths

- **WHEN** realtime quote or high-volume market-data delivery is required
- **THEN** the system SHALL use WebSocket or REST according to workload type
- **AND** MCP SHALL NOT be used as the hot-path transport for realtime quotes, bulk K-line data, or bulk financial data

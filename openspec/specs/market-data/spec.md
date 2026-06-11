# market-data Specification

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

## Purpose
TBD - created by archiving change expand-akshare-data-sources. Update Purpose after archive.
## Requirements
### Requirement: Enhanced Market Data Coverage
The system SHALL provide enhanced market data coverage including market overview statistics, regional trading data, and sector performance analysis.

#### Scenario: Exchange Market Statistics
- **WHEN** user requests Shanghai/Shenzhen exchange statistics
- **THEN** system returns comprehensive market overview data
- **AND** includes circulation market value, P/E ratios, and trading volumes

#### Scenario: Regional Trading Analysis
- **WHEN** user requests regional trading performance
- **THEN** system returns province-level trading statistics
- **AND** includes market share and volume rankings

### Requirement: Real-time Quote Enhancements
The system SHALL provide enhanced real-time quote data including bid-ask spreads, volume analysis, and multi-market coverage.

#### Scenario: Enhanced Quote Data
- **WHEN** user requests stock bid-ask data
- **THEN** system returns five-level bid-ask prices and volumes
- **AND** includes real-time spread and volume analysis

#### Scenario: Multi-Market Coverage
- **WHEN** user requests quotes from different markets
- **THEN** system provides unified data format across all markets
- **AND** supports Shanghai, Shenzhen, Beijing, and new shares

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

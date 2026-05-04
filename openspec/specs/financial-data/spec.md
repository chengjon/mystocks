# financial-data Specification

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

## Purpose
TBD - created by archiving change expand-akshare-data-sources. Update Purpose after archive.
## Requirements
### Requirement: Profit Forecast Data Support
The system SHALL provide comprehensive profit forecast data from multiple sources including East Money and THS.

#### Scenario: East Money Profit Forecasts
- **WHEN** user requests profit forecasts from East Money
- **THEN** system returns analyst profit predictions
- **AND** includes EPS forecasts and target prices

#### Scenario: THS Profit Forecasts
- **WHEN** user requests profit forecasts from THS
- **THEN** system returns institutional profit predictions
- **AND** includes detailed forecast reports

### Requirement: Technical Indicator Support
The system SHALL provide comprehensive technical indicator calculations and analysis.

#### Scenario: Technical Indicator Calculation
- **WHEN** user requests technical indicators
- **THEN** system calculates and returns indicator values
- **AND** supports MACD, RSI, Bollinger Bands, and other indicators

### Requirement: Account Statistics Support
The system SHALL provide stock account statistics and monthly analysis data.

#### Scenario: Monthly Account Statistics
- **WHEN** user requests stock account monthly statistics
- **THEN** system returns comprehensive account analysis
- **AND** includes trading volume and participant statistics

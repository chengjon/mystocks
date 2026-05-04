# data-sources Specification

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

## Purpose
TBD - created by archiving change expand-akshare-data-sources. Update Purpose after archive.
## Requirements
### Requirement: Market Overview Data Support
The system SHALL provide comprehensive market overview data including Shanghai/Shenzhen exchange statistics, regional trading rankings, and sector transaction data.

#### Scenario: Shanghai Exchange Summary Data
- **WHEN** user requests Shanghai exchange market summary
- **THEN** system returns comprehensive statistics including circulation market value, average P/E ratio, and total listed companies
- **AND** data includes both main board and STAR market statistics

#### Scenario: Shenzhen Exchange Area Ranking
- **WHEN** user requests regional trading rankings for Shenzhen exchange
- **THEN** system returns trading volume and market share data by province
- **AND** data covers multiple time periods (current month, current year)

### Requirement: Individual Stock Deep Information
The system SHALL provide detailed individual stock information including business introductions, constituent analysis, investor ratings, and news data.

#### Scenario: Business Introduction Data
- **WHEN** user requests stock business introduction from THS
- **THEN** system returns detailed business scope and operations data
- **AND** includes main business composition analysis

#### Scenario: Stock News and Ratings
- **WHEN** user requests individual stock news
- **THEN** system returns latest news articles and investor ratings
- **AND** includes thousand stock thousand evaluation data

### Requirement: Capital Flow Data Support
The system SHALL provide comprehensive capital flow data including SH-HK-SZ Connect funds flow, detailed capital flow analysis, and chip distribution data.

#### Scenario: SH-HK-SZ Connect Fund Flow
- **WHEN** user requests northbound/southbound fund flow data
- **THEN** system returns daily and historical fund flow statistics
- **AND** includes both summary and detailed flow data

#### Scenario: Chip Distribution Analysis
- **WHEN** user requests stock chip distribution
- **THEN** system returns cost distribution and concentration analysis
- **AND** includes institutional holding distribution data

## ADDED Requirements

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


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

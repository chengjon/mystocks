## ADDED Requirements

### Requirement: Provider Implementation Boundary

The data-sources capability SHALL distinguish external provider implementation from MyStocks business consumption and SHALL route new external provider work to OpenStock.

#### Scenario: New provider work is rejected inside MyStocks

- **GIVEN** a change proposes new or expanded direct use of external provider SDKs such as AkShare, Baostock, Tushare, efinance, easyquotation, TDX, or similar upstream acquisition libraries
- **WHEN** the proposed change is inside `mystocks_spec`
- **THEN** the change SHALL be rejected or reframed as a compatibility/consumer change unless explicitly authorized as a temporary migration exception
- **AND** the provider implementation SHALL be proposed in OpenStock instead.

#### Scenario: Existing MyStocks provider-shaped surfaces are migration inventory

- **GIVEN** existing MyStocks files or routes expose provider-shaped behavior, including `/api/akshare/market/**`, `web/backend/app/services/adapters_split/**`, `src/adapters/**`, or provider portions of `src/data_sources/**`
- **WHEN** they are touched during B4.013 runtime mainline work
- **THEN** they SHALL be treated as compatibility or migration inventory
- **AND** they SHALL NOT be expanded as canonical provider architecture
- **AND** any retirement, proxying, or replacement SHALL require separate scoped authorization and route smoke evidence.

#### Scenario: Local persisted read models remain in MyStocks

- **GIVEN** a data-source-related MyStocks component reads from PostgreSQL, TDengine, or another local persisted application store
- **WHEN** the component does not perform external provider acquisition or provider runtime orchestration
- **THEN** it MAY remain in MyStocks as a business/application read model
- **AND** it SHALL be classified separately from external provider adapter code before any cleanup or migration decision.

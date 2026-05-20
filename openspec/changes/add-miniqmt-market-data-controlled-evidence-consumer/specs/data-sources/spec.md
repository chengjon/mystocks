## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: miniQMT Market Data Platform Adapter Boundary

The system SHALL define miniQMT Market Data Platform consumption as a read-only dataset release adapter boundary, separate from miniQMT broker execution runtime.

#### Scenario: Adapter uses the Market Data Platform namespace

- **GIVEN** MyStocks integrates a miniQMT market-data source
- **WHEN** the source retrieves dataset metadata or release artifacts
- **THEN** it SHALL use the miniQMT Market Data Platform release contract, such as `/api/v1/market-data/*` or an equivalent promotion bundle
- **AND** it SHALL not treat `/api/v1/qmt/market-data/*` as the canonical market-data store
- **AND** it SHALL not reuse broker execution submission or reconciliation APIs for dataset evidence.

#### Scenario: Adapter is read-only

- **GIVEN** the miniQMT market-data adapter consumes a release artifact
- **WHEN** the adapter returns rows or metadata to MyStocks services
- **THEN** it SHALL expose data for dry-run rehearsal and evidence generation only
- **AND** it SHALL not directly persist formal MyStocks business data
- **AND** it SHALL leave formal PostgreSQL, TDengine, and Redis writes under MyStocks import-control services.

#### Scenario: Adapter supports offline fixture mode

- **GIVEN** miniQMT HTTP services are unavailable during development or CI
- **WHEN** the miniQMT adapter is configured with a local bundle or fixture
- **THEN** it SHALL load manifest and artifact content from the bundle
- **AND** it SHALL apply the same identity and artifact hash checks as HTTP mode
- **AND** the bundle SHALL require a `bundle_manifest.json` that resolves the rest of the upstream promotion-bundle files
- **AND** the bundle layout SHALL remain compatible with the upstream promotion bundle workflow instead of an ad hoc folder shape.

#### Scenario: Adapter follows upstream promotion bundle layout

- **GIVEN** a miniQMT promotion bundle is prepared for MyStocks
- **WHEN** the adapter loads bundle mode
- **THEN** it SHALL expect the upstream promotion bundle file set, including `README.md`, `promotion_requirements.json`, `promotion_gaps.json`, `mystocks_dry_run.template.evidence.json`, `mystocks_dry_run.request.json`, `mystocks_dry_run.validator.txt`, `quantix_regression.template.evidence.json`, `quantix_regression.request.json`, `quantix_regression.validator.txt`, `authoritative_approval.request.json`, `authoritative_approval.apply.txt`, `promotion_targets.json`, `promotion_bundle.apply.txt`, `promotion_bundle.validate.txt`, and `bundle_manifest.json`
- **AND** it SHALL fail closed if the manifest is missing or the bundle tree is incompatible.

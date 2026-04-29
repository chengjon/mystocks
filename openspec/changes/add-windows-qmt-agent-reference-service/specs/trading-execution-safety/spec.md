## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: Windows qmt Reference Service Fails Closed
The project SHALL keep the Windows `qmt` reference-service boundary fail-closed until live broker
evidence is explicitly available.

#### Scenario: Reference service runs in mock mode
- **WHEN** the Ubuntu / WSL trading runtime receives a receipt or result produced by the Windows
  reference service in `mock` mode
- **THEN** that evidence SHALL remain non-production by classification
- **AND** it SHALL NOT by itself justify broker acknowledgement, broker execution truth, or
  production-eligible status

#### Scenario: Live provider is unavailable or unconfigured
- **WHEN** the Windows `qmt` reference service is configured for a live `miniQMT` provider but the
  provider is unavailable, misconfigured, or missing required dependencies
- **THEN** the boundary SHALL preserve explicit failure evidence
- **AND** it SHALL NOT silently fall back to Tongdaxin or synthetic broker-facing outcomes

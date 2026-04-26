## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: Q2 Architecture Closure Program
The project SHALL treat the 2026 Q2 phase evaluation as a cross-cutting closure program rather than as an unstructured collection of optimization suggestions.

#### Scenario: Q2 closure scope is defined
- **WHEN** a Q2 architecture or quality closure wave is proposed
- **THEN** the scope SHALL identify the canonical truths it intends to settle
- **AND** it SHALL identify the closure evidence required before the wave is marked complete

### Requirement: Sequential Closure Gate For Cross-Cutting Waves
The project SHALL execute cross-cutting architecture closure waves through a sequential gate unless the canonical truths and write scopes are already stabilized.

#### Scenario: Cross-cutting wave is planned
- **WHEN** a change affects overlapping architecture truth sources, governance rules, or shared composition entrypoints
- **THEN** the default execution model SHALL be single-CLI sequential delivery
- **AND** parallel multi-CLI execution SHALL require an explicit low-coupling justification

### Requirement: Backend Composition Source Of Truth
The backend SHALL define one canonical source-of-truth for application composition and startup assembly.

#### Scenario: Composition path is canonicalized
- **WHEN** multiple backend assembly entrypoints exist or appear to overlap
- **THEN** one path SHALL be declared canonical for application composition
- **AND** non-canonical paths SHALL be classified as compatibility-retained, delegated, or retirement-targeted

### Requirement: Realtime Delivery Truth Registry
The system SHALL maintain a realtime delivery truth registry for active push-driven backend paths.

#### Scenario: Realtime path is added or changed
- **WHEN** a websocket, socket manager, streaming service, or equivalent realtime delivery path is introduced or materially changed
- **THEN** the registry SHALL record its owner, canonical transport role, fallback policy, and consumer scope
- **AND** it SHALL identify whether the path is canonical, compatibility-retained, or cleanup-ready
- **AND** the registry SHALL be consistent with the canonical realtime transport selection policy defined for API integration

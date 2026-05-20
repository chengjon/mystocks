> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## ADDED Requirements

### Requirement: Backend Core Import Compatibility Governance

The project SHALL preserve import compatibility when splitting backend Core modules.

#### Scenario: Core module is moved

- **GIVEN** a Core module path is imported by backend code, tests, or scripts
- **WHEN** the module implementation is moved to a new package or file
- **THEN** the old import path SHALL remain available through an approved re-export or thin wrapper
- **AND** the wrapper SHALL have a documented retirement condition
- **AND** lifecycle-owned Core modules SHALL identify their coordination point with dependency lifecycle governance before movement

#### Scenario: Logger internals are reorganized

- **GIVEN** logging internals are moved under `app.core.logging`
- **WHEN** caller imports are reviewed
- **THEN** `app.core.logger` SHALL remain the canonical caller entrypoint
- **AND** callers SHALL NOT be required to import internal logging implementation modules
- **AND** import smoke SHALL cover `from app.core.logger import logger`

### Requirement: Backend Core Split Batch Governance

The project SHALL split Core modules in small independently verifiable batches.

#### Scenario: Core split batch is prepared

- **GIVEN** a batch moves Core files or changes Core imports
- **WHEN** the batch is prepared for implementation
- **THEN** it SHALL include import inventory, compatibility strategy, import smoke, runtime smoke, and rollback notes
- **AND** broad database, cache, security, socketio, or logger moves SHALL be blocked until lifecycle ownership and monkeypatch paths are classified

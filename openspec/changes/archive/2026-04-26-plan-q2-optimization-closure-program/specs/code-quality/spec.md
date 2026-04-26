## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: Closure Wave Evidence Contract
The project SHALL require explicit evidence artifacts before a Q2 closure wave is marked complete.

#### Scenario: Closure wave claims completion
- **WHEN** a cross-cutting architecture, safety, or governance wave is marked complete
- **THEN** the completion record SHALL identify the verified truth source, affected scope, executed validations, and unresolved follow-up items
- **AND** it SHALL distinguish delivered closure from deferred backlog items

#### Scenario: Closure evidence is reviewed
- **WHEN** reviewers inspect a closure wave
- **THEN** they SHALL be able to identify what was verified in code, what was verified in docs, and what remains assumption or follow-up
- **AND** the evidence SHALL be sufficient to reject narrative-only completion claims

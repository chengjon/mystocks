# trading-execution-safety Specification

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

## ADDED Requirements

### Requirement: Windows qmt Service-Ready Evidence Gate
The project SHALL require dedicated readiness evidence before a separately deployed Windows `qmt` /
`miniQMT` service is described as ready for first formal cross-project acceptance.

#### Scenario: Operator or documentation claims Windows qmt service is ready
- **WHEN** an operator-facing workflow, guide, or status artifact describes a Windows `qmt` /
  `miniQMT` service as ready for first formal acceptance from `WSL 上的 Ubuntu 24.04.4 LTS`
- **THEN** that claim SHALL be backed by a dedicated read-only readiness artifact
- **AND** a successful contract acceptance run alone SHALL not be treated as equivalent service-ready
  proof

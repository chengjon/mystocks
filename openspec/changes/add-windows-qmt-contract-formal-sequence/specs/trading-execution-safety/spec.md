# trading-execution-safety Specification

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

## MODIFIED Requirements

### Requirement: Trading Domain Safety Contract
The project SHALL define an explicit safety contract for trading execution paths before they are
described as production-grade.

#### Scenario: Trading path is classified
- **WHEN** a trading execution path is documented or exposed
- **THEN** it SHALL be classified as simulated, experimental, or production-eligible
- **AND** the classification SHALL identify the safety controls that justify that state
- **AND** the classification SHALL define the minimum audit retention expectation for that state

#### Scenario: External broker-facing path is described as formally ready
- **WHEN** a trading execution path depends on a separately deployed Windows broker-facing
  `qmt` / `miniQMT` service and is presented as ready for first formal cross-project acceptance
- **THEN** the readiness claim SHALL point to a local formal acceptance sequence artifact produced
  from `WSL 上的 Ubuntu 24.04.4 LTS`
- **AND** that artifact SHALL distinguish contract-level acceptance from production broker-truth
  claims

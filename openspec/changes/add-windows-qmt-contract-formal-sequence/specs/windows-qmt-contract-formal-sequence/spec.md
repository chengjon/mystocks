# windows-qmt-contract-formal-sequence Specification

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

## ADDED Requirements

### Requirement: Formal Windows qmt Acceptance Sequence Entry Point
The repository SHALL provide a canonical formal acceptance sequence entry point that operators can
run from `WSL 上的 Ubuntu 24.04.4 LTS` against a separately deployed Windows `qmt` / `miniQMT`
service.

#### Scenario: Operator runs the formal sequence
- **WHEN** an operator launches the formal Windows `qmt` acceptance sequence
- **THEN** the sequence SHALL execute a stable local order of steps
- **AND** that order SHALL cover preflight, contract verification, status summarization, and
  artifact capture

### Requirement: Kernel Phase A Defaults
The formal sequence SHALL default to the external `miniQMT` v1 kernel Phase A posture unless the
operator explicitly overrides it.

#### Scenario: Operator targets external miniQMT v1 service
- **WHEN** the operator runs the formal sequence without an explicit contract-profile override
- **THEN** the sequence SHALL default to `contract_profile=kernel-phase-a`
- **AND** it SHALL use the standard report directory under
  `docs/reports/quality/windows-qmt-contract-acceptance`

### Requirement: Baseline-Aware Formal Verification
The formal sequence SHALL support baseline-aware contract drift review without requiring operators
to hand-assemble the command order.

#### Scenario: Existing baseline is available
- **WHEN** a latest Windows `qmt` acceptance baseline is present
- **THEN** the formal sequence SHALL be able to compare the new run against that baseline
- **AND** it SHALL preserve the resulting comparison evidence in the sequence artifacts

#### Scenario: Operator requests baseline freeze
- **WHEN** the operator explicitly requests a baseline freeze after a successful formal sequence
- **THEN** the sequence SHALL only freeze a baseline from a successful completed acceptance summary
- **AND** it SHALL record the resulting baseline artifact paths in the sequence evidence

### Requirement: Sequence Manifest Artifact
The formal sequence SHALL emit a machine-readable manifest that records how the acceptance sequence
was executed.

#### Scenario: Formal sequence completes
- **WHEN** the sequence finishes with success, contract drift, or failure
- **THEN** the manifest SHALL record invoked steps, per-step outcomes, produced artifact paths, and
  the final recommended exit code
- **AND** the manifest SHALL make it clear that the result is a contract-level acceptance artifact,
  not automatic production broker-truth proof

## ADDED Requirements

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


### Requirement: Graphiti MCP Must Be the Project Memory MCP

The project SHALL expose Graphiti MCP as the active project-level memory MCP entry in its maintained MCP configuration files.

#### Scenario: Active MCP config uses Graphiti memory

- **WHEN** an agent reads the repository MCP configuration
- **THEN** it finds a Graphiti MCP server entry
- **AND** that entry points to the project-approved Graphiti MCP endpoint
- **AND** the project-level Apifox MCP entry is no longer advertised as an active memory tool

### Requirement: Mongo Must Remain the Coordination Source of Truth

The project SHALL preserve MongoDB control-plane state as the only authoritative coordination source for main/worker task lifecycle.

#### Scenario: Agent chooses between Mongo and Graphiti

- **WHEN** an agent needs task status, assignment state, approval state, or work item lifecycle
- **THEN** it uses Mongo-backed coordination tools
- **AND** it does not treat Graphiti memory as authoritative workflow state

### Requirement: Graphiti Usage Boundaries Must Be Documented

The project SHALL document when Graphiti MCP is used, when Mongo is used, and how `group_id` values are partitioned for agent workflows.

#### Scenario: Worker starts or resumes work

- **WHEN** a main CLI or worker CLI needs historical context, handoff recall, or fact retrieval
- **THEN** the documentation directs it to Graphiti MCP
- **AND** the documentation includes recommended `group_id` values
- **AND** the documentation preserves Mongo as the control-plane truth source

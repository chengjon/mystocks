## ADDED Requirements

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


### Requirement: Trunk-First Documentation Governance

The repository SHALL govern documentation from canonical trunks outward instead of starting from
individual stale leaf documents.

#### Scenario: Define the canonical trunk before cleanup
- **WHEN** a document family or subtree is selected for cleanup
- **THEN** the repository SHALL define the canonical trunk for that concern first
- **AND** leaf-level edits or deletions SHALL not proceed before that trunk is identified

#### Scenario: Route navigation through trunks first
- **WHEN** indexes or reader entrypoints are updated
- **THEN** they SHALL route users and AI to canonical trunks first
- **AND** they SHALL not present stale leaf documents as co-equal entrypoints

### Requirement: Canonical Documentation Trunks

The repository SHALL define a small set of canonical documentation trunks so that humans and AI can
determine current truth by concern without scanning the full documentation surface.

#### Scenario: Route a reader to the canonical trunk
- **WHEN** a reader needs governance, capability, API contract, operations, or testing truth
- **THEN** the repository SHALL provide a documented canonical trunk for that concern
- **AND** navigational indexes SHALL route readers to that trunk first

#### Scenario: Prevent historical reports from acting as canonical truth
- **WHEN** a historical report, summary, or verification document exists beside active documentation
- **THEN** it SHALL NOT be treated as the canonical truth source
- **AND** the canonical trunk definition SHALL take precedence

### Requirement: Documentation Lifecycle Classification

The repository SHALL classify retained documentation by lifecycle instead of treating all markdown
documents as equally active.

#### Scenario: Classify a retained document family
- **WHEN** a documentation family is inventoried
- **THEN** it SHALL be classified as one of `canonical`, `supporting`, `report`, `plan`,
  `generated_reference`, `archive_candidate`, or `delete_candidate`
- **AND** that classification SHALL be recorded in governance artifacts

#### Scenario: Restrict current-truth language to canonical docs
- **WHEN** a document is classified as `report`, `plan`, `generated_reference`, or `archive_candidate`
- **THEN** it SHALL NOT be relied on as the current truth source for that concern

### Requirement: Trunk-First Retention and Deletion

The repository SHALL make retention, archive, and deletion decisions from canonical trunk mappings,
not by isolated file-by-file judgment.

#### Scenario: Block deletion without canonical replacement
- **WHEN** a document is proposed for deletion
- **AND** no canonical replacement or canonical trunk has been identified
- **THEN** the deletion SHALL be blocked
- **AND** the decision register SHALL mark the document `needs-replacement`

#### Scenario: Delete stale documentation only after decision gates pass
- **WHEN** a document family is marked as a delete candidate
- **AND** canonical replacement mapping, inbound-link cleanup, and retention checks are complete
- **THEN** the repository MAY delete that document family
- **AND** the action SHALL be recorded in the cleanup decision artifacts

#### Scenario: Prefer deletion over perpetual stale rewrites
- **WHEN** a stale document has a canonical replacement
- **AND** no audit or retention obligation requires keeping it
- **THEN** the default remediation SHALL be deletion
- **AND** repetitive wording-only edits SHALL not be the long-term governance strategy

### Requirement: Cluster-Based Cleanup Workflow

The repository SHALL execute documentation governance by subtree or document family clusters instead
of indefinite one-off manual edits.

#### Scenario: Create a bounded cleanup wave
- **WHEN** a high-risk documentation subtree such as `docs/api/` or `docs/reports/` is selected
- **THEN** the governance workflow SHALL inventory that subtree as a bounded cluster
- **AND** it SHALL assign canonical mappings and lifecycle decisions before mutation

#### Scenario: Prefer archive/delete over mass historical relabeling
- **WHEN** a cluster contains redundant or stale historical material
- **THEN** the default remediation SHALL be archive or delete based on canonical trunk decisions
- **AND** file-by-file disclaimer editing SHALL be treated only as a temporary transition tactic

### Requirement: Documentation Governance Audit

The repository SHALL provide machine-readable audit support so future AI and human workflows can
detect duplicate truths, unclassified docs, and blocked deletion candidates.

#### Scenario: Emit documentation inventory findings
- **WHEN** the documentation governance audit runs
- **THEN** it SHALL identify unclassified documentation, duplicate-truth risks, and unresolved
  delete candidates
- **AND** it SHALL produce findings that can be consumed by local workflows or CI

#### Scenario: Reject undocumented new documentation sprawl
- **WHEN** a new documentation subtree or large document family is introduced
- **AND** it is not mapped to a canonical trunk and lifecycle class
- **THEN** governance automation SHALL flag it for review
- **AND** the repository SHALL not treat it as an accepted documentation trunk by default

### Requirement: AI-Friendly Documentation Hierarchy

The repository SHALL expose documentation hierarchy and lifecycle clearly enough that AI can infer
scope boundaries, canonical precedence, and obsolescence without relying on guesswork.

#### Scenario: Distinguish active truth from historical evidence
- **WHEN** AI or a human inspects a documentation subtree
- **THEN** canonical trunks, supporting documents, historical evidence, and obsolete candidates
  SHALL be distinguishable from repository structure or governance artifacts

#### Scenario: Prevent parallel documentation universes
- **WHEN** two document families appear to describe the same concern
- **THEN** governance artifacts SHALL identify which family is canonical
- **AND** the non-canonical family SHALL be marked for merge, archive, or deletion

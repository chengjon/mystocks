# function-tree-governance Specification

## Purpose
Define governance requirements for a machine-readable function-tree catalog, task-card mapping, scope-gate enforcement, mirrored-domain sync duties, and meta-governance self-bootstrap rules.
## Requirements
### Requirement: Governance SHALL maintain a machine-readable function-tree catalog

The system SHALL maintain a machine-readable function-tree catalog with stable domain and node identifiers, coverage paths, categorized entrypoints, and mirror policy metadata.

#### Scenario: Catalog declares mirrored business domains and reserved governance domains
- **GIVEN** the repository loads the function-tree catalog
- **WHEN** the catalog is parsed for governance validation
- **THEN** it SHALL contain business domains that mirror into `docs/FUNCTION_TREE.md`
- **AND** it SHALL contain a reserved `meta-governance` domain
- **AND** each node SHALL declare `coverage_paths` and categorized `entrypoints`.

### Requirement: Task cards SHALL declare function-tree mapping for governed changes

The system SHALL require machine-readable `function_tree` metadata in task cards when task classification and changed scope require function-tree governance.

#### Scenario: Feature task requires function-tree metadata
- **GIVEN** a task card declares `classification.task_type=feature`
- **WHEN** the task card is validated
- **THEN** it SHALL provide `function_tree.domain_id`
- **AND** it SHALL provide `function_tree.node_id`
- **AND** it SHALL provide `function_tree.affected_entrypoints`
- **AND** it SHALL provide `function_tree.update_status`.

### Requirement: Scope gate SHALL validate catalog, task card, and diff consistency

The mainline scope gate SHALL validate that declared function-tree mapping matches the catalog and the effective changed files.

#### Scenario: Changed files do not match declared function-tree node
- **GIVEN** a task card declares a function-tree node
- **AND** the git diff does not match the node `coverage_paths` or declared entrypoint paths
- **WHEN** the scope gate runs
- **THEN** the gate SHALL fail with a function-tree mapping violation.

#### Scenario: Cross-domain business change requires explicit declaration
- **GIVEN** the git diff matches more than one business domain
- **WHEN** the task card omits `secondary_domains` and `exemption_reason`
- **THEN** the scope gate SHALL fail with a cross-domain declaration violation.

### Requirement: Mirrored business entrypoint changes SHALL enforce sync obligations

The system SHALL require explicit sync acknowledgement when mirrored business entrypoints change.

#### Scenario: Mirrored business entrypoint change cannot claim not-needed
- **GIVEN** the git diff hits entrypoint paths of a mirrored business domain
- **WHEN** the task card declares `function_tree.update_status=not-needed`
- **THEN** the scope gate SHALL fail
- **AND** the violation SHALL explain that mirrored business entrypoint changes require sync.

### Requirement: Governance infrastructure SHALL self-bootstrap through meta-governance

The system SHALL allow governance infrastructure changes to use reserved meta-governance nodes without forcing business function-tree document sync.

#### Scenario: Meta-governance change bypasses business document sync
- **GIVEN** the git diff only hits `meta-governance` coverage or entrypoint paths
- **WHEN** the task card declares the corresponding `meta-governance` node
- **THEN** the scope gate SHALL accept `function_tree.update_status=not-needed`
- **AND** it SHALL NOT require `docs/FUNCTION_TREE.md` synchronization.


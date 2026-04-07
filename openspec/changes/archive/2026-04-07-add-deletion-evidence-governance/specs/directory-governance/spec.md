## ADDED Requirements

### Requirement: Deletion Evidence Gate

The project SHALL block tracked directory deletion and batches deleting three or more documents unless
exact-path, pre-existing, machine-readable deletion governance artifacts authorize the deletion.

#### Scenario: Block directory deletion without pre-existing evidence
- **WHEN** a tracked directory is fully deleted from the repository
- **AND** `HEAD:governance/deletion-evidence.yaml` does not contain an approved exact-path directory entry
- **THEN** the deletion evidence gate SHALL report a blocking error

#### Scenario: Block document batch deletion without per-document evidence
- **WHEN** three or more documents are deleted outside already-deleted directories
- **AND** any deleted document lacks an approved exact-path document entry in `HEAD:governance/deletion-evidence.yaml`
- **THEN** the deletion evidence gate SHALL report a blocking error

#### Scenario: Ignore in-commit evidence for deletion authorization
- **WHEN** a commit or worktree adds deletion evidence in the same unmerged state as the deletion
- **THEN** the deletion evidence gate SHALL resolve evidence from `HEAD`
- **AND** it SHALL NOT treat in-commit evidence as valid authorization

### Requirement: Exact Machine-Readable Deletion Evidence

The project SHALL use one canonical machine-readable deletion evidence registry with exact-path scope.

#### Scenario: Exact path evidence authorizes deletion
- **WHEN** `HEAD:governance/deletion-evidence.yaml` contains an entry whose `path` and `kind` exactly match the deletion target
- **AND** the entry has `status: approved`
- **AND** the entry has `code_path_verdict: safe_to_delete`
- **AND** the entry has `function_tree_verdict` equal to `重复冗余` or `正式下线`
- **THEN** the gate SHALL allow that deletion target

#### Scenario: Wildcard or fuzzy evidence is rejected
- **WHEN** a deletion evidence entry uses wildcard path syntax or parent-scope approximation
- **THEN** the gate SHALL treat that entry as invalid authorization
- **AND** it SHALL continue searching only for exact-path evidence

### Requirement: Emergency Waiver Registry

The project SHALL support emergency deletion waivers through one fixed YAML registry with exact-path scope and expiry.

#### Scenario: Allow exact-path emergency waiver
- **WHEN** `HEAD:governance/waivers/deletion-evidence-waivers.yaml` contains an exact-path waiver for the deletion target
- **AND** the waiver includes user approval metadata, owner, reason, ticket/context, and a future expiry date
- **THEN** the gate SHALL allow that deletion target through waiver mode

#### Scenario: Expired or invalid waiver is rejected
- **WHEN** a waiver is expired, missing required fields, or uses wildcard path syntax
- **THEN** the gate SHALL treat the waiver as invalid
- **AND** it SHALL continue to require normal deletion evidence

### Requirement: Dual Gate Integration

The project SHALL enforce the same deletion evidence rules in both commit-time and Claude Stop workflows.

#### Scenario: Enforce staged deletion gate in pre-commit
- **WHEN** `.pre-commit-config.yaml` or `.githooks/pre-commit` runs on staged changes
- **THEN** the deletion evidence gate SHALL inspect staged deletions
- **AND** it SHALL block staged directory deletion or document batch deletion without valid authorization

#### Scenario: Enforce worktree deletion gate in Stop hook
- **WHEN** the Claude Stop hook runs for the current worktree
- **THEN** it SHALL inspect current staged and unstaged deletions through the shared engine
- **AND** it SHALL block stopping when governed deletions lack valid authorization

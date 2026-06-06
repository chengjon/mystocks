## ADDED Requirements

### Requirement: Dirty Worktree Cleanup Governance

The repository SHALL implement dirty worktree cleanup through recoverable, classified, slice-based governance before any destructive root-worktree mutation is allowed.

#### Scenario: Cleanup guide uses an authoritative step map

- **WHEN** the dirty worktree cleanup procedure is updated
- **THEN** the procedure SHALL use one authoritative 0-9 execution sequence
- **AND** approval protocol, generated/runtime artifact rules, product-code rules, and final cleanup details SHALL be represented as controls inside that sequence rather than conflicting parallel steps

#### Scenario: Dirty worktree cleanup is prepared

- **WHEN** the repository has a mixed dirty worktree spanning multiple domains
- **THEN** the cleanup operator SHALL capture branch, HEAD, status inventory, diff statistics, stash inventory, worktree inventory, and service status before mutation
- **AND** the operator SHALL create a recovery snapshot containing tracked diff evidence, untracked-file preservation, a manifest, and restore instructions
- **AND** machine-readable status inventories SHALL use `--porcelain=v1` with NUL-delimited parsing where paths may contain whitespace

#### Scenario: Cleanup entries are classified before mutation

- **WHEN** dirty entries are inventoried for cleanup
- **THEN** each entry SHALL be assigned in a single canonical classification manifest to a cleanup slice such as documentation/governance, OpenSpec, frontend, backend/API, Python source/scripts/tests, root config/tooling, generated/runtime, worktree/stash, or review-required
- **AND** derived inventory tables SHALL be generated from or reconciled to that canonical manifest
- **AND** entries whose business value or lifecycle status is unclear SHALL remain `review_required` and SHALL NOT be deleted based only on static search

#### Scenario: Recovery artifacts are concrete and testable

- **WHEN** a recovery snapshot is produced
- **THEN** its manifest SHALL include creation time, repository path, original branch, original HEAD, tracked diff hash and size, untracked archive hash and size, inventory error count, and missing required files
- **AND** restore instructions SHALL include tracked restore, untracked restore, rescue branch, and fallback notes
- **AND** `git apply --check` results SHALL be documented as a sanity check with known limitations for new files, deleted files, binary files, file mode changes, and index divergence

#### Scenario: Cleanup slices are extracted safely

- **WHEN** a cleanup slice is ready for implementation
- **THEN** the slice SHALL be extracted in a clean review worktree or otherwise isolated branch
- **AND** the slice SHALL include only one responsibility class of changes
- **AND** its validation evidence SHALL match the touched surface before review or merge
- **AND** the clean review worktree path, branch, base commit, and owner SHALL be recorded for final cleanup

#### Scenario: Code cleanup uses graph-backed impact gates

- **WHEN** a cleanup slice touches code symbols, API behavior, frontend routes, or shared test behavior
- **THEN** the operator SHALL run the required impact analysis before editing or committing the code slice
- **AND** staged-scope change detection SHALL be used before commit so unrelated root dirty entries are not included in the risk verdict

#### Scenario: Generated and runtime artifacts are disposed recoverably

- **WHEN** generated or runtime artifacts are found in the dirty worktree
- **THEN** the operator SHALL move, archive, or preserve them with a documented restore path before deletion
- **AND** the final disposition SHALL update ignore rules or governance docs when recurring artifact paths are identified

#### Scenario: Multi-branch dirty work is assigned before cleanup

- **WHEN** dirty paths may belong to multiple active branches, worktrees, or unfinished proposals
- **THEN** the cleanup operator SHALL map those paths to known branches, worktrees, PRs, or OpenSpec changes before assigning a disposition
- **AND** path ownership uncertainty SHALL block deletion and require `review_required` classification

#### Scenario: Root clean status is not overclaimed

- **WHEN** the root worktree reports no dirty entries
- **THEN** the cleanup operator SHALL still enumerate registered worktrees and record each worktree status before claiming cleanup completion
- **AND** final reports SHALL distinguish root-clean state from whole-repository cleanup completion

#### Scenario: Ignore rules are not used for local-only noise

- **WHEN** cleanup proposes a versioned `.gitignore` change
- **THEN** the proposal SHALL document whether the ignored path is team-shared, stable, and reproducible across environments
- **AND** single-machine logs, reports, or tool noise SHALL use local exclude mechanisms instead of versioned ignore rules

#### Scenario: Squash-merged branches are classified with PR evidence

- **WHEN** a branch or worktree is considered stale after a squash merge
- **THEN** the operator SHALL NOT rely only on `git branch --merged`
- **AND** the disposition SHALL consider PR state, merge timestamp, ahead/behind state, file-level diff, and owner approval

#### Scenario: WIP worktrees are not deleted as garbage

- **WHEN** a worktree is a deletion candidate
- **THEN** the operator SHALL record its branch, status, recent log, and untracked files before removal
- **AND** worktrees with substantive WIP SHALL be committed locally, handed off, or assigned to a cleanup slice instead of deleted or ignored

#### Scenario: Rescue branches are retained until recovery is closed

- **WHEN** a `rescue/*` branch exists
- **THEN** it SHALL be retained until recovery packages are externally archived, path-level disposition is approved, and final closeout identifies an alternate recovery path
- **AND** any rescue branch deletion SHALL record the branch name, HEAD, deletion reason, and replacement recovery evidence

#### Scenario: Root realignment is deferred

- **WHEN** cleanup slices are still pending review or merge
- **THEN** root-worktree realignment commands such as blanket reset, clean, or bulk stash/apply SHALL remain blocked
- **AND** root realignment SHALL occur only after approved slices have landed and recovery evidence is still available

#### Scenario: Temporary cleanup infrastructure is retired

- **WHEN** cleanup slices are merged, archived, or explicitly abandoned
- **THEN** temporary clean review worktrees and associated cleanup branches SHALL be removed or documented as retained exceptions
- **AND** the final cleanup report SHALL list removed worktrees, retained exceptions, and remaining residual dirty paths

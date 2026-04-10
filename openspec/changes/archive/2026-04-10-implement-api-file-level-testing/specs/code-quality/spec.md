## ADDED Requirements
### Requirement: API File-Level Test Governance
The project SHALL maintain file-level API test suites as the canonical grouped verification surface for API route modules, and SHALL use documented closeout evidence to distinguish completed mainline salvage from unrelated dirty-worktree hygiene.

#### Scenario: Route module is covered by file-level tests
- **WHEN** an API route module is promoted into the canonical test baseline
- **THEN** the repository SHALL provide a corresponding file-level suite under `tests/api/file_tests/`
- **AND** that suite SHALL verify the route module through grouped endpoint assertions or contract-aligned checks

#### Scenario: Mainline salvage is closed without reopening on root-dirty noise
- **WHEN** the planned file-test salvage batches have already merged on mainline
- **THEN** the project SHALL record a closeout artifact for the salvage line
- **AND** formatting-equivalent or user-owned dirty-worktree drift SHALL be treated as separate hygiene work instead of reopening the closed salvage change

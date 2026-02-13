## ADDED Requirements

### Requirement: ArtDeco Governance Manifest Baseline
The system SHALL define an ArtDeco governance manifest as a machine-verifiable baseline for design-system consistency.

#### Scenario: Required governance sections exist
- **WHEN** the governance manifest is loaded from `web/frontend/src/styles/artdeco-governance-manifest.json`
- **THEN** it includes `tokens`, `typography`, `spacing`, and `docs` sections
- **AND** each section contains governance metadata required for automated checks

#### Scenario: Typography and spacing baseline is explicit
- **WHEN** reviewers inspect governance metadata
- **THEN** the typography baseline references Cinzel, Barlow, and JetBrains Mono
- **AND** the spacing baseline defines an 11-level mapping used by ArtDeco implementation guidance

### Requirement: ArtDeco Documentation Wording Consistency
The system SHALL keep core ArtDeco governance documentation aligned to a v3/v3.1 baseline.

#### Scenario: Core documents use v3 governance language
- **WHEN** core ArtDeco docs are validated
- **THEN** they contain v3/v3.1 governance wording
- **AND** legacy v2 wording is removed from active guidance
- **AND** historical references are preserved only with explicit archived/history labeling

### Requirement: Strict Token Governance Validation
The system SHALL provide strict token governance validation that detects duplicate custom properties and minimizes parser false positives.

#### Scenario: Duplicate custom property definitions are rejected
- **WHEN** a stylesheet defines the same custom property multiple times in governance-controlled scope
- **THEN** the strict token check fails with duplicate-property diagnostics

#### Scenario: Non-style code and comments do not trigger false positives
- **WHEN** Vue template/script blocks or comments include token-like text
- **THEN** strict validation ignores non-style contexts
- **AND** reports only actionable style-governance violations

### Requirement: Governance Checks Are Integrated Into Frontend Workflow
The system SHALL expose governance validation through frontend workflow commands and documentation.

#### Scenario: Strict governance command is discoverable and executable
- **WHEN** developers inspect `web/frontend/package.json`
- **THEN** `lint:artdeco:strict` exists as an executable script
- **AND** developer guidance documents describe when to run it

#### Scenario: Governance violations fail verification
- **WHEN** `npm run lint:artdeco:strict` detects hardcoded or duplicate token violations
- **THEN** the command exits with a non-zero status
- **AND** emits diagnostics suitable for pre-commit or CI workflows

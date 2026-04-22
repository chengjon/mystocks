## ADDED Requirements

### Requirement: ArtDeco Design Contract Precedence

The system SHALL treat `DESIGN.md` as the experience-strategy truth for active ArtDeco frontend work, with runtime and placement governance documents refining implementation boundaries rather than replacing the design contract.

#### Scenario: A new ArtDeco frontend batch is prepared
- **WHEN** a new ArtDeco implementation batch is defined
- **THEN** the batch SHALL derive its experience direction from `DESIGN.md`
- **AND** SHALL use active `web/` governance documents to determine runtime and placement boundaries
- **AND** SHALL NOT use historical V3 summaries or compatibility redirect files as co-equal truth sources

### Requirement: Shared Primitive State-Machine Adoption

The system SHALL adopt the `--ad-*` state-machine token model on canonical shared ArtDeco primitives before attempting broad page-level rollout.

#### Scenario: Shared primitive state behavior is modernized
- **WHEN** a shared ArtDeco primitive such as button, input, or card is updated for state behavior
- **THEN** its visual state expression SHALL bind to the `--ad-*` token system where the current design contract defines those states
- **AND** the change SHALL remain limited to visual-state expression rather than replacing the underlying behavior contract

#### Scenario: Page-level cleanup is proposed in the same batch
- **WHEN** a batch begins to expand from shared primitives into broad page-by-page token adoption
- **THEN** that expansion SHALL be treated as out of scope for the primitive-adoption batch
- **AND** it SHALL require a separate reviewed change

### Requirement: Canonical Shared Semantic Surfaces

The system SHALL assign filter-chip and status-chip semantics to canonical shared surfaces instead of leaving them as repeated page-local styling patterns.

#### Scenario: Filter-chip semantics are implemented
- **WHEN** a reusable filter-chip-like surface is introduced or updated
- **THEN** the implementation SHALL use one canonical shared ownership surface
- **AND** page-local inline styling SHALL NOT become the primary truth for filter-chip semantics

#### Scenario: Status semantics are implemented
- **WHEN** reusable status-chip or badge semantics are updated
- **THEN** the implementation SHALL align with the approved `DESIGN.md` semantic set for values such as warning, holding, pending, profit, and loss where supported
- **AND** the batch SHALL avoid creating competing semantic implementations across multiple shared surfaces without ownership clarity

### Requirement: Compatibility Layers Stay Non-Canonical

The system SHALL keep ArtDeco compatibility style files as bridges only during shared primitive modernization.

#### Scenario: Primitive work encounters compatibility-era variables
- **WHEN** shared primitive adoption touches paths that still depend on compatibility-era variables
- **THEN** the batch SHALL resolve the primitive against canonical token truth where practical
- **AND** SHALL NOT create new runtime truth in `artdeco-main.css`, `artdeco-variables.css`, or `artdeco-colors.css`

### Requirement: Decorative Corner Marker Exception Preservation

The system SHALL preserve the approved runtime exception that decorative corner markers remain globally disabled unless overlap and collision issues are explicitly resolved in a later reviewed change.

#### Scenario: A design enhancement proposal touches decorative chrome
- **WHEN** an ArtDeco frontend batch proposes stronger decorative framing
- **THEN** it MAY reuse geometric language conceptually
- **BUT** it SHALL NOT re-enable global decorative corner marker elements in runtime without a separately reviewed change that proves non-overlapping behavior

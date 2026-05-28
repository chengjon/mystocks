## ADDED Requirements

### Requirement: Impeccable Design Documentation Gate

The system SHALL require ArtDeco Web design improvement work to complete an `impeccable` design-documentation gate before any source implementation begins.

#### Scenario: A new ArtDeco Web design improvement batch is prepared
- **WHEN** a new Web ArtDeco design improvement batch is proposed
- **THEN** the batch SHALL start with design documentation, route critique, or shape artifacts
- **AND** it SHALL NOT begin Vue, TypeScript, SCSS, token, route, component, or composable implementation before approval
- **AND** it SHALL identify the affected ArtDeco documents, active route targets, and verification expectations before implementation

#### Scenario: Pre-approval artifacts are produced
- **WHEN** the batch is still before user approval
- **THEN** allowed outputs SHALL be limited to design context findings, documentation alignment findings, critique reports, shape briefs, page review checklists, implementation task plans, and verification plans
- **AND** build, PM2, or E2E success claims SHALL NOT be used to imply unimplemented UI work has been delivered

### Requirement: Impeccable ArtDeco Audit Sequence

The system SHALL use an `impeccable` audit sequence that inspects the currently implemented Web ArtDeco design before code changes are proposed.

#### Scenario: The baseline design gate runs
- **WHEN** the ArtDeco Web design gate begins
- **THEN** it SHALL run or account for `$impeccable document` as the baseline design-context step
- **AND** it SHALL compare extracted design facts against the active ArtDeco documentation chain and known legacy boundaries

#### Scenario: The first pilot page is reviewed
- **WHEN** a pilot page is selected for page-level ArtDeco review
- **THEN** `web/frontend/src/views/market/Realtime.vue` SHALL be the default first critique target unless an approved design document chooses a different target
- **AND** the critique SHALL evaluate real-time data density, freshness and stale feedback, controls, table or chart structure, runtime states, token usage, and A-share financial semantics

### Requirement: Approval Boundary Before Craft

The system SHALL require explicit approval of the design documents and page shape brief before `impeccable craft` or equivalent implementation work begins.

#### Scenario: A shape brief exists but has not been approved
- **WHEN** `$impeccable shape <target>` has produced a page brief
- **THEN** the brief SHALL be treated as a design document awaiting approval
- **AND** `$impeccable craft <target>` SHALL NOT run until the user explicitly approves the design documents and implementation scope

#### Scenario: Implementation begins after approval
- **WHEN** the user explicitly approves the design documents and implementation scope
- **THEN** implementation SHALL stay inside the approved shape scope
- **AND** the implementation SHALL report the frontend quality gates required by `architecture/STANDARDS.md`

### Requirement: ArtDeco Optimization Priority Classification

The system SHALL classify ArtDeco design and documentation optimization findings by importance before implementation decisions are made.

#### Scenario: A design or documentation issue is found
- **WHEN** `impeccable` or document review identifies an optimization opportunity
- **THEN** the finding SHALL be classified by impact, risk, reuse value, and verification cost
- **AND** P0 findings SHALL cover contradictions with route truth, token truth, runtime safety, or verification gates
- **AND** P1 findings SHALL cover high-use pages or task-critical workflows
- **AND** P2 findings SHALL cover reusable page or component patterns with evidence
- **AND** P3 findings SHALL cover historical, cosmetic, or low-risk documentation cleanup

### Requirement: Post-Approval ArtDeco Implementation Sequence

The system SHALL keep ArtDeco implementation, audit, polish, and extraction work after the design approval boundary.

#### Scenario: A pilot page is approved for implementation
- **WHEN** the approved pilot scope targets a page such as `web/frontend/src/views/market/Realtime.vue`
- **THEN** implementation MAY proceed through `$impeccable craft`, `$impeccable audit`, and `$impeccable polish`
- **AND** shared extraction SHALL NOT occur from a single page unless a second consumer or an approved extraction rationale exists
- **AND** touched visual values SHALL use ArtDeco tokens or documented exceptions

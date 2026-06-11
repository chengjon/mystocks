## ADDED Requirements

### Requirement: Data Source Runtime Extraction Governance

The architecture-governance capability SHALL treat data-source runtime extraction as a proposal-first, phased migration with explicit ownership, rollback, and closure gates.

#### Scenario: Extraction proposal is approved before implementation

- **WHEN** implementation work begins for data-source runtime extraction
- **THEN** the `extract-data-source-runtime-service` proposal SHALL have passed strict OpenSpec validation
- **AND** the user SHALL have approved implementation after reviewing affected specs, phase scope, first pilot, and rollback path

#### Scenario: Phase 2 has an explicit approval gate

- **WHEN** the team is ready to move from completed Phase 0/1 work into Phase 2
- **THEN** Phase 2 SHALL require explicit approval of the REST/WebSocket runtime scope, `RemoteDataSourceClient`, Docker readiness work, and rollback path
- **AND** Phase 2 approval SHALL explicitly exclude MCP tools, MCP transports, mounted MCP diagnostics, and MCP-over-SSE compatibility

#### Scenario: Extraction depends on optimize-data-source-v2 evidence

- **WHEN** the extraction proposal maps local runtime capabilities into the new `DataSourceClient` or `DataSourceRuntime`
- **THEN** it SHALL reference `optimize-data-source-v2` as dependency evidence rather than re-implementing SmartRouter, CircuitBreaker, cache, metrics, BatchProcessor, or runtime config semantics
- **AND** remaining grey/production validation items from `optimize-data-source-v2` SHALL be classified as blockers or parallel follow-up before remote extraction is treated as deliverable

#### Scenario: Compatibility layers have closure criteria

- **WHEN** local/remote clients, main-backend facades, old registry paths, old priority config, or old manager wrappers coexist during migration
- **THEN** each compatibility layer SHALL be documented as thin forwarding or transition code
- **AND** each compatibility layer SHALL have explicit exit criteria before old paths are retired
- **AND** deletion or retirement SHALL follow `architecture/STANDARDS.md` approval and evidence requirements

#### Scenario: Verification matrix is executable

- **WHEN** a migration phase is marked complete
- **THEN** its task entry SHALL include executable validation commands or named evidence artifacts
- **AND** conceptual review alone SHALL NOT be sufficient to close implementation tasks

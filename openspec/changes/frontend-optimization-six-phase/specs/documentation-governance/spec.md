# Documentation Governance Delta

## ADDED Requirements

### Requirement: Frontend Optimization Change Documentation Anchors
The repository SHALL keep frontend optimization change documentation anchors aligned with current canonical web guide paths when active repository-hygiene tests depend on those anchors.

#### Scenario: Active frontend optimization change docs reference canonical web guides
- **GIVEN** repository-hygiene tests read the `frontend-optimization-six-phase` change documentation
- **WHEN** the active OpenSpec change documentation is restored for documentation truth validation
- **THEN** the change documentation references `docs/guides/web/WEB_FRAMEWORK_INCREMENTAL_OPTIMIZATION_PLAN.md`
- **AND** it does not reference retired `docs/frontend/` guide paths

## ADDED Requirements

### Requirement: Compatibility-Aware Core Directory Migration

The directory governance process SHALL distinguish same-name package migration from renamed-module migration when backend Core files are reorganized.

#### Scenario: Same-name package migration

- **GIVEN** `app.core.database` changes from a file to a package
- **WHEN** compatibility is designed
- **THEN** `app.core.database.__init__` SHALL re-export the approved public API
- **AND** import smoke SHALL prove old and new imports resolve correctly

#### Scenario: Renamed-module migration

- **GIVEN** `app.core.cache_manager` moves to `app.core.cache.manager`
- **WHEN** compatibility is designed
- **THEN** `app.core.cache_manager` SHALL remain as a thin wrapper unless all consumers are migrated in the approved batch
- **AND** wrapper retirement SHALL wait for cleanup evidence
- **AND** lifecycle-owned modules SHALL not move until lifecycle ownership and teardown responsibilities are classified

### Requirement: Core Wrapper Retirement Gate

Core compatibility wrappers SHALL NOT be retired until runtime and consumer evidence proves they are no longer needed.

#### Scenario: Wrapper is proposed for deletion

- **GIVEN** a Core wrapper is proposed for deletion
- **WHEN** the deletion is reviewed
- **THEN** evidence SHALL show zero code/test/script consumers, passing import smoke, passing runtime smoke, and a rollback plan

### Requirement: Core Import Matrix Artifact

Core directory migration SHALL produce an import compatibility matrix before file movement.

#### Scenario: Core split batch is approved

- **GIVEN** a Core split implementation batch is proposed
- **WHEN** it is reviewed
- **THEN** the review SHALL include a matrix of old import path, canonical target path, wrapper/re-export strategy, lifecycle owner, monkeypatch consumers, and rollback path
- **AND** the matrix SHALL identify whether the module is blocked by dependency lifecycle coordination

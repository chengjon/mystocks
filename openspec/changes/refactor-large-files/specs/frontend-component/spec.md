## ADDED Requirements

### Requirement: Vue Component Splitting

Vue components exceeding 500 lines SHALL be split into smaller, focused components.

#### Scenario: Template extraction
- **WHEN** a Vue template section exceeds 200 lines
- **THEN** extractable template portions SHALL be moved to child components
- **AND** child components SHALL be placed in a `components/` subdirectory

#### Scenario: Script extraction
- **WHEN** a Vue script section exceeds 200 lines
- **THEN** related logic SHALL be extracted to composables
- **AND** composables SHALL be placed in the `composables/` directory

#### Scenario: API call organization
- **WHEN** a component makes API calls
- **THEN** API calls SHALL be moved to dedicated API files
- **AND** API files SHALL be placed in the `api/` directory

#### Scenario: Style isolation
- **WHEN** component styles exceed 100 lines
- **THEN** shared styles SHALL be moved to global SCSS files
- **AND** component-specific styles SHALL use scoped CSS

### Requirement: Component Communication

Components SHALL communicate through well-defined interfaces.

#### Scenario: Props for parent-to-child
- **WHEN** passing data from parent to child
- **THEN** props SHALL be used
- **AND** props SHALL be type-checked with TypeScript

#### Scenario: Events for child-to-parent
- **WHEN** a child component needs to communicate with parent
- **THEN** events (emit) SHALL be used
- **AND** events SHALL be properly typed

#### Scenario: Provide/Inject for deep nesting
- **WHEN** component nesting exceeds 2 levels
- **THEN** Provide/Inject MAY be used instead of props drilling
- **AND** Provide/Inject SHALL only be used for cross-component data

#### Scenario: Pinia for global state
- **WHEN** state needs to be shared across unrelated components
- **THEN** Pinia store SHALL be used
- **AND** store SHALL be properly typed with TypeScript

### Requirement: Composables Organization

Reusable logic SHALL be extracted to composables.

#### Scenario: Composable naming
- **WHEN** creating a composable
- **THEN** it SHALL use the `use` prefix
- **AND** it SHALL be placed in the `composables/` directory

#### Scenario: Composable responsibilities
- **WHEN** extracting logic to a composable
- **THEN** the composable SHALL have a single responsibility
- **AND** the composable SHALL be testable independently

#### Scenario: Composable state management
- **WHEN** a composable manages state
- **THEN** it SHALL return reactive state
- **AND** it SHALL provide methods to modify state

### Requirement: TypeScript Type Organization

TypeScript type definitions SHALL be organized by domain.

#### Scenario: Domain-based type organization
- **WHEN** organizing type definitions
- **THEN** types SHALL be placed in domain-specific directories
- **AND** each domain SHALL have its own type file

#### Scenario: Type exports
- **WHEN** types need to be shared
- **THEN** an `index.ts` file SHALL provide unified exports
- **AND** types SHALL be exported using `export * from`

#### Scenario: Generated type handling
- **WHEN** types are generated from backend
- **THEN** the generation script SHALL support multi-file output
- **AND** generated types SHALL follow the domain-based organization

## MODIFIED Requirements

### Requirement: Component File Size

Component files SHALL have a maximum size for maintainability.

#### Scenario: Maximum component size
- **WHEN** a Vue component file exceeds 500 lines
- **THEN** it SHALL be considered for refactoring
- **AND** the refactoring plan SHALL be documented

#### Scenario: Sub-component size
- **WHEN** creating sub-components
- **THEN** each sub-component SHALL not exceed 400 lines
- **AND** sub-components SHALL have a single responsibility

## REMOVED Requirements

### Requirement: Monolithic Vue Component

Large monolithic Vue components (exceeding 1000 lines) are REMOVED.

**Reason**: Monolithic components are difficult to maintain, test, and collaborate on.

**Migration**: Each monolithic component SHALL be split into:
- Multiple focused child components
- Composables for reusable logic
- Dedicated API files for data fetching
- Scoped styles or shared style files

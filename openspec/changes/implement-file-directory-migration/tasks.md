## ADDED Requirements

### Requirement: Root Directory Minimalism
The project root directory SHALL contain only 5 core files: README.md, CLAUDE.md, CHANGELOG.md, requirements.txt, and .mcp.json. All other files MUST be organized into appropriate subdirectories.

#### Scenario: Root Directory Compliance
- **WHEN** a new file is created in the project
- **THEN** it SHALL be placed in the appropriate subdirectory according to FILE_ORGANIZATION_RULES.md
- **AND** the root directory SHALL maintain ≤5 files

#### Scenario: Root Directory Audit
- **WHEN** `check-structure.sh` is executed
- **THEN** it SHALL report any files violating root directory rules
- **AND** exit with code 1 if violations are found

### Requirement: File Classification System
All project files SHALL be classified into appropriate directories based on their purpose and type.

#### Scenario: Documentation Files
- **WHEN** a .md file is created
- **THEN** it SHALL be placed in `docs/guides/`, `docs/api/`, `docs/architecture/`, or `docs/standards/`
- **EXCEPT** when it's a submodule document in `web/docs/` or similar

#### Scenario: Script Files
- **WHEN** a script file (.sh, .py) is created
- **THEN** it SHALL be placed in appropriate `scripts/` subdirectories:
  - `scripts/tests/` for test scripts
  - `scripts/runtime/` for production scripts
  - `scripts/database/` for database operations
  - `scripts/dev/` for development tools

#### Scenario: Configuration Files
- **WHEN** a configuration file is created
- **THEN** it SHALL be placed in `config/` directory
- **EXCEPT** when it's environment-specific and belongs in project root

### Requirement: Automated Structure Enforcement
The project SHALL implement automated mechanisms to enforce directory structure rules.

#### Scenario: Pre-commit Validation
- **WHEN** `git commit` is executed
- **THEN** pre-commit hooks SHALL validate directory structure
- **AND** block commits that violate root directory rules

#### Scenario: Manual Organization
- **WHEN** `organize-files.sh` is executed
- **THEN** it SHALL automatically move files to correct locations
- **AND** provide detailed reporting of all moves

#### Scenario: Dry-run Preview
- **WHEN** `organize-files.sh --dry-run` is executed
- **THEN** it SHALL show what moves would be made without executing them
- **AND** allow user to review and confirm changes

### Requirement: Path Independence
All scripts SHALL be designed to work regardless of execution location by using dynamic project root resolution.

#### Scenario: Dynamic Path Resolution
- **WHEN** a script is executed from any directory
- **THEN** it SHALL correctly locate project root and config files
- **AND** not rely on relative paths like `../config/`

### Requirement: Documentation Organization
Documentation files SHALL be organized according to their purpose and scope.

#### Scenario: Project Documentation
- **WHEN** project-level documentation is created
- **THEN** it SHALL be placed in appropriate `docs/` subdirectories
- **AND** follow the established classification system

#### Scenario: Submodule Documentation
- **WHEN** submodule-specific documentation is created
- **THEN** it MAY be placed in the submodule's internal `docs/` directory
- **AND** SHALL be excluded from main project documentation hooks</content>
<parameter name="filePath">openspec/changes/implement-file-directory-migration/specs/file-organization/spec.md
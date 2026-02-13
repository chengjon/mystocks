# OpenSpec Conventions & Format Guide
## Complete Reference for mystocks_spec Project

---

## 1. DIRECTORY STRUCTURE

```
openspec/
├── project.md                    # Project conventions & tech stack
├── AGENTS.md                     # Instructions for AI assistants (THIS FILE)
├── specs/                        # ✅ CURRENT TRUTH - What IS built
│   ├── 01-unified-response-format/
│   ├── 02-type-safety-generation/
│   ├── 03-adapter-pattern/
│   ├── 04-smart-dumb-components/
│   ├── 05-csrf-protection/
│   ├── api-documentation/
│   └── [capability]/
│       ├── spec.md              # Requirements + scenarios
│       └── design.md            # Technical patterns (optional)
│
├── changes/                      # 📝 PROPOSALS - What SHOULD change
│   ├── [change-id]/             # Kebab-case, verb-led
│   │   ├── proposal.md          # Why, what, impact
│   │   ├── tasks.md             # Implementation checklist
│   │   ├── design.md            # Technical decisions (optional)
│   │   └── specs/               # Delta changes
│   │       └── [capability]/
│   │           └── spec.md      # ADDED/MODIFIED/REMOVED
│   │
│   └── archive/                 # ✅ COMPLETED changes
│       └── YYYY-MM-DD-[name]/
│           ├── proposal.md
│           ├── tasks.md
│           └── specs/
```

---

## 2. FILE NAMING CONVENTIONS

### Change IDs (kebab-case, verb-led)
```
✅ CORRECT:
- add-comprehensive-risk-management-system
- refactor-large-files
- update-web-design-system-v2
- implement-file-directory-migration
- extend-frontend-config-model

❌ WRONG:
- AddRiskManagement (PascalCase)
- risk_management (snake_case)
- Risk Management (spaces)
- phase5-risk (phase-based, not verb-led)
```

### Verb Prefixes (in priority order)
- `add-` - New features/capabilities
- `update-` - Enhancements to existing features
- `remove-` - Deprecation/deletion
- `refactor-` - Code reorganization
- `implement-` - Implementation of planned features
- `enhance-` - Performance/quality improvements
- `consolidate-` - Merging multiple changes
- `extend-` - Adding to existing systems

---

## 3. PROPOSAL.MD FORMAT

### Structure
```markdown
# Change: [Brief description]

## Why
[1-2 sentences on problem/opportunity]

## What Changes
- [Bullet list of changes]
- [Mark breaking changes with **BREAKING**]

## Impact
- Affected specs: [list capabilities]
- Affected code: [key files/systems]
```

### Real Example (refactor-large-files)
```markdown
# 重构：拆分超长文件为可维护模块

## 为什么
当前项目中存在多个超过1200行的大型文件，这些文件难以维护、测试和协作开发

## 改变什么
- Python后端文件拆分 (4个文件)
- Vue组件文件拆分 (12个文件)
- TypeScript类型文件拆分
- 测试文件拆分

## 影响
- Affected specs: code-quality, backend-api, frontend-component, test-suite
- Affected code: scripts/ci/, web/backend/app/api/, web/frontend/src/
```

---

## 4. TASKS.MD FORMAT

### Structure
```markdown
## [Phase Number]. [Phase Name]

### [Section Number]. [Section Name]
- [ ] [Task ID] [Task description]
- [ ] [Task ID] [Task description]

## Verification Checklist
- [ ] All new files ≤500 lines
- [ ] No circular dependencies
- [ ] Tests pass
```

### Real Example (refactor-large-files)
```markdown
## 阶段1：立即行动（本周）

### 1.1 修复akshare_market.py类结构
- [ ] 1.1.1 分析akshare_market.py缩进问题
- [ ] 1.1.2 提取retry装饰器到base.py
- [ ] 1.1.3 修复类结构，验证方法定义在类内部
- [ ] 1.1.4 运行测试验证功能正常

### 1.2 拆分mystocks_complete.py
- [ ] 1.2.1 创建目录结构 `api/v1/{system,strategy,trading,admin,analysis}/`
- [ ] 1.2.2 创建 `system/health.py` - 数据库健康检查
...

## 验证清单
- [ ] 所有新文件≤500行
- [ ] 无循环依赖
- [ ] ESLint/Pylint无错误
```

---

## 5. SPEC.MD DELTA FORMAT (CRITICAL!)

### Requirement Header Format
```markdown
### Requirement: [Name]
[Description of what the system SHALL/MUST do]

#### Scenario: [Scenario name]
- **WHEN** [condition]
- **THEN** [expected result]
- **AND** [additional result] (optional)
```

### Delta Operations

#### ADDED Requirements
```markdown
## ADDED Requirements

### Requirement: Domain-Based API Organization
The backend API SHALL be organized by business domain rather than development phase.

#### Scenario: Domain-based directory structure
- **WHEN** organizing API files
- **THEN** directories SHALL use domain names (system, strategy, trading, admin, analysis)
- **AND** directories SHALL NOT use phase numbers (phase1, phase2, etc.)

#### Scenario: System domain
- **WHEN** creating system-related APIs
- **THEN** they SHALL be placed in the `api/v1/system/` directory
- **AND** include health checks and routing management
```

#### MODIFIED Requirements
```markdown
## MODIFIED Requirements

### Requirement: File Size Limits
The codebase SHALL enforce maximum file size limits to maintain code quality and maintainability.

#### Scenario: Python file size limit
- **WHEN** a Python file exceeds 500 lines
- **THEN** the file SHALL be considered for refactoring
- **AND** the development team SHOULD create a plan to split the file

#### Scenario: Vue file size limit
- **WHEN** a Vue file exceeds 500 lines
- **THEN** the file SHALL be considered for component splitting
- **AND** the template, script, and style sections SHOULD be analyzed for independent components
```

#### REMOVED Requirements
```markdown
## REMOVED Requirements

### Requirement: Phase-Based API Organization
The previous requirement for organizing APIs by development phase is REMOVED.

**Reason**: Phase-based organization does not reflect business domains and causes confusion for new developers.

**Migration**: All phase-based directories (phase1, phase2, phase3, phase4, phase5) SHALL be migrated to domain-based directories (system, strategy, trading, admin, analysis).
```

#### RENAMED Requirements
```markdown
## RENAMED Requirements
- FROM: `### Requirement: Login`
- TO: `### Requirement: User Authentication`
```

### Critical Formatting Rules

✅ **CORRECT** (4 hashtags for scenarios):
```markdown
#### Scenario: User login success
- **WHEN** valid credentials provided
- **THEN** return JWT token
```

❌ **WRONG** (don't use these):
```markdown
- **Scenario: User login**           ❌ Bullet point
**Scenario**: User login             ❌ Bold text
### Scenario: User login             ❌ 3 hashtags
Scenario: User login                 ❌ No formatting
```

### Requirement Wording
- Use **SHALL/MUST** for normative requirements (mandatory)
- Use **SHOULD** for recommended but not mandatory
- Use **MAY** for optional features
- Avoid vague language like "should", "could", "might"

### Every Requirement MUST Have At Least One Scenario
```markdown
❌ WRONG - No scenarios:
### Requirement: User Authentication
Users must be able to log in.

✅ CORRECT - Has scenarios:
### Requirement: User Authentication
Users MUST be able to log in with valid credentials.

#### Scenario: Successful login
- **WHEN** valid credentials provided
- **THEN** return JWT token

#### Scenario: Invalid credentials
- **WHEN** invalid credentials provided
- **THEN** return 401 Unauthorized error
```

---

## 6. DESIGN.MD FORMAT (Optional)

Create `design.md` ONLY if:
- Cross-cutting change (multiple services/modules)
- New architectural pattern
- New external dependency or significant data model changes
- Security, performance, or migration complexity
- Ambiguity that benefits from technical decisions

### Minimal Skeleton
```markdown
## Context
[Background, constraints, stakeholders]

## Goals / Non-Goals
- Goals: [...]
- Non-Goals: [...]

## Decisions
- Decision: [What and why]
- Alternatives considered: [Options + rationale]

## Risks / Trade-offs
- [Risk] → Mitigation

## Migration Plan
[Steps, rollback]

## Open Questions
- [...]
```

---

## 7. WHEN TO CREATE A CHANGE PROPOSAL

### ✅ CREATE PROPOSAL FOR:
- New features or functionality
- Breaking changes (API, schema)
- Architecture or pattern changes
- Performance optimizations (changes behavior)
- Security pattern updates

### ❌ SKIP PROPOSAL FOR:
- Bug fixes (restore intended behavior)
- Typos, formatting, comments
- Non-breaking dependency updates
- Configuration changes
- Tests for existing behavior

---

## 8. VALIDATION & COMMANDS

### Essential Commands
```bash
# List active changes
openspec list

# List specifications
openspec list --specs

# Show change details
openspec show [change-id]

# Show spec details
openspec show [spec-id] --type spec

# Validate change (ALWAYS use --strict)
openspec validate [change-id] --strict

# Archive completed change
openspec archive [change-id] --yes

# Debug delta parsing
openspec show [change-id] --json --deltas-only
```

### Common Validation Errors

**"Change must have at least one delta"**
- Check `changes/[name]/specs/` exists with .md files
- Verify files have operation prefixes (## ADDED Requirements)

**"Requirement must have at least one scenario"**
- Check scenarios use `#### Scenario:` format (4 hashtags)
- Don't use bullet points or bold for scenario headers

**"Silent scenario parsing failures"**
- Exact format required: `#### Scenario: Name`
- Debug with: `openspec show [change] --json | jq '.deltas'`

---

## 9. MULTI-CAPABILITY CHANGES

When a change affects multiple capabilities, create separate delta files:

```
openspec/changes/add-2fa-notify/
├── proposal.md
├── tasks.md
└── specs/
    ├── auth/
    │   └── spec.md          # ADDED: Two-Factor Authentication
    └── notifications/
        └── spec.md          # ADDED: OTP Email Notification
```

Each spec.md file contains its own ADDED/MODIFIED/REMOVED sections.

---

## 10. CURRENT PROJECT STATE

### Active Changes (as of Feb 8, 2025)
```
tech-debt-governance-2026q1                    0/8 tasks     5d ago
extend-frontend-config-model                   62/85 tasks   5d ago
frontend-optimization-six-phase                43/119 tasks  5d ago
implement-file-directory-migration             ✓ Complete    5d ago
implement-web-frontend-v2-navigation           17/223 tasks  5d ago
refactor-large-code-files                      150/263 tasks 5d ago
refactor-web-frontend-menu-architecture        20/153 tasks  5d ago
```

### Naming Patterns Observed
- Verb-led: `add-`, `implement-`, `refactor-`, `update-`, `extend-`, `consolidate-`
- Domain-focused: `frontend-`, `backend-`, `api-`, `testing-`
- Feature-specific: `file-directory-migration`, `web-frontend-v2-navigation`
- Governance: `tech-debt-governance-2026q1`

---

## 11. BEST PRACTICES

### Change ID Naming
- ✅ Short and descriptive: `add-two-factor-auth`
- ✅ Verb-led: `add-`, `update-`, `remove-`, `refactor-`
- ✅ Unique: If taken, append `-2`, `-3`, etc.
- ❌ Too long: `add-comprehensive-two-factor-authentication-with-email-and-sms`
- ❌ Phase-based: `phase5-risk-management`

### Capability Naming
- Use verb-noun: `user-auth`, `payment-capture`
- Single purpose per capability
- 10-minute understandability rule
- Split if description needs "AND"

### Spec Writing
- Always check if capability already exists
- Prefer modifying existing specs over creating duplicates
- Use `openspec show [spec]` to review current state
- Include concrete scenarios, not just abstract requirements

### Dependency Management
- API layer → Services layer → Models layer → Utils
- No circular dependencies
- Use local imports as last resort

---

## 12. WORKFLOW SUMMARY

### Stage 1: Creating Changes
1. Review `openspec/project.md` for conventions
2. Run `openspec list` to see active changes
3. Choose unique verb-led `change-id`
4. Scaffold: `proposal.md`, `tasks.md`, optional `design.md`, spec deltas
5. Write deltas with ADDED/MODIFIED/REMOVED Requirements
6. Run `openspec validate [change-id] --strict`
7. Request approval before implementation

### Stage 2: Implementing Changes
1. Read `proposal.md` - Understand what's being built
2. Read `design.md` (if exists) - Review technical decisions
3. Read `tasks.md` - Get implementation checklist
4. Implement tasks sequentially
5. Update checklist: set every task to `- [x]`
6. Verify all work is done

### Stage 3: Archiving Changes
1. Move `changes/[name]/` → `changes/archive/YYYY-MM-DD-[name]/`
2. Update `specs/` if capabilities changed
3. Run `openspec archive [change-id] --yes`
4. Run `openspec validate --strict` to confirm

---

## 13. PROJECT CONVENTIONS (from project.md)

### Code Style
- Python: Black formatting (line-length=88), full type annotations
- Naming: snake_case (functions), PascalCase (classes), UPPER_SNAKE_CASE (constants)
- API paths: kebab-case (e.g., `/api/market-data/stock`)
- Database: snake_case + module prefix (e.g., `market_daily_kline`)

### Architecture Patterns
- Backend: API layer → Services layer → Data layer
- Frontend: Pages → Components → Utils
- Tests: Mirror business code structure
- Data: Adapter pattern for multi-source integration

### Testing Strategy
- Unit tests: ≥95% coverage
- E2E tests: ≥95% coverage
- Performance: API P95 response ≤300ms
- All tests must include normal + edge cases

### Git Workflow
- Commit format: `[type][module]: description`
- Types: feat, fix, refactor, test, docs, deploy
- Each commit: single feature/problem
- Agent-generated code: separate commits with Agent source

---

## 14. QUICK REFERENCE CHECKLIST

Before creating a change proposal:
- [ ] Read `openspec/project.md`
- [ ] Run `openspec list` to see active changes
- [ ] Run `openspec list --specs` to see existing capabilities
- [ ] Check if capability already exists
- [ ] Choose unique verb-led `change-id`
- [ ] Create directory: `openspec/changes/[change-id]/`
- [ ] Write `proposal.md` (Why, What Changes, Impact)
- [ ] Write `tasks.md` (Implementation checklist)
- [ ] Create spec deltas with ADDED/MODIFIED/REMOVED
- [ ] Ensure every requirement has ≥1 scenario
- [ ] Use correct scenario format: `#### Scenario: Name`
- [ ] Run `openspec validate [change-id] --strict`
- [ ] Fix all validation errors
- [ ] Request approval before implementation

---

## 15. EXAMPLE: COMPLETE CHANGE PROPOSAL

### Directory Structure
```
openspec/changes/cleanup-directory-structure/
├── proposal.md
├── tasks.md
├── design.md
└── specs/
    ├── code-quality/
    │   └── spec.md
    └── project-organization/
        └── spec.md
```

### proposal.md
```markdown
# Change: Cleanup Directory Structure and Remove Obsolete Files

## Why
The project root contains 42+ obsolete files and directories from previous phases that clutter the codebase and confuse new developers. Cleaning these up will improve project clarity and maintainability.

## What Changes
- Remove obsolete `.backup`, `.bak`, and temporary files
- Consolidate configuration files into `config/` directory
- Archive old documentation to `docs/archive/`
- Update import paths to reflect new structure
- **BREAKING**: Some import paths will change

## Impact
- Affected specs: code-quality, project-organization
- Affected code: All Python imports, all TypeScript imports, documentation references
```

### tasks.md
```markdown
## 1. Inventory & Analysis
- [ ] 1.1 List all files in project root
- [ ] 1.2 Identify obsolete files (>6 months old, no recent commits)
- [ ] 1.3 Categorize files by type (config, docs, scripts, etc.)
- [ ] 1.4 Document dependencies on obsolete files

## 2. Consolidation
- [ ] 2.1 Create `config/` subdirectories for each config type
- [ ] 2.2 Move configuration files to `config/`
- [ ] 2.3 Update all import paths
- [ ] 2.4 Verify imports work correctly

## 3. Archival
- [ ] 3.1 Create `docs/archive/` directory
- [ ] 3.2 Move old documentation to archive
- [ ] 3.3 Create index of archived documents
- [ ] 3.4 Update main README with archive reference

## 4. Cleanup
- [ ] 4.1 Delete obsolete `.backup` files
- [ ] 4.2 Delete obsolete `.bak` files
- [ ] 4.3 Delete temporary files
- [ ] 4.4 Verify no broken references

## 5. Verification
- [ ] 5.1 Run all tests
- [ ] 5.2 Check linting passes
- [ ] 5.3 Verify imports work
- [ ] 5.4 Update documentation
```

### specs/code-quality/spec.md
```markdown
## ADDED Requirements

### Requirement: Root Directory Cleanliness
The project root directory SHALL contain only essential files and directories.

#### Scenario: No obsolete files
- **WHEN** scanning project root
- **THEN** no `.backup` or `.bak` files SHALL exist
- **AND** no temporary files SHALL exist

#### Scenario: Organized configuration
- **WHEN** looking for configuration files
- **THEN** all configuration files SHALL be in `config/` directory
- **AND** configuration files SHALL be organized by type

### Requirement: Import Path Consistency
All import paths SHALL be consistent and reflect the current directory structure.

#### Scenario: Python imports
- **WHEN** importing from project modules
- **THEN** imports SHALL use paths from `src/` directory
- **AND** no imports SHALL reference obsolete directories

#### Scenario: TypeScript imports
- **WHEN** importing from project modules
- **THEN** imports SHALL use paths from `web/frontend/src/` directory
- **AND** no imports SHALL reference obsolete directories
```

---

## SUMMARY

The openspec system is a **spec-driven development framework** with three key concepts:

1. **`specs/`** = Current truth (what IS built)
2. **`changes/`** = Proposals (what SHOULD change)
3. **`archive/`** = Completed changes (what WAS changed)

Key rules:
- Change IDs: kebab-case, verb-led
- Every requirement needs ≥1 scenario
- Scenarios: `#### Scenario: Name` with WHEN/THEN/AND
- Deltas: ADDED/MODIFIED/REMOVED/RENAMED
- Validate with `--strict` flag
- Archive after deployment

This structure ensures clear communication, traceability, and maintainability of all project changes.

# Tasks: Web Application Development Methodology Improvement

**Feature Branch**: `006-web-90-1`
**Input**: Design documents from `/opt/claude/mystocks_spec/specs/006-web-90-1/`
**Prerequisites**: plan.md, spec.md, research.md, process-framework.md, quickstart.md

**Tests**: No tests required - this is a process/documentation improvement project

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each deliverable.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- All paths are absolute for clarity

## Path Conventions
- **Documentation**: `/opt/claude/mystocks_spec/docs/development-process/`
- **Integration Tests**: `/opt/claude/mystocks_spec/tests/integration/`
- **Spec Directory**: `/opt/claude/mystocks_spec/specs/006-web-90-1/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create directory structure and install required tools

- [ ] T001 [P] Create documentation directory structure at `/opt/claude/mystocks_spec/docs/development-process/`
- [ ] T002 [P] Create integration test directory structure at `/opt/claude/mystocks_spec/tests/integration/`
- [ ] T003 [P] Create examples directory at `/opt/claude/mystocks_spec/docs/development-process/examples/`
- [ ] T004 [P] Create helper scripts directory at `/opt/claude/mystocks_spec/scripts/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Install and configure tools that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Install Playwright with Python support: `pip install playwright pytest-playwright && playwright install chromium`
- [ ] T006 [P] Install httpie for API testing: `pip install httpie`
- [ ] T007 [P] Install jq for JSON processing: `sudo apt install jq` or `brew install jq`
- [ ] T008 [P] Install pgcli for PostgreSQL: `pip install pgcli`
- [ ] T009 [P] Create bash aliases file at `/opt/claude/mystocks_spec/scripts/bash_aliases.sh`
- [ ] T010 Create verification screenshot directory at `/opt/claude/mystocks_spec/docs/verification-screenshots/`

**Checkpoint**: Tools installed - documentation and test implementation can now begin in parallel

---

## Phase 3: User Story 1 - End-to-End Functional Verification (Priority: P1) 🎯 MVP

**Goal**: Establish complete end-to-end verification process with Definition of Done framework

**Independent Test**: Developer can follow the Definition of Done checklist and successfully verify a simple bug fix passes all 5 layers of verification

### Implementation for User Story 1

- [ ] T011 [P] [US1] Create Definition of Done main document at `/opt/claude/mystocks_spec/docs/development-process/definition-of-done.md` (consolidate from `process-framework.md`)
- [ ] T012 [P] [US1] Create manual verification guide at `/opt/claude/mystocks_spec/docs/development-process/manual-verification-guide.md` (based on Layer 4/5 in framework)
- [ ] T013 [P] [US1] Create tool selection guide at `/opt/claude/mystocks_spec/docs/development-process/tool-selection-guide.md` (based on research.md decisions)
- [ ] T014 [P] [US1] Create API verification command templates at `/opt/claude/mystocks_spec/scripts/api_templates.sh` (from research.md manual verification patterns)
- [ ] T015 [P] [US1] Create SQL query templates at `/opt/claude/mystocks_spec/scripts/sql_templates.sql` (from research.md Data Validation patterns)
- [ ] T016 [US1] Create quickstart README at `/opt/claude/mystocks_spec/docs/development-process/README.md` (overview and quick links to all docs)
- [ ] T017 [US1] Create concrete API fix example at `/opt/claude/mystocks_spec/docs/development-process/examples/api-fix-example.md` with screenshots showing all 5 layers
- [ ] T018 [US1] Create concrete UI fix example at `/opt/claude/mystocks_spec/docs/development-process/examples/ui-fix-example.md` with screenshots showing all 5 layers
- [ ] T019 [US1] Create data integration example at `/opt/claude/mystocks_spec/docs/development-process/examples/data-integration-example.md` with screenshots

**Checkpoint**: At this point, developers have complete Definition of Done documentation and can manually verify any feature using the 5-layer model

---

## Phase 4: User Story 2 - Automated Integration Testing Framework (Priority: P1)

**Goal**: Implement Playwright-based end-to-end testing that validates complete data flows

**Independent Test**: Run `pytest tests/integration/test_user_login_flow.py -v` and verify it executes complete browser automation, tests all layers, and provides clear failure messages indicating which layer failed

### Implementation for User Story 2

- [ ] T020 [P] [US2] Create Playwright configuration file at `/opt/claude/mystocks_spec/tests/integration/conftest.py` (fixtures, browser setup, authentication, layer validation helpers)
- [ ] T021 [P] [US2] Create browser helpers utility at `/opt/claude/mystocks_spec/tests/integration/utils/browser_helpers.py` (screenshot, wait functions, common selectors)
- [ ] T022 [P] [US2] Create layer validation utility at `/opt/claude/mystocks_spec/tests/integration/utils/layer_validation.py` (database check, API check, UI check functions)
- [ ] T023 [US2] Implement user login flow test at `/opt/claude/mystocks_spec/tests/integration/test_user_login_flow.py` (FR-006 requirement: verify login → dashboard flow with all 4 layers)
- [ ] T024 [US2] Implement dashboard data display test at `/opt/claude/mystocks_spec/tests/integration/test_dashboard_data_display.py` (FR-006 requirement: verify dashboard loads with data, tests all 4 layers, includes layer failure detection per FR-005)
- [ ] T025 [US2] Implement data table rendering test at `/opt/claude/mystocks_spec/tests/integration/test_data_table_rendering.py` (FR-006 requirement: verify at least one data table renders with actual data)
- [ ] T026 [US2] Create Playwright test example file at `/opt/claude/mystocks_spec/specs/006-web-90-1/contracts/playwright-test-examples/example_login_flow.py` (copy of test_user_login_flow.py with detailed comments)
- [ ] T027 [US2] Create dashboard test example at `/opt/claude/mystocks_spec/specs/006-web-90-1/contracts/playwright-test-examples/example_dashboard_data.py` (copy of test_dashboard_data_display.py with detailed comments)
- [ ] T028 [US2] Create layer failure detection example at `/opt/claude/mystocks_spec/specs/006-web-90-1/contracts/playwright-test-examples/example_layer_failure_detection.py` (demonstrates how tests pinpoint failing layer)

**Checkpoint**: At this point, automated integration tests cover core user journeys and clearly indicate which layer failed when tests don't pass

---

## Phase 5: User Story 3 - Clear Development Process Documentation (Priority: P2)

**Goal**: Provide step-by-step process documentation defining what "complete" means

**Independent Test**: New developer reads documentation and successfully completes verification of one feature following all documented steps without asking for clarification

### Implementation for User Story 3

- [ ] T029 [P] [US3] Create troubleshooting guide at `/opt/claude/mystocks_spec/docs/development-process/troubleshooting.md` (common failure modes from FR-017: API returns 500, Frontend shows no data, Database connection fails, plus solutions)
- [ ] T030 [P] [US3] Add workflow diagram to Definition of Done document (visual flow from "code written" to "deployed" showing all 5 layers and decision points)
- [ ] T031 [P] [US3] Create verification workflow infographic at `/opt/claude/mystocks_spec/docs/development-process/verification-workflow.png` or `.svg` (5-layer model visual with time estimates)
- [ ] T032 [US3] Create onboarding checklist document at `/opt/claude/mystocks_spec/docs/development-process/onboarding-checklist.md` (verify developer has all tools installed and understands process)
- [ ] T033 [US3] Add time estimates section to manual verification guide (simple bug: 5-10 min, medium feature: 20-30 min per FR-009)
- [ ] T034 [US3] Create process adoption metrics doc at `/opt/claude/mystocks_spec/docs/development-process/adoption-metrics.md` (tracking template for "% features marked complete that are verifiably functional" per SC-001)

**Checkpoint**: At this point, process documentation is complete with clear criteria, time estimates, and troubleshooting guidance

---

## Phase 6: User Story 4 - Tool Selection Guidance (Priority: P2)

**Goal**: Provide clear guidance on when to use MCP tools vs AGENTS vs manual verification

**Independent Test**: Apply tool selection decision tree to 3 different scenarios (simple fix, complex integration, data verification) and confirm recommended approach is practical

### Implementation for User Story 4

- [ ] T035 [US4] Create tool selection decision tree document at `/opt/claude/mystocks_spec/specs/006-web-90-1/contracts/tool-selection-decision-tree.md` (flowchart: task type → recommended tool, per FR-010)
- [ ] T036 [US4] Add MCP tools usage section to tool selection guide (what MCP is, when to use it - systematic multi-endpoint verification, concrete example commands per FR-011)
- [ ] T037 [US4] Add AGENTS usage section to tool selection guide (what AGENTS are, when to use them - complex multi-step analysis, example scenarios per FR-012)
- [ ] T038 [US4] Add manual verification section to tool selection guide (when tools NOT needed - simple one-line fixes per FR-013)
- [ ] T039 [US4] Create tool comparison matrix at `/opt/claude/mystocks_spec/docs/development-process/tool-comparison.md` (MCP vs AGENTS vs Manual: when to use each, pros/cons, time investment)
- [ ] T040 [US4] Add MCP tool examples to API verification guide (concrete curl/httpie commands for MyStocks APIs: dashboard, dragon-tiger, fund-flow)

**Checkpoint**: At this point, developers have clear decision-making framework for tool selection with concrete examples

---

## Phase 7: User Story 5 - Rapid Deployment Confidence Checklist (Priority: P3)

**Goal**: Create quick smoke test checklist that catches critical breaks in <5 minutes

**Independent Test**: Run smoke test checklist after known-good deployment and after intentionally broken deployment, confirm it catches the break

### Implementation for User Story 5

- [ ] T041 [P] [US5] Create smoke test main document at `/opt/claude/mystocks_spec/specs/006-web-90-1/contracts/smoke-test-checklist.md` (5-7 critical tests per FR-014)
- [ ] T042 [P] [US5] Create smoke test guide at `/opt/claude/mystocks_spec/docs/development-process/smoke-test-guide.md` (detailed guide linking to spec checklist)
- [ ] T043 [US5] Implement smoke test suite at `/opt/claude/mystocks_spec/tests/smoke/test_smoke.py` (7 critical tests from research.md: health check, DB connectivity, login, dashboard loads, critical APIs, frontend assets, data table rendering)
- [ ] T044 [US5] Create pre-deployment check script at `/opt/claude/mystocks_spec/scripts/pre_deploy_check.sh` (runs smoke tests, validates pass/fail, blocks deployment on failure)
- [ ] T045 [US5] Add smoke test execution instructions to smoke-test-guide.md (how to run `pytest tests/smoke/ -v -x`, expected pass/fail output per FR-015)
- [ ] T046 [US5] Create smoke test CI/CD integration example at `/opt/claude/mystocks_spec/docs/development-process/examples/ci-cd-smoke-test.yml` (GitHub Actions example running smoke tests on PR)

**Checkpoint**: At this point, smoke tests provide 5-minute pre-deployment confidence check for core functionality

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final touches and integration across all user stories

- [ ] T047 [P] Update main README.md at `/opt/claude/mystocks_spec/README.md` to link to new development process documentation
- [ ] T048 [P] Create development process index at `/opt/claude/mystocks_spec/docs/development-process/INDEX.md` (master index of all documentation with descriptions)
- [ ] T049 [P] Create quickstart validation script at `/opt/claude/mystocks_spec/scripts/validate_quickstart.sh` (verifies all tools installed, all docs present, runs one example verification)
- [ ] T050 [P] Add adoption metrics tracking to README (link to adoption-metrics.md, current baseline: 10% functional, target: 90% functional)
- [ ] T051 Review all documentation for Chinese language consistency and completeness (all process docs must be in Chinese per FR-016)
- [ ] T052 Create team training presentation outline at `/opt/claude/mystocks_spec/docs/development-process/training-outline.md` (2-hour training agenda based on process-framework.md rollout plan)
- [ ] T053 Generate consolidated documentation bundle at `/opt/claude/mystocks_spec/docs/development-process/COMPLETE_GUIDE.md` (single-file reference with all key documentation)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P1 → P2 → P2 → P3)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories - Core DoD framework
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independent but references US1's DoD concepts
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Extends US1's documentation with troubleshooting and metrics
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Independent guidance on tool selection
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Independent smoke testing framework

### Within Each User Story

- Documentation tasks (different files) can run in parallel [P]
- Example creation depends on main documentation
- Script creation can happen in parallel with documentation
- No test tasks (this is documentation project, not code)

### Parallel Opportunities

- All Setup tasks (T001-T004) can run in parallel
- All Foundational tool installation tasks (T006-T009) can run in parallel
- Within US1: T011-T015 (all different docs) can run in parallel
- Within US2: T020-T022 (utils and config) can run in parallel, then T023-T025 (tests), then T026-T028 (examples)
- Within US3: T029-T031 can run in parallel
- Within US4: T036-T038 (adding sections to same doc) must be sequential, but T039-T040 can run after
- Within US5: T041-T042 can run in parallel, T044-T046 can run after T043
- All Polish tasks (T047-T050) can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1 (Definition of Done)

```bash
# Launch all main documentation files together:
Task T011: "Create Definition of Done main document"
Task T012: "Create manual verification guide"
Task T013: "Create tool selection guide"
Task T014: "Create API verification command templates"
Task T015: "Create SQL query templates"

# These 5 tasks are all different files with no dependencies - perfect for parallel execution
```

---

## Parallel Example: User Story 2 (Integration Testing)

```bash
# Launch all utility files together:
Task T020: "Create Playwright configuration file (conftest.py)"
Task T021: "Create browser helpers utility"
Task T022: "Create layer validation utility"

# Once utils are done, launch all integration tests together:
Task T023: "Implement user login flow test"
Task T024: "Implement dashboard data display test"
Task T025: "Implement data table rendering test"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only - Both P1)

1. Complete Phase 1: Setup (T001-T004) - Create directory structure
2. Complete Phase 2: Foundational (T005-T010) - Install all tools - **CRITICAL BLOCKER**
3. Complete Phase 3: User Story 1 (T011-T019) - Definition of Done framework complete
4. Complete Phase 4: User Story 2 (T020-T028) - Integration tests functional
5. **STOP and VALIDATE**:
   - Developers can follow DoD checklist (US1)
   - Integration tests run successfully (US2)
   - Run example verification using both frameworks
6. Deploy/demo if ready - **This is a minimal viable process improvement**

### Incremental Delivery

1. Complete Setup + Foundational → Tools ready
2. Add User Story 1 → Developers have DoD framework → Can start using immediately
3. Add User Story 2 → Automated integration tests working → Reduces manual verification time
4. Add User Story 3 → Process documentation complete with troubleshooting → Self-service support
5. Add User Story 4 → Tool selection clarity → Efficient tool usage
6. Add User Story 5 → Smoke tests working → Fast pre-deployment confidence
7. Each story adds value without breaking previous deliverables

### Parallel Team Strategy

With multiple developers (recommended for speed):

1. Team completes Setup + Foundational together (T001-T010)
2. Once Foundational is done (tools installed):
   - **Developer A**: User Story 1 (T011-T019) - DoD documentation
   - **Developer B**: User Story 2 (T020-T028) - Integration tests
   - **Developer C**: User Story 4 (T035-T040) - Tool selection guide
3. Then add:
   - **Developer A**: User Story 3 (T029-T034) - Troubleshooting docs
   - **Developer B**: User Story 5 (T041-T046) - Smoke tests
4. Stories complete and integrate independently

**Time Estimate**:
- Setup + Foundational: 2-3 hours
- User Story 1: 6-8 hours (core DoD docs)
- User Story 2: 4-6 hours (integration tests)
- User Story 3: 3-4 hours (troubleshooting)
- User Story 4: 2-3 hours (tool selection)
- User Story 5: 2-3 hours (smoke tests)
- Polish: 1-2 hours
- **Total: 20-29 hours (2.5-3.5 days)**

---

## Notes

- [P] tasks = different files, can run in parallel
- [Story] label (US1-US5) maps task to specific user story for traceability
- Each user story should be independently deliverable and usable
- No test tasks included (documentation project, testing not requested in spec)
- All documentation must be in Chinese (中文) per FR-016
- Commit after each logical group of tasks
- Stop at any checkpoint to validate story independently
- Priority: Focus on US1 + US2 (both P1) for MVP, then US3-US5 as enhancements

---

## Success Criteria Mapping

| User Story | Success Criterion | Validation Method |
|------------|-------------------|-------------------|
| US1 | SC-001: 90% of features marked "complete" are verifiably functional | Track using adoption-metrics.md template (T034) |
| US1 | SC-003: Verification time increases by <30% | Measure using time estimates in manual verification guide (T033) |
| US1 | SC-004: "Thought done but broken" incidents decrease 75% | Track using adoption-metrics.md (T034) |
| US1 | SC-005: Developers answer "Is this functional?" with confidence | Verify via onboarding checklist (T032) |
| US2 | SC-002: Integration tests detect 80% of breaks before manual testing | Verify by running test suite (T023-T025) on intentional failures |
| US2 | SC-005: Developers cite specific test results | Integration test output provides layer-specific failure messages (T024) |
| US3 | SC-007: 90% of developers follow process without clarification | Validated after 2-week rollout using training outline (T052) |
| US5 | SC-006: Smoke tests catch 100% of critical path breaks | Verify using pre-deployment check script (T044) |

---

**Generated**: 2025-10-29
**Feature**: Web Application Development Methodology Improvement
**Branch**: `006-web-90-1`
**Total Tasks**: 53
**Estimated Effort**: 20-29 hours (2.5-3.5 days)

# Feature Specification: Web Application Development Methodology Improvement

**Feature Branch**: `006-web-90-1`
**Created**: 2025-10-29
**Status**: Draft
**Input**: User description: "工作方法改进分析：Web应用90%功能不可用问题的根本原因分析和解决方案。需要评估当前开发流程中的问题：1）前后端集成验证不足 2）数据流完整性检查缺失 3）端到端测试覆盖不够 4）是否需要MCP工具辅助 5）是否需要AGENTS协作 6）文档指导是否足够详细。目标是建立更有效的开发和验证流程，确保功能的可用性而不仅仅是代码的正确性。"

## Background Context

**Current Situation**:
- Web application has 90% of features non-functional
- Many features show UI elements but lack data or have incorrect backend connections
- Recent development focused on fixing login API (HTTP 500 error) with graceful degradation and monitoring
- 42 test cases created with 85% pass rate, but tests focus on API correctness, not end-to-end functionality
- User cannot effectively use the web application despite code-level fixes being "complete"

**Core Problem**: Development methodology focuses on **code correctness** rather than **functional usability**, resulting in technically correct components that don't work together as a system.

**Root Cause Analysis** (2025-10-29): Detailed analysis revealed 8 critical/medium bugs blocking functionality:
- BUG-NEW-005 (P0): Watchlist API endpoint mismatch (frontend expects `/category/`, backend provides `/group/`)
- BUG-NEW-003 (P0): Technical Analysis indicator config still uses MySQL (removed in Week 3 architecture simplification)
- BUG-NEW-001 (P1): Dashboard concept stocks tab hardcoded to empty array
- BUG-NEW-007 (P1): ETF data API endpoint naming inconsistency
- BUG-NEW-002, BUG-NEW-004, BUG-NEW-006, BUG-NEW-008 (P2): Additional data handling and UI issues

**Scope Clarification**:
- **IN SCOPE**: Development process improvement, Definition of Done framework, integration test infrastructure, verification methodology
- **OUT OF SCOPE**: Fixing the 8 existing bugs listed above (requires separate implementation effort, see `specs/006-web-90-2-bug-fixes/` or similar)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - End-to-End Functional Verification Before Deployment (Priority: P1)

As a **development team**, when we complete any feature work (bug fix, enhancement, or new feature), we need to verify that the entire feature chain works from user interface to data display, so that we can confidently deploy knowing users can actually use the functionality.

**Why this priority**: This addresses the core issue - 90% of features don't work despite code being "correct". Without end-to-end verification, code correctness is meaningless to users.

**Independent Test**: Can be fully tested by establishing a verification checklist for any single feature (e.g., dashboard data display) and confirming data flows from database → backend API → frontend display → user sees actual data.

**Acceptance Scenarios**:

1. **Given** a completed bug fix or feature, **When** the developer runs the end-to-end verification checklist, **Then** all steps (backend API returns data, frontend receives data, UI displays data correctly) pass before code is considered "complete"

2. **Given** the dashboard feature, **When** the verification process is executed, **Then** the developer confirms: database has data, API endpoint returns data, frontend makes correct API calls, data appears in UI, no console errors

3. **Given** any feature deployment, **When** the end-to-end test fails at any step, **Then** the feature is marked as incomplete and the specific failure point is documented for fixing

---

### User Story 2 - Automated Integration Testing Framework (Priority: P1)

As a **developer**, I need an automated test suite that validates complete data flows (database → backend → frontend → UI), so that I can quickly identify integration breaks without manual verification every time.

**Why this priority**: Manual end-to-end testing is time-consuming and error-prone. Automation ensures consistent verification and catches regression issues.

**Independent Test**: Can be fully tested by creating one complete integration test (e.g., "user logs in and sees dashboard data") that exercises all system layers and delivers confidence that the feature actually works.

**Acceptance Scenarios**:

1. **Given** a complete feature, **When** the automated integration test runs, **Then** it verifies database connectivity, API response correctness, frontend API calls, and data rendering in UI

2. **Given** a code change in any layer (database, backend, frontend), **When** integration tests are re-run, **Then** any breaks in data flow are immediately detected with clear error messages indicating which layer failed

3. **Given** the test suite, **When** it executes, **Then** test results clearly show: X% of features fully functional (end-to-end working), Y% partially functional (specific layer broken), Z% non-functional

---

### User Story 3 - Clear Development Process Documentation (Priority: P2)

As a **developer**, I need step-by-step process documentation that clearly defines "what does 'complete' mean for any work item", so that I don't prematurely mark features as done when they're only code-correct but not user-functional.

**Why this priority**: Current confusion stems from lack of clear "Definition of Done". Code passes tests but features don't work for users.

**Independent Test**: Can be fully tested by following the documented process for one feature and confirming that following all steps results in a fully functional, user-usable feature.

**Acceptance Scenarios**:

1. **Given** a new bug fix or feature task, **When** the developer follows the process documentation, **Then** they know they must verify: unit tests pass, integration tests pass, manual end-to-end verification complete, deployment checklist complete

2. **Given** the process documentation, **When** a developer completes their work, **Then** they have a clear checklist showing: [ ] Code written, [ ] Unit tests pass, [ ] Integration tests pass, [ ] API manually verified (curl/Postman), [ ] Frontend manually verified (browser), [ ] Data visible to user

3. **Given** ambiguity about "is this feature done?", **When** the developer consults the documentation, **Then** they find clear criteria: "A feature is done when a user can successfully complete the intended task without errors and see expected results"

---

### User Story 4 - Tool Selection Guidance (MCP vs AGENTS vs Manual) (Priority: P2)

As a **development team**, we need clear guidance on when to use MCP tools, when to use AGENTS, and when manual verification is sufficient, so that we use the right tools for the right tasks without over-engineering or under-verifying.

**Why this priority**: Confusion about tooling contributes to process inefficiency. Clear guidance prevents both "not using helpful tools" and "over-complicating simple tasks".

**Independent Test**: Can be fully tested by applying the tool selection guidance to three different scenarios (simple bug fix, complex integration feature, data verification task) and confirming the recommended approach is practical and effective.

**Acceptance Scenarios**:

1. **Given** a simple bug fix (e.g., fix typo in error message), **When** consulting tool guidance, **Then** the documentation recommends manual verification (no need for MCP/AGENTS) with clear verification steps

2. **Given** a complex multi-system integration task (e.g., verify all dashboard APIs work), **When** consulting tool guidance, **Then** the documentation recommends MCP tools for systematic API verification and shows example usage

3. **Given** a data quality verification task (e.g., check database has expected data), **When** consulting tool guidance, **Then** the documentation recommends AGENTS if data spans multiple sources or manual SQL queries if simple, with decision tree provided

---

### User Story 5 - Rapid Deployment Confidence Checklist (Priority: P3)

As a **team lead or developer**, before merging any code to main branch or deploying to production, I need a quick "smoke test" checklist that verifies core functionality works, so that we catch obvious breaks before they reach users.

**Why this priority**: Acts as final safety net. Less critical than development process itself but prevents embarrassing deployments.

**Independent Test**: Can be fully tested by running the smoke test checklist after a known-good deployment and after an intentionally broken deployment, confirming it catches the break.

**Acceptance Scenarios**:

1. **Given** code ready for deployment, **When** the smoke test checklist is executed, **Then** it verifies: user can login, dashboard loads with data, at least one data table shows records, no 500 errors in browser console

2. **Given** a deployment with broken database connection, **When** the smoke test runs, **Then** it immediately fails with clear message "Dashboard API returns no data - check backend logs"

3. **Given** successful smoke test completion, **When** the team reviews results, **Then** they have confidence that core user journeys work (even if edge cases may still have issues)

---

### Edge Cases

- **What happens when automated integration tests fail intermittently?**: Process should include re-run logic and guidance on when to investigate flakiness vs accepting occasional failures
- **What happens when manual end-to-end verification takes too long (>30 minutes)?**: Documentation should provide "critical path" vs "full verification" checklists with time estimates
- **What happens when different developers interpret "functional" differently?**: Process documentation must include concrete examples with screenshots showing "this is functional" vs "this is not functional"
- **What happens when backend is correct but frontend has bug?**: Integration tests should pinpoint the failing layer (backend vs frontend vs database) to avoid "works for me" debates

## Definitions *(mandatory)*

To ensure clarity throughout this specification, the following terms are defined:

**MCP Tools**: Model Context Protocol tools for systematic API verification. These are standardized command-line tools (such as `httpie`, `curl` with structured workflows, or dedicated MCP clients) used to test API endpoints consistently. MCP tools provide structured output, authentication handling, and repeatable test patterns for backend API validation.

**AGENTS**: AI-powered analysis tools used for complex multi-step verification tasks. AGENTS can analyze multiple data sources, trace data flows across system layers, perform exploratory testing, and generate comprehensive reports. Used when verification requires intelligent decision-making beyond simple pass/fail checks.

**Definition of Done (DoD)**: A comprehensive checklist defining when a feature is truly "complete" and ready for deployment. Goes beyond code-level correctness to verify functional usability across all system layers (database → backend API → frontend → user interface → actual user-visible results).

**Layer-Specific Failure Detection**: The ability of integration tests to clearly indicate which system layer failed when a test does not pass. Example outputs:
- "Backend API Layer Failed: returned 500 status code"
- "Frontend Layer Failed: did not call expected API endpoint"
- "Database Layer Failed: query returned no data"
- "UI Layer Failed: data received but not rendered in interface"

**Smoke Test**: A quick pre-deployment verification suite (target: <5 minutes) that checks core functionality is working. Catches critical breaks (login fails, dashboard completely non-functional) before they reach production.

**Functional Usability**: A feature is functionally usable when an end user can successfully complete the intended task and see expected results, without errors or missing data. Contrasts with "code correctness" which only verifies code compiles and passes unit tests.

## Requirements *(mandatory)*

### Functional Requirements

**Process Definition:**

- **FR-001**: Development process MUST define clear "Definition of Done" that requires both code correctness AND functional usability verification
- **FR-002**: Definition of Done MUST include mandatory checklist items: unit tests pass, integration tests pass, manual verification complete (API + UI), data visible to end user
- **FR-003**: Process documentation MUST provide concrete examples with screenshots showing "done correctly" vs "not done" for at least 3 common scenarios (API fix, UI fix, data integration)

**Integration Testing:**

- **FR-004**: System MUST include automated integration test framework that verifies complete data flows across all system layers (database → backend → frontend → UI)
- **FR-005**: Integration tests MUST clearly indicate which layer failed when tests don't pass (e.g., "Backend API returned 500" vs "Frontend failed to call API" vs "Database has no data")
- **FR-006**: Integration test suite MUST cover at minimum: user login flow, dashboard data display, at least one data table rendering with actual data

**Manual Verification Process:**

- **FR-007**: Process MUST include step-by-step manual verification checklist for any feature, with specific commands/tools to use (curl examples, browser dev tools instructions)
- **FR-008**: Manual verification checklist MUST include these steps as minimum: verify database has data (SQL query example), verify API returns data (curl command), verify frontend receives data (browser network tab), verify user sees data (screenshot)
- **FR-009**: Process MUST provide time estimates for manual verification (e.g., "simple bug fix: 5-10 minutes", "new feature: 20-30 minutes") to set expectations

**Tool Selection Guidance:**

- **FR-010**: Documentation MUST provide decision tree for when to use MCP tools vs AGENTS vs manual verification
- **FR-011**: MCP tool guidance MUST include: what MCP is, when to use it (systematic multi-endpoint verification), concrete example usage commands
- **FR-012**: AGENTS guidance MUST include: what AGENTS are, when to use them (complex multi-step analysis), example scenarios where they add value vs overcomplicate
- **FR-013**: Guidance MUST explicitly state when tools are NOT needed (e.g., "for simple one-line fixes, manual curl test is sufficient")

**Smoke Testing:**

- **FR-014**: System MUST include pre-deployment smoke test suite with exactly 7 critical tests that execute in <5 minutes total: (1) system health check, (2) database connectivity and data validation, (3) user login flow, (4) dashboard loads with data, (5) critical APIs functional, (6) frontend assets load, (7) at least one data table renders with actual data
- **FR-015**: Smoke test MUST fail clearly when core functionality is broken, with specific error message indicating what's wrong (e.g., "Dashboard API returns no data - check backend logs" not just "test failed")

**Documentation Requirements:**

- **FR-016**: All process documentation MUST be in Chinese (用户主要语言是中文)
- **FR-017**: Documentation MUST include troubleshooting section for common failure modes: "API returns 500", "Frontend shows no data", "Database connection fails"
- **FR-018**: Documentation MUST be stored in project repository in easily discoverable location (e.g., `/docs/development-process/`)

### Key Entities

- **Development Checklist**: Step-by-step checklist for "Definition of Done" that developers follow for every feature/bug fix, including unit tests, integration tests, manual verification steps
- **Integration Test Suite**: Automated tests that verify complete data flows across system layers, with clear pass/fail results and layer-specific failure messages
- **Tool Selection Decision Tree**: Flowchart/document helping developers choose between MCP tools, AGENTS, or manual verification based on task characteristics
- **Smoke Test Checklist**: Quick pre-deployment verification checklist (<5 min) that catches obvious breaks in core functionality
- **Process Documentation**: Comprehensive guide explaining the full development workflow from task start to deployment, with examples and troubleshooting

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After implementing new process, 90% of features marked as "complete" are verifiably functional from end-user perspective (user can complete intended task and see expected results)
- **SC-002**: Integration test suite detects at least 80% of integration breaks before they reach manual testing, reducing wasted verification time
- **SC-003**: Time to verify a feature is complete increases by <30% despite additional verification steps (process adds thoroughness without excessive overhead)
- **SC-004**: Number of "thought it was done but actually broken" incidents decreases by 75% within one month of adopting new process
- **SC-005**: Developers can answer "Is this feature fully functional?" with confidence, citing specific test results or verification steps, rather than guessing or assuming
- **SC-006**: Pre-deployment smoke test catches 100% of "critical path broken" issues (login fails, dashboard completely non-functional) before deployment
- **SC-007**: 90% of developers follow the documented process without requiring additional clarification or guidance after initial training

## Dependencies & Assumptions

**Dependencies:**
- Existing web application architecture (FastAPI backend, Vue 3 frontend, PostgreSQL/TDengine databases) remains unchanged
- Developers have basic knowledge of HTTP API testing tools (curl or httpie), browser dev tools, and SQL queries
- Existing unit test framework (pytest) continues to be used
- Playwright will be installed for browser automation (Python support required)

**Assumptions:**
- Team is willing to invest initial time (estimated 2-3 days) to set up integration test framework and document process
- Current 90% non-functional state has TWO root causes: (1) lack of verification process (this feature addresses), and (2) actual code bugs requiring fixes (out of scope, see Root Cause Analysis above)
- Database contains or can be populated with test data for verification purposes
- Developers have access to all system components (database, backend, frontend) for local testing
- Fixing the 8 identified bugs (BUG-NEW-001 through BUG-NEW-008) will be handled in a separate implementation effort, potentially using the new verification process established by this feature

## Out of Scope

**Explicitly OUT OF SCOPE for this feature**:

- **Fixing existing bugs**: The 8 bugs identified in Root Cause Analysis (BUG-NEW-001 to BUG-NEW-008) require separate implementation
  - Watchlist API endpoint mismatch (BUG-NEW-005)
  - Technical Analysis MySQL dependency removal (BUG-NEW-003)
  - Dashboard concept stocks implementation (BUG-NEW-001)
  - ETF API endpoint alignment (BUG-NEW-007)
  - Other data handling and UI issues (BUG-NEW-002, 004, 006, 008)
- Completely rewriting existing tests or features (focus is on process, not code rewrite)
- Implementing CI/CD pipeline (though process should be CI/CD-compatible)
- Performance testing or load testing (focus is functional correctness, not performance)
- Refactoring existing codebase architecture (work within current structure)
- Training on basic development tools (assume developers know git, HTTP clients, browser dev tools)

## Decisions Made

### Process Rollout Approach
**Decision**: Full adoption immediately - all features use new process

**Rationale**: Given the severity of the current issue (90% of features non-functional), the team has chosen to prioritize rapid improvement over cautious iteration. The entire team will learn the new approach together, with comprehensive documentation and training support to mitigate risks.

**Implications**:
- All new work (features and bug fixes) must follow the new process starting immediately
- Team will receive intensive training on Definition of Done, integration testing, and verification checklists
- Higher initial learning curve but faster path to resolving the 90% non-functional issue
- Process will be monitored closely in first 2 weeks with adjustments made as needed

---

### Integration Test Technology
**Decision**: Full browser automation (Playwright/Selenium)

**Rationale**: Since the core problem is that features appear functional in isolation but fail in real-world usage, full browser automation is necessary to catch actual integration issues that simpler testing would miss. The slower test execution time (5-10 seconds per test) is acceptable given the current quality crisis.

**Implications**:
- Integration test suite will use Playwright for browser automation
- Tests will exercise complete stack: database → backend API → frontend → real browser rendering
- Test infrastructure requires browser installation and maintenance
- Slower test execution but higher confidence that features actually work end-to-end
- Critical for catching the "UI shows but no data" type issues currently plaguing the system

---

### MCP Tool Adoption
**Decision**: Mandatory - all API verification must use MCP tools

**Rationale**: To ensure systematic and thorough API verification, MCP tools will be mandatory for all API-related work. This ensures consistency in verification practices across the team and prevents under-verification that contributed to current issues.

**Implications**:
- Team must learn MCP tools immediately (training and documentation will be provided)
- All API verification steps in the process checklist will reference specific MCP tool commands
- Some overhead for simple tasks, but benefit is systematic verification preventing "thought it worked but didn't" issues
- MCP usage examples will be included in all process documentation
- Team can use simplified MCP commands for simple cases and comprehensive MCP workflows for complex multi-endpoint scenarios

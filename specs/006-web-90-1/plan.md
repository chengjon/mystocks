# Implementation Plan: Web Application Development Methodology Improvement

**Branch**: `006-web-90-1` | **Date**: 2025-10-29 | **Spec**: [spec.md](/opt/claude/mystocks_spec/specs/006-web-90-1/spec.md)

## Summary

This project addresses the critical issue that 90% of web application features are non-functional despite code being technically correct. The root cause is a development methodology that focuses on code correctness rather than functional usability.

**Primary Requirement**: Establish a comprehensive development and verification process that ensures features work end-to-end from user perspective, not just pass code-level tests.

**Technical Approach**:
1. Create clear "Definition of Done" process documentation (in Chinese)
2. Implement Playwright-based browser automation for integration testing
3. Mandate MCP tools for systematic API verification
4. Establish manual verification checklists with time estimates
5. Create quick pre-deployment smoke tests

**Key Decision**: Full immediate adoption of new process across all work (features and bug fixes) to rapidly address the 90% non-functional crisis.

## Technical Context

**Project Type**: Process/Documentation improvement (non-code deliverable)
**Language/Version**: Documentation in Chinese (Markdown), Test automation in Python 3.8+
**Primary Dependencies**:
- Playwright (browser automation)
- pytest (existing unit test framework)
- MCP tools (API verification)
- FastAPI (existing backend framework)
- Vue 3 (existing frontend framework)

**Storage**: N/A (documentation project, uses existing PostgreSQL/TDengine)
**Testing**: Playwright for end-to-end tests, pytest for integration tests
**Target Platform**: Linux server (backend), Modern browsers (frontend testing)

**Performance Goals**:
- Integration test execution: 5-10 seconds per test (acceptable for quality gains)
- Manual verification: <30 minutes for complex features, 5-10 minutes for simple fixes
- Smoke tests: <5 minutes total execution time

**Constraints**:
- Must work within existing architecture (FastAPI + Vue 3 + PostgreSQL/TDengine)
- Documentation must be in Chinese for team accessibility
- Process must add <30% overhead to feature completion time
- Cannot disrupt ongoing development work during rollout

**Scale/Scope**:
- 1 web application (MyStocks quantitative trading system)
- ~10-15 features requiring end-to-end verification
- Team of 3-5 developers learning new process
- 2-3 days initial setup investment

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Alignment with Constitution Principles

#### ✅ **1. Configuration-Driven Principle**
- **Status**: PASS
- **Rationale**: This is a process improvement project, not infrastructure change. Existing configuration-driven architecture remains unchanged.
- **Action**: None required

#### ✅ **2. Data Classification Storage Principle**
- **Status**: PASS
- **Rationale**: No changes to data storage strategy. Project focuses on development process, not data architecture.
- **Action**: None required

#### ✅ **3. Layered Architecture Principle**
- **Status**: PASS
- **Rationale**: Process documentation and testing framework respect existing architecture layers (database → backend → frontend → UI).
- **Action**: Integration tests will explicitly verify layer boundaries

#### ✅ **4. Intelligent Routing Principle**
- **Status**: PASS
- **Rationale**: No changes to DataManager or routing logic. Process ensures existing routing is properly tested.
- **Action**: None required

#### ✅ **5. Complete Observability Principle**
- **Status**: **ENHANCED**
- **Rationale**: New process IMPROVES observability by adding:
  - Integration test results showing layer-specific failures
  - Manual verification checklists with explicit checkpoints
  - Smoke test results identifying specific failure modes
- **Action**: Ensure monitoring of test suite execution and failure patterns

#### ✅ **6. Security and Fault Tolerance Principle**
- **Status**: PASS
- **Rationale**: Process improvements enhance fault detection without changing security mechanisms.
- **Action**: Manual verification checklist includes security checks (no passwords in responses, proper authentication)

### Documentation Standards Compliance

####

 ✅ **Document Types**
- **Status**: PASS
- **Deliverables**:
  1. Process Documentation (开发流程文档) - for developers
  2. Tool Selection Guide (工具选择指南) - for all team members
  3. Definition of Done Checklist (完成标准检查清单) - for developers
  4. Smoke Test Checklist (冒烟测试清单) - for team leads/QA
  5. Integration Test Suite Documentation (集成测试文档) - for developers/QA

#### ✅ **Chinese Language Requirement**
- **Status**: PASS
- **All documentation will be in Chinese per FR-016**

### Code Standards Compliance

#### ✅ **Testing Requirements**
- **Status**: **ENHANCED**
- **Current**: 42 unit tests (85% pass rate), focus on API correctness
- **New**: Adding Playwright integration tests covering end-to-end flows
- **Target**: 80% of integration breaks detected before manual testing (SC-002)

#### ✅ **Automation**
- **Status**: PASS
- **CI/CD Integration**: Process is CI/CD-compatible (though pipeline implementation is out of scope per spec)
- **Automated Tests**: Playwright suite will run automatically

### Change Management Compliance

#### ✅ **Minimal Change Principle**
- **Status**: PASS
- **Rationale**: No code changes to existing features. Only adding:
  - Process documentation
  - Test infrastructure (Playwright setup)
  - Verification checklists
- **Scope**: Documentation and tooling additions, no refactoring

#### ✅ **Layered Verification**
- **Status**: PASS (for test code)
- **AI Self-Verification**: Test code will include syntax checks, dependency validation
- **Automated Testing**: Integration tests will have their own unit tests
- **Human Review**: Team lead (JohnC) will review process documentation before rollout

#### ✅ **Architecture Compliance**
- **Status**: PASS
- **No Protected Modules Modified**: This project does not touch:
  - Core trading modules
  - Database schemas
  - Risk/position management
  - Configuration files
- **Focus**: External process documentation and testing tools only

### Constitution Check Result: ✅ **PASS**

**Summary**: All constitution principles are satisfied. This process improvement project:
1. Works within existing architecture without modifications
2. Enhances observability and quality assurance
3. Follows documentation standards with Chinese language requirement
4. Adheres to minimal change principle (only adding documentation and tests)
5. Does not touch any protected core modules

**No violations to justify**. Project may proceed to Phase 0 research.

---

## Project Structure

### Documentation (this feature)

```
specs/006-web-90-1/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (Phase 0-1 output)
├── research.md          # Phase 0: Technology research and best practices
├── process-framework.md # Phase 1: "Definition of Done" framework design
├── quickstart.md        # Phase 1: Quick start guide for developers
├── contracts/           # Phase 1: Checklist templates and test examples
│   ├── definition-of-done-checklist.md
│   ├── manual-verification-checklist.md
│   ├── smoke-test-checklist.md
│   ├── tool-selection-decision-tree.md
│   └── playwright-test-examples/
└── tasks.md             # Phase 2: Implementation tasks (NOT created by /speckit.plan)
```

### Deliverable Locations (repository root)

**Note**: This is a process improvement project. Deliverables are documentation and test infrastructure, not source code.

```
docs/
├── development-process/      # FR-018: Process documentation location
│   ├── README.md            # Overview and quick links
│   ├── definition-of-done.md   # FR-001, FR-002: Complete DoD definition
│   ├── manual-verification-guide.md  # FR-007, FR-008, FR-009: Step-by-step manual checks
│   ├── tool-selection-guide.md       # FR-010, FR-011, FR-012, FR-013: MCP/AGENTS/Manual
│   ├── smoke-test-guide.md          # FR-014, FR-015: Quick pre-deployment checks
│   ├── troubleshooting.md           # FR-017: Common failure modes
│   └── examples/                    # FR-003: Concrete examples with screenshots
│       ├── api-fix-example.md
│       ├── ui-fix-example.md
│       └── data-integration-example.md

tests/
├── integration/                      # FR-004, FR-005, FR-006: Playwright tests
│   ├── conftest.py                  # Playwright fixtures and setup
│   ├── test_user_login_flow.py      # FR-006: User login end-to-end
│   ├── test_dashboard_data_display.py  # FR-006: Dashboard data rendering
│   ├── test_data_table_rendering.py    # FR-006: At least one data table
│   └── utils/
│       ├── browser_helpers.py
│       └── layer_validation.py      # FR-005: Detect which layer failed

web/
├── backend/                          # Existing backend (no changes)
│   └── tests/                       # Existing pytest tests (no changes)
└── frontend/                        # Existing frontend (no changes)
    └── tests/                       # Existing frontend tests (no changes)
```

**Structure Decision**: This project creates NEW documentation directory (`docs/development-process/`) and NEW integration test directory (`tests/integration/`) without modifying existing code or test structures. All deliverables are additive, ensuring zero disruption to current development workflow during rollout.

## Complexity Tracking

*This section documents constitution violations that require justification. Currently: NONE*

**Status**: No violations detected. Project fully complies with constitution.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

---

## Phase 0: Research & Technology Selection

**Objective**: Resolve unknowns in Technical Context and establish best practices for process improvement and testing framework.

### Research Tasks

#### Research 1: Playwright vs Selenium for Python/FastAPI/Vue3 Stack
**Question**: Which browser automation framework best integrates with our existing FastAPI backend and Vue 3 frontend for end-to-end testing?

**Key Evaluation Criteria**:
- Python integration quality
- Vue 3 SPA testing capabilities
- Network interception for API verification
- Execution speed (target: 5-10 seconds per test)
- Debugging experience
- CI/CD compatibility
- Chinese language documentation availability

**Expected Output**: Comparison matrix with recommendation (likely Playwright given better async support and modern SPA testing)

---

#### Research 2: MCP Tools for FastAPI API Verification
**Question**: What specific MCP tools/commands are most effective for systematic API verification in FastAPI applications?

**Key Evaluation Criteria**:
- FastAPI OpenAPI integration
- Authentication handling (JWT tokens)
- Multi-endpoint testing workflows
- Error reporting clarity
- Learning curve for team
- Chinese language resources

**Expected Output**: List of recommended MCP tools/commands with concrete usage examples for MyStocks API endpoints

---

#### Research 3: Definition of Done Best Practices in Agile Teams
**Question**: What are proven "Definition of Done" frameworks that balance thoroughness with development velocity?

**Key Evaluation Criteria**:
- Checklist structure and completeness
- Time overhead (target: <30% increase)
- Adoption patterns in small teams (3-5 developers)
- Visual verification methods (screenshots, screen recordings)
- Integration with existing workflow tools

**Expected Output**: Sample DoD templates adapted to quantitative trading domain with time estimates per checklist item

---

#### Research 4: Manual Verification Efficiency Patterns
**Question**: How can manual verification be streamlined without sacrificing quality, especially for API + UI verification?

**Key Evaluation Criteria**:
- Curl command templates for API testing
- Browser DevTools workflow for frontend debugging
- SQL query templates for data verification
- Screenshot/screen recording tools
- Time-saving shortcuts and browser extensions

**Expected Output**: Optimized verification workflow with tool recommendations and estimated time per step

---

#### Research 5: Smoke Test Design for Web Applications
**Question**: What are effective smoke test patterns that catch critical breaks in <5 minutes?

**Key Evaluation Criteria**:
- Test selection criteria (which tests to include)
- Execution orchestration (sequential vs parallel)
- Failure reporting clarity
- Integration with deployment pipeline
- Historical data on smoke test effectiveness

**Expected Output**: Smoke test strategy with 5-7 critical tests covering login, dashboard, and core data flows

---

### Research Consolidation (research.md)

All findings will be consolidated into `/opt/claude/mystocks_spec/specs/006-web-90-1/research.md` with:
- **Decision**: Technology/approach chosen
- **Rationale**: Why this choice best fits our context
- **Alternatives Considered**: What else was evaluated and why rejected
- **Implementation Notes**: Specific setup steps, gotchas, and best practices

---

## Phase 1: Design & Documentation Artifacts

**Prerequisites**: `research.md` complete with all technology selections finalized

### Artifact 1: Process Framework Document (process-framework.md)

**Purpose**: Define the complete "Definition of Done" framework that developers will follow

**Contents**:
1. **Overview** (中文): What does "done" mean in new process
2. **Core Principles**: Functional usability > code correctness
3. **Verification Layers**:
   - Layer 1: Unit tests (existing pytest framework)
   - Layer 2: Integration tests (new Playwright suite)
   - Layer 3: Manual verification (new checklists)
   - Layer 4: Smoke tests (pre-deployment gates)
4. **Workflow Diagram**: Visual flow from "code written" to "deployed"
5. **Time Estimates**: Expected overhead per work type (bug fix, small feature, large feature)
6. **Rollout Plan**: Immediate full adoption strategy with 2-week adjustment period

---

### Artifact 2: Checklist Templates (contracts/)

**2a. Definition of Done Checklist** (`contracts/definition-of-done-checklist.md`)

Template structure:
```markdown
# 功能完成检查清单 (Definition of Done)

## 📋 适用范围
- ✅ Bug修复
- ✅ 功能增强
- ✅ 新功能开发

## ✅ 必须完成的验证步骤

### 1. 代码层 (5-10分钟)
- [ ] 代码已提交到feature分支
- [ ] 单元测试通过 (`pytest tests/unit/`)
- [ ] 代码格式检查通过 (`black`, `flake8`)
- [ ] 类型检查通过 (`mypy`)

### 2. API层 (10-15分钟)
- [ ] 使用MCP工具验证所有相关API端点
  - 命令示例: `mcp test --endpoint /api/data/dashboard`
- [ ] API返回正确的HTTP状态码 (200/201/204/400/401等)
- [ ] API返回数据结构符合预期 (使用JSON schema验证)
- [ ] 错误场景正确处理 (缺失参数、无效数据等)

### 3. 集成层 (自动执行, 5-10分钟)
- [ ] Playwright集成测试通过
  - 命令: `pytest tests/integration/test_*.py -v`
- [ ] 数据流完整: 数据库 → 后端 → 前端 → 用户界面
- [ ] 无层间断点 (测试报告明确指出通过的层)

### 4. 用户界面层 (10-20分钟)
- [ ] 在浏览器中手动访问功能
- [ ] 数据正确显示 (截图保存到 `docs/verification-screenshots/`)
- [ ] 无控制台错误 (F12 检查)
- [ ] 网络请求成功 (Network标签检查，无failed请求)
- [ ] 交互功能正常 (按钮点击、表单提交等)

### 5. 数据验证层 (5-10分钟)
- [ ] 使用SQL查询确认数据库有数据
  - 示例: `SELECT * FROM table_name ORDER BY created_at DESC LIMIT 10;`
- [ ] 数据时效性检查 (最新数据不超过X分钟/小时)
- [ ] 数据完整性检查 (无NULL关键字段)

## 📊 完成标准
✅ **所有上述检查项必须通过，才能认为功能"完成"**

## ⏱️ 预计时间投入
- 简单Bug修复: 35-55分钟
- 中等功能: 50-80分钟
- 复杂功能: 90-120分钟

## 📝 记录
- 验证人: _______
- 验证日期: _______
- 截图位置: _______
```

**2b. Manual Verification Checklist** (`contracts/manual-verification-checklist.md`)
- Step-by-step commands for curl, browser DevTools, SQL queries
- Expected outputs with screenshots
- Common failure modes and how to recognize them

**2c. Smoke Test Checklist** (`contracts/smoke-test-checklist.md`)
- 5-7 critical tests
- Pass/fail criteria
- Execution time per test
- Total time budget: <5 minutes

**2d. Tool Selection Decision Tree** (`contracts/tool-selection-decision-tree.md`)
- Flowchart: Task type → Recommended tool
- When to use MCP (mandatory for all API work per FR-010)
- When to use AGENTS (complex multi-source data verification)
- When manual is sufficient (simple one-line fixes)

**2e. Playwright Test Examples** (`contracts/playwright-test-examples/`)
- `example_login_flow.py`: Complete user login test
- `example_dashboard_data.py`: Dashboard data display test
- `example_layer_failure_detection.py`: Demonstrates how tests pinpoint failing layer

---

### Artifact 3: Developer Quick Start (quickstart.md)

**Purpose**: Get developers productive with new process in <30 minutes

**Contents**:
1. **5-Minute Overview** (中文): What changed and why
2. **Setup** (10 minutes):
   - Install Playwright: `pip install playwright && playwright install`
   - Install MCP tools: [specific commands from research]
   - Verify setup: Run example integration test
3. **Your First Verification** (15 minutes):
   - Walk through simple bug fix verification
   - Use checklist
   - Run integration test
   - Manual verification steps
   - Mark as "done"
4. **Common Questions**:
   - "What if integration test fails?" → Check which layer, fix that layer
   - "What if verification takes >30 minutes?" → Use "critical path" subset
   - "What if I'm not sure how to verify?" → Consult tool selection guide

---

### Artifact 4: Integration Test Suite Setup

**4a. Playwright Configuration** (`tests/integration/conftest.py`)
- Browser setup (headless vs headed)
- Base URL configuration
- Authentication fixtures (JWT token handling)
- Screenshot on failure
- Layer-specific assertions

**4b. Core Integration Tests** (`tests/integration/`)
- `test_user_login_flow.py`: FR-006 requirement
- `test_dashboard_data_display.py`: FR-006 requirement
- `test_data_table_rendering.py`: FR-006 requirement

Each test includes:
```python
def test_dashboard_data_display(page, authenticated_session):
    """
    验证仪表板数据显示的完整流程

    验证层次:
    1. 数据库层: 确认数据存在
    2. 后端API层: 确认API返回数据
    3. 前端层: 确认前端请求API
    4. UI层: 确认用户看到数据
    """
    # Layer 1: Database check
    assert database_has_data("dashboard_summary")

    # Layer 2: API check
    api_response = requests.get("/api/data/dashboard/summary")
    assert api_response.status_code == 200
    assert len(api_response.json()["data"]) > 0

    # Layer 3 + 4: Frontend + UI check
    page.goto("/dashboard")
    page.wait_for_selector("[data-testid='dashboard-summary']")

    # FR-005: Clearly indicate which layer failed
    assert page.locator("[data-testid='data-table']").count() > 0, \
        "UI Layer Failed: Data table not rendered (frontend may not be calling API or rendering data)"
```

---

### Agent Context Update

**Script**: `.specify/scripts/bash/update-agent-context.sh claude`

**New Technologies Added**:
- Playwright (browser automation framework)
- MCP tools (API verification)

**Context File Location**: Will detect and update Claude-specific context file

---

## Next Steps

**Phase 2 (Separate Command)**: Run `/speckit.tasks` to generate implementation tasks from this plan.

**Expected Task Categories**:
1. **Setup Tasks** (1-2 hours):
   - Install Playwright and MCP tools
   - Create directory structure for documentation
   - Set up integration test infrastructure

2. **Documentation Tasks** (6-8 hours):
   - Write Definition of Done documentation (Chinese)
   - Create manual verification guide with screenshots
   - Write tool selection guide
   - Create smoke test checklist
   - Write troubleshooting guide with common failure modes

3. **Integration Test Tasks** (4-6 hours):
   - Implement Playwright configuration
   - Write user login flow test
   - Write dashboard data display test
   - Write data table rendering test

4. **Training Tasks** (2-3 hours):
   - Create quickstart guide
   - Prepare example verification walkthrough
   - Schedule team training session

5. **Rollout Tasks** (1-2 hours):
   - Present new process to team
   - Run first verification with team member
   - Collect feedback and adjust
   - Monitor adoption in first 2 weeks

**Total Estimated Effort**: 14-21 hours (spread over 2-3 days per spec assumptions)

---

**Report**: Branch `006-web-90-1`, Implementation Plan complete at `/opt/claude/mystocks_spec/specs/006-web-90-1/plan.md`. Ready for Phase 0 research and Phase 1 artifact generation (continuing in this command execution).

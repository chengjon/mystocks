# Tasks: 系统规范化改进

**Input**: Design documents from `/opt/claude/mystocks_spec/specs/006-0-md-1/`
**Prerequisites**: plan.md, spec.md (5 user stories with priorities)
**Branch**: `006-0-md-1`

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- Includes exact file paths in descriptions

---

## Phase 0: Research & Investigation

**Purpose**: Complete all research tasks before implementation begins

**Priority**: P1 tasks must complete before any other work can begin

### Research Tasks

- [ ] T001 [P] [R1] Analyze byapi_adapter business scope - Read `adapters/byapi_adapter.py`, search for non-business keywords ("期货"/"期权"/"外汇"/"黄金"/"美股"/"futures"/"options"/"forex"/"gold"), check `adapters/byapi/` directory, decide: keep or delete (2 hours)
- [ ] T002 [P] [R2] Create core documents list - Identify 10-15 core MD files needing metadata (README.md, CHANGELOG_v2.1.md, QUICKSTART.md, adapters/README.md, web/README.md, monitoring/grafana_setup.md, etc.), check current metadata status (1 hour)
- [ ] T003 [P] [R3] Create core Python files list - Identify 20 core .py files needing header comments (interfaces/, factory/, manager/, core.py, unified_manager.py, monitoring.py, adapters/核心适配器), prioritize by layer (1.5 hours)
- [ ] T004 [P] [R4] Create test file rename plan - Find all test files not starting with `test_`, plan renames (old_name → new_name), identify import fixes needed (1 hour)
- [ ] T005 [R5] Validate database connections - Check `.env.example` and `web/backend/app/core/config.py`, test MySQL connection (mystocks DB + key tables), test PostgreSQL (mystocks + mystocks_monitoring), test TDengine (time-series supertables), test Redis cache, document all connection issues (2 hours)
- [ ] T006 [R6] Validate web page data APIs - List 10 key pages and their API dependencies (`/api/auth/login`, `/api/tdx/*`, `/api/market/*`, `/api/data/*`, `/api/indicators/*`, `/api/system/*`), test each API with curl, check response format, verify DB queries, test pages in browser, document display issues (2.5 hours)
- [ ] T007 [P] [R7] Research .gitignore optimization - Run `git status` to identify ignored files showing, review Python/Node.js/.gitignore best practices, check if subdirectories need separate .gitignore (0.5 hours)
- [ ] T008 [R8] Plan historical data backup - Identify non-business tables (if byapi marked for deletion), create mysqldump/pg_dump commands, define backup storage location/naming, define deletion verification SOP (1 hour)

**Output**: Create `research.md` with 8 sections (R1-R8 findings)

**Checkpoint**: Research complete - all decisions documented, ready for design phase

---

## Phase 1: Design & Contracts

**Purpose**: Create templates and contracts based on research findings

**Dependencies**: Phase 0 must be complete

### Design Tasks

- [ ] T009 [P] [D1] Design document metadata template - Create "文档元数据规范" section in `quickstart.md` with 5-field template (创建人/版本/批准日期/最后修订/修订内容), based on R2 findings (0.5 hours)
- [ ] T010 [P] [D2] Design Python header comment template - Create "Python头注释规范" section in `quickstart.md` with 7-component template (encoding/功能/作者/日期/依赖/注意事项/版权), based on R3 findings (0.5 hours)
- [ ] T011 [P] [D3] Create test file rename contract - Create `contracts/test-file-naming.md` with rename mapping, import fix list, validation command (`pytest test_*.py -v`), acceptance criteria, based on R4 findings (0.5 hours)
- [ ] T012 [P] [D4] Create database validation contract - Create `contracts/database-validation.md` with connection parameters for 4 DBs, health check SQL queries, key table lists, error code handling, fix verification checklist, based on R5 findings (1 hour)
- [ ] T013 [P] [D5] Create web API health check contract - Create `contracts/api-health-check.md` with 10 key pages + API endpoints, curl health check commands, expected response formats, common error codes, troubleshooting flowchart, based on R6 findings (1 hour)
- [ ] T014 [P] [D6] Create .gitignore configuration contract - Create `contracts/gitignore-rules.md` with must-exclude file types, general vs specific rules, subdirectory .gitignore strategy, validation command (`git status`), based on R7 findings (0.5 hours)

**Output**: Updated `quickstart.md` + 4 contract files in `contracts/` directory

**Checkpoint**: All templates and contracts ready - implementation can begin

---

## Phase 2: User Story 1 - 业务范围限定和清理 (Priority: P1) 🎯

**Goal**: Ensure system only handles business-scope data (A股, 股指期货, optional H股), remove out-of-scope code

**Independent Test**: Keyword search for "期货"/"期权"/"外汇"/"黄金"/"美股"/"futures"/"options"/"forex"/"gold" returns 0 results (除了A股+股指期货注释), adapters only contain business-scope code

**Dependencies**: Phase 0 (R1, R8) and Phase 1 (D4 for backup verification) must be complete

### Implementation Tasks

- [ ] T015 [US1] Execute historical data backup (if needed) - If byapi_adapter marked for deletion in R1, run mysqldump/pg_dump per R8 SOP, verify backup integrity, store backup with timestamp (1 hour)
- [ ] T016 [US1] Remove/move byapi_adapter code - If non-business: move `adapters/byapi_adapter.py` and `adapters/byapi/` to `temp/`, add migration note with reason and 30-day observation period (0.5 hours)
- [ ] T017 [US1] Clean byapi references in code - Search for "byapi" imports/references in `factory/data_source_factory.py` and other files, comment out or remove, add TODO comments if needed (0.5 hours)
- [ ] T018 [US1] Update table_config.yaml - If byapi had table configs, backup `table_config.yaml`, remove non-business table definitions, verify YAML syntax (0.5 hours)
- [ ] T019 [US1] Add A+H interface placeholders - In `interfaces/data_source.py` or relevant adapters, add method stubs with docstrings like "预留给后续A+H关联功能 - TODO: implement cross-market linking" (0.5 hours)
- [ ] T020 [US1] Document business scope in config - Add/update `config/business_scope.yaml` or similar, clearly list supported markets (A股各板块, 股指期货, H股[可选]), add comments explaining exclusions (0.5 hours)
- [ ] T021 [US1] Verify scope cleanup - Run keyword search across all files (`grep -r "期货" --exclude-dir=temp`, `grep -r "futures" --exclude-dir=temp`), verify 0 unexpected results, update documentation if A+H placeholders appear in results (1 hour)

**Acceptance**:
- SC-001: 代码库中不存在期货/期权/外汇/黄金/美股相关代码 (通过关键词搜索验证)
- FR-001 to FR-005: Business scope requirements met
- Database backup completed if data deletion occurred

**Checkpoint**: Business scope is clean and well-documented

---

## Phase 3: User Story 2 - 文档标记规范化 (Priority: P1) 🎯

**Goal**: All MD documents contain standardized metadata (创建人/版本/批准日期/最后修订/修订内容)

**Independent Test**: Script checks all 10-15 core .md files for 5 metadata fields, generates compliance report showing 100%

**Dependencies**: Phase 1 (D1 template) must be complete

### Implementation Tasks

- [ ] T022 [P] [US2] Add metadata to root documentation - Update `README.md`, `CHANGELOG_v2.1.md`, `QUICKSTART.md`, `DELIVERY_v2.1.md` with 5-field metadata per D1 template (4 files × 5 min = 20 min)
- [ ] T023 [P] [US2] Add metadata to adapters documentation - Update `adapters/README.md`, `adapters/README_TDX.md` with metadata (2 files × 5 min = 10 min)
- [ ] T024 [P] [US2] Add metadata to web documentation - Update `web/README.md`, `web/PORTS.md`, `web/TDX_SETUP_COMPLETE.md` with metadata (3 files × 5 min = 15 min)
- [ ] T025 [P] [US2] Add metadata to monitoring documentation - Update `monitoring/grafana_setup.md`, `monitoring/MANUAL_SETUP_GUIDE.md`, `monitoring/生成监控数据说明.md` with metadata (3 files × 5 min = 15 min)
- [ ] T026 [P] [US2] Add metadata to specs documentation - Update `specs/005-tdx-web-tdx/spec.md`, `specs/005-tdx-web-tdx/README.md` with metadata (2 files × 5 min = 10 min)
- [ ] T027 [US2] Create metadata validation script - Create `utils/validate_doc_metadata.py` script to check .md files for 5 required fields (创建人/版本/批准日期/最后修订/修订内容), output compliance report (30 min)
- [ ] T028 [US2] Run metadata validation - Execute validation script on core documents, verify 100% compliance, fix any missing fields (15 min)

**Acceptance**:
- SC-002: All core MD documents (10-15) contain complete 5-field metadata (100% compliance)
- FR-006 to FR-009: Documentation metadata requirements met
- Validation script available for future use

**Checkpoint**: Documentation is fully standardized with traceable metadata

---

## Phase 4: User Story 3 - Python代码注释规范化 (Priority: P2)

**Goal**: All Python programs follow unified comment standards (file header + docstrings)

**Independent Test**: Static analysis tool checks all 20 core .py files for: 1) file header with 7 components, 2) class/function docstrings, generates compliance report

**Dependencies**: Phase 1 (D2 template) must be complete

### Implementation Tasks - Interfaces Layer (Highest Priority)

- [ ] T029 [P] [US3] Add header to interfaces/data_source.py - Add 7-component header comment per D2 template (功能: 定义统一数据源接口IDataSource, 作者: JohnC & Claude, 依赖: pandas/numpy, etc.) (10 min)

### Implementation Tasks - Factory Layer

- [ ] T030 [P] [US3] Add header to factory/data_source_factory.py - Add 7-component header (功能: 数据源工厂模式实现, 支持8种适配器) (10 min)

### Implementation Tasks - Manager Layer

- [ ] T031 [P] [US3] Add header to manager/unified_data_manager.py - Add 7-component header (功能: 统一数据访问管理, 参数标准化) (10 min)

### Implementation Tasks - Core Modules

- [ ] T032 [P] [US3] Add header to core.py - Add 7-component header (功能: 5层数据分类+智能路由) (10 min)
- [ ] T033 [P] [US3] Add header to unified_manager.py - Add 7-component header (功能: MyStocks统一管理器) (10 min)
- [ ] T034 [P] [US3] Add header to monitoring.py - Add 7-component header (功能: 监控和数据质量管理) (10 min)

### Implementation Tasks - Adapters (4 Core Adapters)

- [ ] T035 [P] [US3] Add header to adapters/akshare_adapter.py - Add 7-component header (功能: Akshare数据源适配器) (10 min)
- [ ] T036 [P] [US3] Add header to adapters/baostock_adapter.py - Add 7-component header (功能: Baostock数据源适配器) (10 min)
- [ ] T037 [P] [US3] Add header to adapters/tdx_adapter.py - Add 7-component header (功能: 通达信TDX数据源适配器) (10 min)
- [ ] T038 [P] [US3] Add header to adapters/financial_adapter.py - Add 7-component header (功能: 财务数据适配器) (10 min)
- [ ] T039 [P] [US3] Add header to adapters/customer_adapter.py - Add 7-component header (功能: 自定义数据源适配器) (10 min)
- [ ] T040 [P] [US3] Add header to adapters/data_source_manager.py - Add 7-component header (功能: 数据源统一管理) (10 min)

### Implementation Tasks - Additional Core Files (6 more to reach 20 total)

- [ ] T041 [P] [US3] Add headers to db_manager files - Add headers to key database manager files (2 files × 10 min = 20 min)
- [ ] T042 [P] [US3] Add headers to data_access files - Add headers to database access layer files (2 files × 10 min = 20 min)
- [ ] T043 [P] [US3] Add headers to utils files - Add headers to key utility files like `utils/failure_recovery_queue.py`, `utils/tdx_server_config.py` (2 files × 10 min = 20 min)

### Validation Tasks

- [ ] T044 [US3] Create header validation script - Create `utils/validate_py_headers.py` to check .py files for 7-component headers and docstrings, output compliance report (30 min)
- [ ] T045 [US3] Run header validation - Execute validation on 20 core files, verify 100% compliance, fix any issues (20 min)
- [ ] T046 [US3] Verify technical term language - Check that technical terms (API, DataFrame, Token, Cache) kept in English, descriptions in Chinese per clarification answer (15 min)

**Acceptance**:
- SC-003: All 20 core Python files contain standard header comments (100% compliance)
- FR-010 to FR-014: Python comment standards requirements met
- Technical terms in English, descriptions in Chinese

**Checkpoint**: Python code is fully documented and maintainable

---

## Phase 5: User Story 4 - 文件和测试管理规范化 (Priority: P2)

**Goal**: Clean up unrelated files, unify test file naming (test_ prefix), optimize directory structure

**Independent Test**: Check root directory file list: 1) all test files start with test_, 2) temp files in temp/ directory, 3) core files clearly categorized

**Dependencies**: Phase 1 (D3 test rename contract) must be complete

### Setup Tasks

- [ ] T047 [US4] Create temp directory - Create `temp/` directory at repository root with README.md explaining purpose (5 min)

### Test File Rename Tasks

- [ ] T048 [US4] Rename test file simple_test.py - Move `adapters/simple_test.py` to `adapters/test_simple.py`, update any imports, run `pytest adapters/test_simple.py -v` to verify (5 min)
- [ ] T049 [US4] Verify all test files - Run `find . -name "*test*.py" -not -path "./temp/*"`, check all start with `test_`, identify any remaining violations (10 min)
- [ ] T050 [US4] Fix test imports if needed - If pytest failures found, fix import paths in renamed test files per D3 contract (15 min)
- [ ] T051 [US4] Run full test suite - Execute `pytest test_*.py -v` from repo root, verify 100% pass rate, document any failures (15 min)

### File Cleanup Tasks

- [ ] T052 [US4] Identify temp/unrelated files - Scan root directory for temp/unrelated files (*.tmp, old backups, experimental scripts), list candidates for temp/ (15 min)
- [ ] T053 [US4] Move files to temp directory - Move identified files to `temp/`, create `temp/MIGRATION_LOG.md` documenting: filename, original location, reason, observation period end date (20 min)
- [ ] T054 [US4] Verify directory structure - Check project follows clear structure (adapters/, core files, web/, specs/, docs/, tests/, temp/, utils/), document structure in README if missing (15 min)

**Acceptance**:
- SC-004: All test files (10+) start with test_ (100% compliance)
- SC-006: Root directory file count reduced ≥50%
- FR-015 to FR-019: File management requirements met
- All tests still passing after renames

**Checkpoint**: File organization is clean and pytest-compatible

---

## Phase 6: User Story 5 - .gitignore配置优化 (Priority: P3)

**Goal**: .gitignore correctly excludes unnecessary files (.env, __pycache__, *.log, IDE configs)

**Independent Test**: Run `git status` - should show 0 untracked files that should be ignored

**Dependencies**: Phase 1 (D6 .gitignore contract) must be complete

### Implementation Tasks

- [ ] T055 [US5] Backup current .gitignore - Copy `.gitignore` to `temp/.gitignore.backup` before modifications (2 min)
- [ ] T056 [US5] Update root .gitignore - Add/update rules per D6 contract: .env/.env.local, __pycache__/\*.pyc/\*.pyo/\*.pyd, \*.log/logs/, .vscode/.idea/\*.swp, temp/\*.tmp, .coverage/htmlcov/.pytest_cache/, !.env.example (10 min)
- [ ] T057 [US5] Create/update web/frontend/.gitignore - Add node_modules/, dist/, build/, .vscode/, .DS_Store (5 min)
- [ ] T058 [US5] Verify .env.example exists - Check `.env.example` has all required env vars without sensitive values, update if needed (10 min)
- [ ] T059 [US5] Test .gitignore effectiveness - Run `git status`, verify no __pycache__, \*.log, .env, or IDE files shown, remove any incorrectly tracked files with `git rm --cached` (15 min)
- [ ] T060 [US5] Document .gitignore rules - Add comments in .gitignore explaining each section (Python, Node.js, IDE, Logs, Temp, Security) (10 min)

**Acceptance**:
- SC-005: `git status` shows 0 should-be-ignored files
- FR-020 to FR-027: .gitignore requirements met
- .env.example available as template

**Checkpoint**: Git repository is clean and secure

---

## Phase 7: Database & API Validation + Fixes (Priority: P1) 🔧

**Goal**: Validate 4 database connections and fix Web page data display issues

**Independent Test**: All 4 databases pass connection tests, ≥80% of 10 key Web pages display data correctly

**Dependencies**: Phase 0 (R5, R6) and Phase 1 (D4, D5) must be complete

### Database Fix Tasks

- [ ] T061 [DB] Fix MySQL connection issues - Based on R5 findings, fix MySQL connection config in `.env`/`web/backend/app/core/config.py`, verify connection to mystocks DB, verify key tables accessible (30 min)
- [ ] T062 [DB] Fix PostgreSQL connection issues - Fix PostgreSQL config, verify mystocks DB and mystocks_monitoring DB connections, verify key tables (30 min)
- [ ] T063 [DB] Fix TDengine connection issues - Fix TDengine config, verify time-series DB connection, verify supertables accessible (30 min)
- [ ] T064 [DB] Fix Redis connection issues - Fix Redis config, verify cache service availability (15 min)
- [ ] T065 [DB] Create database health check script - Create `utils/check_db_health.py` to test all 4 databases per D4 contract, output status report (45 min)
- [ ] T066 [DB] Run database validation - Execute health check script, verify 100% pass rate per SC-009-NEW (15 min)

### Web API Fix Tasks

- [ ] T067 [P] [API] Fix authentication API - Fix `/api/auth/login` endpoint issues found in R6, verify login page works (30 min)
- [ ] T068 [P] [API] Fix TDX market data APIs - Fix `/api/tdx/*` endpoints, verify TDX行情页面 displays real-time quotes and K-lines (45 min)
- [ ] T069 [P] [API] Fix market data APIs - Fix `/api/market/*` endpoints, verify 市场行情页面 displays stock data (30 min)
- [ ] T070 [P] [API] Fix data query APIs - Fix `/api/data/*` endpoints, verify 数据查询页面 displays query results (30 min)
- [ ] T071 [P] [API] Fix indicator APIs - Fix `/api/indicators/*` endpoints, verify 指标计算页面 displays calculated indicators (30 min)
- [ ] T072 [P] [API] Fix system management APIs - Fix `/api/system/*` endpoints, verify 系统管理页面 works (20 min)
- [ ] T073 [API] Test remaining 4 key pages - Test and fix remaining 4 pages from 10-page list in R6 (4 pages × 20 min = 80 min)
- [ ] T074 [API] Create API health check script - Create `utils/check_api_health.py` to test 10 key page APIs per D5 contract, output status report (45 min)
- [ ] T075 [API] Run API validation - Execute API health check, verify ≥80% pass rate per SC-010-NEW, document any remaining issues (20 min)

### Integration Verification

- [ ] T076 [API] Browser end-to-end test - Test all 10 key pages in browser, verify data displays correctly, take screenshots of P1 pages working (30 min)
- [ ] T077 [API] Document fixes applied - Update `research.md` or create `WEB_PAGE_FIXES.md` documenting: problem found, root cause, fix applied, verification result (20 min)

**Acceptance**:
- SC-009-NEW: 4个数据库连接测试100%通过
- SC-010-NEW: 10个关键Web页面数据接口验证通过率 ≥ 80%
- SC-011-NEW: 所有P1级别Web页面数据显示问题得到修复

**Checkpoint**: Database connectivity and Web page data display issues resolved

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting multiple user stories

**Dependencies**: Desired user stories (at minimum US1-US2 for P1) must be complete

### Documentation Tasks

- [ ] T078 [P] [Polish] Update CHANGELOG_v2.1.md - Add section for 006-0-md-1 normalization improvements, list all changes (业务范围限定, 文档标记, 代码注释, 测试文件规范, .gitignore优化, 数据库/API修复) (20 min)
- [ ] T079 [P] [Polish] Update main README.md - Add/update sections on business scope, documentation standards, code comment standards, project structure (30 min)
- [ ] T080 [P] [Polish] Create NORMALIZATION_REPORT.md - Comprehensive report: what was normalized, before/after metrics, validation results, remaining TODOs (30 min)

### Verification Tasks

- [ ] T081 [Polish] Run all validation scripts - Execute metadata validation, header validation, test suite, database health check, API health check - generate combined report (20 min)
- [ ] T082 [Polish] Verify all success criteria - Check SC-001 through SC-012 from spec.md, document compliance status for each (30 min)
- [ ] T083 [Polish] Run quickstart validation - Follow QUICKSTART.md steps to verify system still works end-to-end after all changes (30 min)

### Final Cleanup

- [ ] T084 [Polish] Code review and cleanup - Review all modified files, remove debug comments, ensure consistent formatting (30 min)
- [ ] T085 [Polish] Check for leftover TODOs - Search for TODO comments added during normalization, prioritize for future work (15 min)
- [ ] T086 [Polish] Security audit - Verify .env excluded, no secrets in code, sensitive config in .env.example (15 min)

**Acceptance**:
- All validation scripts pass
- All P1 success criteria met
- Documentation updated
- System functional end-to-end

**Checkpoint**: System normalization complete and validated

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 0 (Research)**: No dependencies - START HERE
  - P1 research (R1, R5, R6, R8) must complete before P1 implementation
  - P2 research (R3, R4) can complete before P2 implementation
  - P3 research (R7) can complete before P3 implementation
- **Phase 1 (Design)**: Depends on Phase 0 research completion
  - All design tasks can run in parallel
- **Phase 2 (US1)**: Depends on Phase 0 (R1, R8) + Phase 1 (D4)
- **Phase 3 (US2)**: Depends on Phase 1 (D1) - Can run parallel with Phase 2
- **Phase 4 (US3)**: Depends on Phase 1 (D2) - Can run parallel with Phase 2/3
- **Phase 5 (US4)**: Depends on Phase 1 (D3) - Can run parallel with Phase 2/3
- **Phase 6 (US5)**: Depends on Phase 1 (D6) - Can run parallel with others
- **Phase 7 (DB/API)**: Depends on Phase 0 (R5, R6) + Phase 1 (D4, D5) - Critical for P1
- **Phase 8 (Polish)**: Depends on all desired user stories complete

### User Story Priority Execution

**P1 (Critical - Must Complete):**
1. Phase 0 → Phase 1 → Phase 2 (US1) + Phase 3 (US2) + Phase 7 (DB/API)
2. These address: business scope, documentation metadata, database/API fixes

**P2 (Important):**
3. Phase 4 (US3) + Phase 5 (US4)
4. These address: code comments, file organization

**P3 (Nice to Have):**
5. Phase 6 (US5)
6. This addresses: .gitignore optimization

**Minimum MVP**: Phase 0 + Phase 1 + Phase 2 + Phase 7 = Business scope clean + DB/API working

### Within Each Phase

- Research tasks (T001-T008): R1/R5/R6/R8 are P1 sequential (R5 depends on DB config), R2/R3/R4/R7 are P2/P3 parallel
- Design tasks (T009-T014): All can run in parallel after research
- US1 tasks (T015-T021): Sequential (backup → remove → clean → verify)
- US2 tasks (T022-T028): T022-T026 parallel (different files), T027-T028 sequential
- US3 tasks (T029-T046): T029-T043 all parallel (different files), T044-T046 sequential
- US4 tasks (T047-T054): T048 independent, T049-T051 sequential, T052-T054 sequential
- US5 tasks (T055-T060): Sequential (backup → update → test)
- DB/API tasks (T061-T077): T061-T064 parallel, T067-T072 parallel, others sequential
- Polish tasks (T078-T086): T078-T080 parallel, T081-T086 sequential

### Parallel Opportunities

**High Parallelism:**
- Phase 1: All 6 design tasks (T009-T014) can run in parallel
- Phase 3 (US2): 5 documentation update tasks (T022-T026) can run in parallel
- Phase 4 (US3): 15 header addition tasks (T029-T043) can run in parallel
- Phase 7 (DB): 4 database fix tasks (T061-T064) can run in parallel
- Phase 7 (API): 6 API fix tasks (T067-T072) can run in parallel
- Phase 8: 3 documentation tasks (T078-T080) can run in parallel

**Story-Level Parallelism:**
- After Phase 1 complete: US1, US2, US3, US4, US5 can all proceed in parallel (if team capacity allows)
- Recommended: Prioritize US1 (P1) and US7 (DB/API fixes) first, then US2 (P1), then US3/US4 (P2), finally US5 (P3)

---

## Parallel Example: User Story 3 (Python Headers)

```bash
# Launch all header addition tasks together (15 different files):
Task T029: "Add header to interfaces/data_source.py"
Task T030: "Add header to factory/data_source_factory.py"
Task T031: "Add header to manager/unified_data_manager.py"
Task T032: "Add header to core.py"
Task T033: "Add header to unified_manager.py"
Task T034: "Add header to monitoring.py"
Task T035: "Add header to adapters/akshare_adapter.py"
Task T036: "Add header to adapters/baostock_adapter.py"
Task T037: "Add header to adapters/tdx_adapter.py"
Task T038: "Add header to adapters/financial_adapter.py"
Task T039: "Add header to adapters/customer_adapter.py"
Task T040: "Add header to adapters/data_source_manager.py"
Task T041: "Add headers to 2 db_manager files"
Task T042: "Add headers to 2 data_access files"
Task T043: "Add headers to 2 utils files"
# All these can execute in parallel - different files, no conflicts
```

---

## Implementation Strategy

### MVP First (P1 Only - 业务范围 + 文档标记 + 数据库/API修复)

1. **Phase 0**: Complete R1, R2, R5, R6, R8 research (P1 research tasks) - ~7.5 hours
2. **Phase 1**: Complete all design tasks (D1-D6) - ~4 hours
3. **Phase 2**: Complete US1 (Business scope cleanup) - ~4.5 hours
4. **Phase 3**: Complete US2 (Documentation metadata) - ~2 hours
5. **Phase 7**: Complete DB/API validation and fixes - ~6.5 hours
6. **STOP and VALIDATE**: Run validation scripts, verify SC-001, SC-002, SC-009-NEW through SC-011-NEW
7. **Total MVP time**: ~24.5 hours

**MVP Deliverables:**
- ✅ Business scope cleaned and documented
- ✅ Core documentation with metadata
- ✅ All 4 databases connecting properly
- ✅ ≥80% of Web pages displaying data correctly
- ✅ System functional for core use cases

### Incremental Delivery (Add P2 Features)

8. **Phase 4**: Complete US3 (Python headers) - ~4 hours
9. **Phase 5**: Complete US4 (File/test management) - ~2 hours
10. **VALIDATE**: Run validation scripts, verify SC-003, SC-004, SC-006
11. **Total with P2**: ~30.5 hours

**P2 Deliverables:**
- ✅ All P1 deliverables PLUS
- ✅ Python code fully documented
- ✅ Test files standardized
- ✅ File organization clean

### Full Delivery (Add P3 Features)

12. **Phase 6**: Complete US5 (.gitignore) - ~1 hour
13. **Phase 8**: Complete Polish - ~4 hours
14. **FINAL VALIDATE**: All success criteria SC-001 through SC-012
15. **Total Complete**: ~35.5 hours

**Full Deliverables:**
- ✅ All P1 + P2 deliverables PLUS
- ✅ Git repository clean and secure
- ✅ Comprehensive documentation updated
- ✅ All validation scripts passing

### Parallel Team Strategy

With 2-3 developers after Phase 0 + Phase 1 complete:

- **Developer A (Backend specialist)**: Phase 2 (US1) + Phase 7 (DB/API fixes)
- **Developer B (Documentation lead)**: Phase 3 (US2) + Phase 4 (US3 headers)
- **Developer C (DevOps/Testing)**: Phase 5 (US4) + Phase 6 (US5)

All can work in parallel, then converge for Phase 8 (Polish).

---

## Time Estimates

| Phase | Tasks | Estimated Time | Priority |
|-------|-------|----------------|----------|
| Phase 0: Research | T001-T008 | 11.5 hours | Mixed (R1/R5/R6/R8=P1, others P2-P3) |
| Phase 1: Design | T009-T014 | 4 hours | All P1 |
| Phase 2: US1 (Business Scope) | T015-T021 | 4.5 hours | P1 |
| Phase 3: US2 (Doc Metadata) | T022-T028 | 2 hours | P1 |
| Phase 4: US3 (Python Headers) | T029-T046 | 4 hours | P2 |
| Phase 5: US4 (File Management) | T047-T054 | 2 hours | P2 |
| Phase 6: US5 (.gitignore) | T055-T060 | 1 hour | P3 |
| Phase 7: DB/API Validation | T061-T077 | 6.5 hours | P1 |
| Phase 8: Polish | T078-T086 | 4 hours | Final |
| **TOTAL** | **86 tasks** | **39.5 hours** | |
| **P1 Only (MVP)** | **58 tasks** | **24.5 hours** | Critical path |
| **P1+P2** | **74 tasks** | **30.5 hours** | Recommended |

**Timeline Estimate**:
- MVP (P1): 3-4 working days (24.5 hours)
- Recommended (P1+P2): 4-5 working days (30.5 hours)
- Complete (P1+P2+P3): 5-6 working days (39.5 hours)

---

## Notes

- **[P] markers**: Tasks affecting different files with no dependencies - can run in parallel
- **[Story] labels**: Map tasks to user stories (US1-US5) for traceability
- **File paths**: All tasks include specific file paths for clarity
- **Validation**: Each phase has validation tasks to verify success criteria
- **Independent testing**: Each user story can be tested independently per spec.md
- **Commit strategy**: Commit after each task group or phase checkpoint
- **Rollback safety**: Git history allows rollback, temp/ directory for risky changes
- **Language standard**: Technical terms in English, descriptions in Chinese (per clarification)
- **Test-first**: Test file renames verified immediately with pytest

**Success Criteria Mapping:**
- US1 (Phase 2): SC-001 (业务范围清理)
- US2 (Phase 3): SC-002 (文档元数据), SC-007 (新成员上手)
- US3 (Phase 4): SC-003 (Python注释), SC-008 (代码审查效率)
- US4 (Phase 5): SC-004 (测试文件规范), SC-006 (根目录清理)
- US5 (Phase 6): SC-005 (git status清洁)
- DB/API (Phase 7): SC-009-NEW, SC-010-NEW, SC-011-NEW (数据库和Web页面修复)

**Risk Mitigation:**
- R1 research addresses byapi_adapter uncertainty
- temp/ directory for risky deletions
- Backup before data deletion (R8, T015)
- Immediate test validation after renames (T051)
- Git history for all rollbacks

---

**Next Steps**:
1. Review this task list with JohnC for approval
2. Execute Phase 0 (Research) tasks T001-T008
3. Generate `research.md` with findings
4. Proceed to Phase 1 (Design) based on research outputs
5. Begin implementation following priority order (P1 → P2 → P3)

# Symphony Service Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python Symphony service that loads repo-owned workflow policy, polls Linear,
dispatches isolated Codex runs, and exposes operator-visible runtime status.

**Architecture:** Keep Symphony as a standalone service under `src/services/symphony/` with typed
models, a Linear adapter, a workspace manager, a Codex app-server client, and a single-authority
orchestrator. Use TDD in vertical slices so each core contract is proven before the next layer is
added.

**Tech Stack:** Python 3.12, PyYAML, Jinja2, httpx, FastAPI, Uvicorn, pytest

---

### Task 1: Add failing tests for workflow loading and typed config

**Files:**
- Create: `tests/unit/services/symphony/test_workflow_loader.py`
- Create: `tests/unit/services/symphony/test_config.py`
- Create: `src/services/symphony/__init__.py`
- Create: `src/services/symphony/workflow_loader.py`
- Create: `src/services/symphony/config.py`
- Create: `src/services/symphony/errors.py`
- Create: `src/services/symphony/models.py`

**Step 1: Write the failing tests**
- Assert workflow loading supports front matter and no-front-matter files.
- Assert invalid YAML and non-map front matter raise typed errors.
- Assert config defaults, `$VAR` resolution, and state normalization match spec rules.

**Step 2: Run tests to verify they fail**
- Run: `pytest tests/unit/services/symphony/test_workflow_loader.py tests/unit/services/symphony/test_config.py -v`
- Expected: FAIL because Symphony modules do not exist yet.

**Step 3: Write the minimal implementation**
- Add typed models, loader, and config resolution functions needed by the tests only.

**Step 4: Run tests to verify they pass**
- Run: `pytest tests/unit/services/symphony/test_workflow_loader.py tests/unit/services/symphony/test_config.py -v`
- Expected: PASS

### Task 2: Add failing tests for workspace safety and hook execution

**Files:**
- Create: `tests/unit/services/symphony/test_workspace_manager.py`
- Create: `src/services/symphony/workspace_manager.py`

**Step 1: Write the failing test**
- Assert deterministic sanitized workspace paths.
- Assert root containment is enforced.
- Assert `after_create`, `before_run`, `after_run`, and `before_remove` obey timeout/failure rules.

**Step 2: Run test to verify it fails**
- Run: `pytest tests/unit/services/symphony/test_workspace_manager.py -v`
- Expected: FAIL because the workspace manager is incomplete.

**Step 3: Write minimal implementation**
- Add workspace creation, hook execution, cleanup, and safety checks.

**Step 4: Run test to verify it passes**
- Run: `pytest tests/unit/services/symphony/test_workspace_manager.py -v`
- Expected: PASS

### Task 3: Add failing tests for Linear normalization

**Files:**
- Create: `tests/unit/services/symphony/test_linear_client.py`
- Create: `src/services/symphony/linear_client.py`

**Step 1: Write the failing test**
- Assert candidate issue normalization lowercases labels, derives blockers, coerces priorities, and
  preserves pagination order.

**Step 2: Run test to verify it fails**
- Run: `pytest tests/unit/services/symphony/test_linear_client.py -v`
- Expected: FAIL because the Linear client does not exist yet.

**Step 3: Write minimal implementation**
- Add GraphQL request helpers, pagination, and normalization functions.

**Step 4: Run test to verify it passes**
- Run: `pytest tests/unit/services/symphony/test_linear_client.py -v`
- Expected: PASS

### Task 4: Add failing tests for Codex app-server protocol and agent runner

**Files:**
- Create: `tests/unit/services/symphony/fixtures/fake_codex_app_server.py`
- Create: `tests/unit/services/symphony/test_codex_app_server.py`
- Create: `tests/unit/services/symphony/test_agent_runner.py`
- Create: `src/services/symphony/template_renderer.py`
- Create: `src/services/symphony/codex_app_server.py`
- Create: `src/services/symphony/agent_runner.py`

**Step 1: Write the failing tests**
- Assert the client performs initialize → initialized → thread/start → turn/start in order.
- Assert approvals are auto-approved, unsupported tool calls return structured failures, and
  user-input-required signals fail the run.
- Assert the agent runner loops continuation turns on one thread and runs `after_run` best effort.

**Step 2: Run tests to verify they fail**
- Run: `pytest tests/unit/services/symphony/test_codex_app_server.py tests/unit/services/symphony/test_agent_runner.py -v`
- Expected: FAIL because the protocol client and runner are incomplete.

**Step 3: Write minimal implementation**
- Add the stdio JSON-line client, strict prompt rendering, and multi-turn worker logic.

**Step 4: Run tests to verify they pass**
- Run: `pytest tests/unit/services/symphony/test_codex_app_server.py tests/unit/services/symphony/test_agent_runner.py -v`
- Expected: PASS

### Task 5: Add failing tests for orchestrator scheduling and retries

**Files:**
- Create: `tests/unit/services/symphony/test_orchestrator.py`
- Create: `src/services/symphony/orchestrator.py`
- Create: `src/services/symphony/service.py`

**Step 1: Write the failing test**
- Assert candidate filtering, blocker handling, retry backoff, continuation retry, and terminal
  reconciliation behavior.

**Step 2: Run test to verify it fails**
- Run: `pytest tests/unit/services/symphony/test_orchestrator.py -v`
- Expected: FAIL because orchestrator state logic is incomplete.

**Step 3: Write minimal implementation**
- Add runtime state, worker lifecycle callbacks, retry scheduling, reconciliation, and workflow
  reload checks.

**Step 4: Run test to verify it passes**
- Run: `pytest tests/unit/services/symphony/test_orchestrator.py -v`
- Expected: PASS

### Task 6: Add failing tests for optional status API and CLI entrypoint

**Files:**
- Create: `tests/unit/services/symphony/test_status_api.py`
- Create: `tests/unit/services/symphony/test_run_symphony_cli.py`
- Create: `src/services/symphony/status_api.py`
- Create: `scripts/runtime/run_symphony.py`
- Create: `WORKFLOW.md`

**Step 1: Write the failing test**
- Assert `/api/v1/state`, `/api/v1/<issue_identifier>`, and `/api/v1/refresh` follow the expected
  JSON behavior.
- Assert CLI uses `./WORKFLOW.md` by default and accepts an explicit workflow path.

**Step 2: Run tests to verify they fail**
- Run: `pytest tests/unit/services/symphony/test_status_api.py tests/unit/services/symphony/test_run_symphony_cli.py -v`
- Expected: FAIL because the API and CLI are incomplete.

**Step 3: Write minimal implementation**
- Add the FastAPI status surface, dashboard HTML, CLI parsing, and a root workflow example.

**Step 4: Run tests to verify they pass**
- Run: `pytest tests/unit/services/symphony/test_status_api.py tests/unit/services/symphony/test_run_symphony_cli.py -v`
- Expected: PASS

### Task 7: Final verification

**Files:**
- Modify: `openspec/changes/add-symphony-service/tasks.md`

**Step 1: Validate OpenSpec**
- Run: `openspec validate add-symphony-service --strict`
- Expected: PASS

**Step 2: Run focused Symphony test suite**
- Run: `pytest tests/unit/services/symphony -v`
- Expected: PASS

**Step 3: Update checklist**
- Mark `openspec/changes/add-symphony-service/tasks.md` items complete only after verification passes.

# Implementation Plan - Track: Refactor Core Modules to Enforce Size Limits

This plan outlines the steps to enforce the 1000-line limit across the codebase, prioritizing high-risk backend and frontend core modules. Adheres to Strict TDD and the Core Coding Principles.

## Phase 1: Discovery & Preparation [checkpoint: b21c642]

### Goal: Identify target files and establish baselines.

- [x] Task: Generate a definitive list of "User Source Code" files > 1000 lines. [03bef72]
    - [x] Sub-task: Run script to find `.py` and `.vue` files > 1000 lines, excluding `node_modules`, `dist`, `generated`, `tests`, `docs`.
    - [x] Sub-task: Prioritize the list based on business criticality (e.g., Risk > Data > UI).
- [x] Task: Establish dependency maps for top priority files. [03bef72]
    - [x] Sub-task: Analyze imports and dependencies for `web/backend/app/api/risk_management.py`.
    - [x] Sub-task: Analyze imports and dependencies for `web/backend/app/services/data_adapter.py`.
- [x] Task: Conductor - User Manual Verification 'Discovery & Preparation' (Protocol in workflow.md)

## Phase 2: Refactor `risk_management.py` (Backend Priority 1) [checkpoint: phase-2-complete]

### Goal: Split `risk_management.py` (2112 lines) into modular units ≤ 1000 lines.

- [x] Task: Enhance Regression Test Suite for `risk_management.py`. [4108ef5]
    - [x] Write Tests: Create/Update `tests/backend/test_risk_management_regression.py` covering all public API endpoints and core calculation logic. ensure 90%+ coverage.
    - [x] Implement: Run tests to confirm current baseline (Green state).
- [x] Task: Refactor `risk_management.py` - Core Split. [bb3eaea]
    - [x] Write Tests: Verify `risk_management_core.py` (new) interfaces.
    - [x] Implement: Extract core calculation logic to `web/backend/app/api/risk_management_core.py`.
    - [x] Implement: Update original file to import from new core module.
    - [x] Verify: Run regression suite (Must be 100% Pass).
- [x] Task: Refactor `risk_management.py` - Utils & Helpers. [01a1be9]
    - [x] Write Tests: Verify extracted utility functions.
    - [x] Implement: Move helper functions to `web/backend/app/utils/risk_utils.py`.
    - [x] Verify: Run regression suite.
- [x] Task: Refactor `risk_management.py` - Route Split (V3.1). [d9cd699]
    - [x] Implement: Extract V3.1 routes to `web/backend/app/api/risk_management_v31.py`.
    - [x] Implement: Update `risk_management.py` to include new router.
    - [x] Verify: Run regression suite.
- [x] Task: Final Polish & Verification.
    - [x] Implement: Add header comments to all split files defining responsibility.
    - [x] Verify: Check line counts of all involved files.
- [x] Task: Conductor - User Manual Verification 'Refactor risk_management.py' (Protocol in workflow.md)

## Phase 3: Refactor `data_adapter.py` (Backend Priority 2) [checkpoint: phase-3-complete]

### Goal: Split `data_adapter.py` (2016 lines).

- [x] Task: Enhance Regression Test Suite for `data_adapter.py`. [57d550c]
    - [x] Write Tests: Create `tests/backend/test_data_adapter_regression.py` covering data fetching and transformation.
    - [x] Implement: Confirm baseline pass.
- [x] Task: Refactor `data_adapter.py` - Logic Separation. [57d550c]
    - [x] Write Tests: Unit tests for new split modules.
    - [x] Implement: Split into `data_adapter_service.py` (logic) and `data_adapter_api.py` (interface) or similar structure based on analysis.
    - [x] Verify: Regression suite pass.
- [x] Task: Conductor - User Manual Verification 'Refactor data_adapter.py' (Protocol in workflow.md)

## Phase 4: Frontend Refactoring (Vue Core) [checkpoint: phase-4-complete]

### Goal: Address largest Vue components.

- [x] Task: Identify and Refactor Top Priority Vue Component. [ae8a03a]
    - [x] Sub-task: Select largest `.vue` file (e.g., `OrderPage.vue` or similar from Phase 1 list).
    - [x] Write Tests: Ensure component has Cypress/Vitest coverage.
    - [x] Implement: Extract static logic to `@/utils`.
    - [x] Implement: Extract stateful logic to `composables/useX.ts`.
    - [x] Implement: Split sub-components (e.g., `Component/Child.vue`).
    - [x] Verify: Tests pass.
- [x] Task: Conductor - User Manual Verification 'Frontend Refactoring' (Protocol in workflow.md)

## Phase 5: Final Review & Cleanup

### Goal: Ensure system-wide adherence.

- [x] Task: Global Line Count Check.
    - [x] Implement: Run line count script again to verify no target files > 1000 lines remain (or phased plan is documented).
- [ ] Task: Conductor - User Manual Verification 'Final Review & Cleanup' (Protocol in workflow.md)
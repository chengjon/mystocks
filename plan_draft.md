# Implementation Plan - Track: Refactor Core Modules to Enforce Size Limits

This plan outlines the steps to enforce the 1000-line limit across the codebase, prioritizing high-risk backend and frontend core modules. Adheres to Strict TDD and the Core Coding Principles.

## Phase 1: Discovery & Preparation

### Goal: Identify target files and establish baselines.

- [ ] Task: Generate a definitive list of "User Source Code" files > 1000 lines.
    - [ ] Sub-task: Run script to find `.py` and `.vue` files > 1000 lines, excluding `node_modules`, `dist`, `generated`, `tests`, `docs`.
    - [ ] Sub-task: Prioritize the list based on business criticality (e.g., Risk > Data > UI).
- [ ] Task: Establish dependency maps for top priority files.
    - [ ] Sub-task: Analyze imports and dependencies for `web/backend/app/api/risk_management.py`.
    - [ ] Sub-task: Analyze imports and dependencies for `web/backend/app/services/data_adapter.py`.
- [ ] Task: Conductor - User Manual Verification 'Discovery & Preparation' (Protocol in workflow.md)

## Phase 2: Refactor `risk_management.py` (Backend Priority 1)

### Goal: Split `risk_management.py` (2112 lines) into modular units ≤ 1000 lines.

- [ ] Task: Enhance Regression Test Suite for `risk_management.py`.
    - [ ] Write Tests: Create/Update `tests/backend/test_risk_management_regression.py` covering all public API endpoints and core calculation logic. ensure 90%+ coverage.
    - [ ] Implement: Run tests to confirm current baseline (Green state).
- [ ] Task: Refactor `risk_management.py` - Core Split.
    - [ ] Write Tests: Verify `risk_management_core.py` (new) interfaces.
    - [ ] Implement: Extract core calculation logic to `web/backend/app/api/risk_management_core.py`.
    - [ ] Implement: Update original file to import from new core module.
    - [ ] Verify: Run regression suite (Must be 100% Pass).
- [ ] Task: Refactor `risk_management.py` - Utils & Helpers.
    - [ ] Write Tests: Verify extracted utility functions.
    - [ ] Implement: Move helper functions to `web/backend/app/utils/risk_utils.py`.
    - [ ] Verify: Run regression suite.
- [ ] Task: Final Polish & Verification.
    - [ ] Implement: Add header comments to all split files defining responsibility.
    - [ ] Verify: Check line counts of all involved files.
- [ ] Task: Conductor - User Manual Verification 'Refactor risk_management.py' (Protocol in workflow.md)

## Phase 3: Refactor `data_adapter.py` (Backend Priority 2)

### Goal: Split `data_adapter.py` (2016 lines).

- [ ] Task: Enhance Regression Test Suite for `data_adapter.py`.
    - [ ] Write Tests: Create `tests/backend/test_data_adapter_regression.py` covering data fetching and transformation.
    - [ ] Implement: Confirm baseline pass.
- [ ] Task: Refactor `data_adapter.py` - Logic Separation.
    - [ ] Write Tests: Unit tests for new split modules.
    - [ ] Implement: Split into `data_adapter_service.py` (logic) and `data_adapter_api.py` (interface) or similar structure based on analysis.
    - [ ] Verify: Regression suite pass.
- [ ] Task: Conductor - User Manual Verification 'Refactor data_adapter.py' (Protocol in workflow.md)

## Phase 4: Frontend Refactoring (Vue Core)

### Goal: Address largest Vue components.

- [ ] Task: Identify and Refactor Top Priority Vue Component.
    - [ ] Sub-task: Select largest `.vue` file (e.g., `OrderPage.vue` or similar from Phase 1 list).
    - [ ] Write Tests: Ensure component has Cypress/Vitest coverage.
    - [ ] Implement: Extract static logic to `@/utils`.
    - [ ] Implement: Extract stateful logic to `composables/useX.ts`.
    - [ ] Implement: Split sub-components (e.g., `Component/Child.vue`).
    - [ ] Verify: Tests pass.
- [ ] Task: Conductor - User Manual Verification 'Frontend Refactoring' (Protocol in workflow.md)

## Phase 5: Final Review & Cleanup

### Goal: Ensure system-wide adherence.

- [ ] Task: Global Line Count Check.
    - [ ] Implement: Run line count script again to verify no target files > 1000 lines remain (or phased plan is documented).
- [ ] Task: Conductor - User Manual Verification 'Final Review & Cleanup' (Protocol in workflow.md)

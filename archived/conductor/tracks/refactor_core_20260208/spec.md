# Specification: Refactor Core Modules to Enforce Size Limits

## 1. Overview
This track focuses on strictly enforcing the `CORE_CODING_PRINCIPLES.md` across the codebase, specifically targeting Python (`.py`) and Vue (`.vue`) files that exceed the 1000-line limit. The primary goal is to improve maintainability, readability, and adherence to the Single Responsibility Principle by splitting large files into smaller, modular units without altering their external behavior. Documentation (`.md`, `.txt`) and generated files are out of scope.

## 2. Functional Requirements
*   **Target Files & Priority:**
    *   **Priority 1:** High-risk / Core Business Files (e.g., `risk_management.py`, Payment/Order Vue components).
    *   **Priority 2:** Non-core but over-sized files.
    *   **Constraint:** Prior to splitting, map dependencies to avoid circular imports.
*   **Refactoring Actions:**
    *   **Logic Extraction:** Move helper functions and generic logic to dedicated utility modules (`utils.py` or `@/utils/`).
    *   **Component/Class Splitting:** Decompose large classes (Python) and components (Vue) into smaller, focused sub-units.
    *   **Layered Separation:** Ensure clear separation of concerns (e.g., Service vs. Controller vs. Data Access).
    *   **Composables (Vue):** Extract stateful logic into Vue composables (`useX`).
        *   *Constraint:* Each composable must follow Single Responsibility (e.g., `useOrderList` handles only list logic) and adhere to the 1000-line limit.
*   **Naming Convention:**
    *   **Python:** `original_name.py` -> `original_name_core.py`, `original_name_calculations.py`, etc.
    *   **Vue:** `OriginalPage.vue` -> `OriginalPage/Table.vue`, `OriginalPage/Filter.vue`.

## 3. Non-Functional Requirements
*   **Code Style:** All new/refactored code must strictly follow `CORE_CODING_PRINCIPLES.md`.
*   **Performance:** Refactoring should not negatively impact application performance.
*   **Test Coverage & Reliability (Strict TDD):**
    *   **Pre-Refactor:** Write/Enrich regression tests covering all external API inputs/outputs and core business logic.
    *   **Coverage Target:** Maintain ≥ pre-refactor coverage. For core files (e.g., `risk_management.py`), target **90%+ coverage**.
    *   **Pass Rate:** Must be 100% before and after refactoring.
*   **Traceability:** Split files must include a header comment: "Split from [Original Filename] for [Reason/Responsibility]".

## 4. Acceptance Criteria
*   [ ] **Line Count limit:**
    *   All target files reduced to < 1000 lines.
    *   If immediate reduction to < 1000 is architecturally blocked, a phased plan (e.g., first to 1500) is acceptable, but *newly created* split files MUST be ≤ 1000 lines.
*   [ ] **Single Responsibility Verification:**
    *   Each file/component has a header comment explicitly stating its core responsibility (e.g., "Handles only risk rule calculation, no persistence").
*   [ ] **Behavioral Preservation:**
    *   Regression tests (Unit/Integration) pass 100%. Manual verification alone is **prohibited**.
*   [ ] No new linting errors.

## 5. Out of Scope
*   Refactoring of `.md`, `.txt`, or other documentation files.
*   Refactoring of auto-generated files (e.g., `*.d.ts`, `sass.dart.js`).
*   Adding new features.

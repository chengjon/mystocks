# Core Coding Principles for File Size Control (< 1000 Lines)

This document outlines the core coding principles to strictly control file sizes (specifically keeping them under 1000 lines) while ensuring code readability, maintainability, and adherence to best practices for both Python and Vue.

## 1. General Principles (Applicable to Python & Vue)

These are foundational rules to strictly observe regardless of the file type.

### 1.1 Single Responsibility Principle (Core)
*   **Concept**: Each file/module must be responsible for **only one core function**. Avoid "monolithic" files.
*   **Examples**:
    *   **Python**: A file should not simultaneously handle data processing, API requests, permission checks, and logging.
    *   **Vue**: A file should not handle form submission, chart rendering, and permission control all at once.
*   **Goal**: Limit code volume at the root level by narrowing the scope of responsibility.

### 1.2 Modularization (Key to Size Control)
*   **Concept**: Break down large features into independent modules/components and use **imports** instead of writing everything in one file.
*   **Actions**:
    *   Extract repetitive logic into common utilities (Python: `utils.py`, Vue: `@/utils/`).
    *   Split functional modules into independent files (e.g., Python: `data_process.py`/`api.py`; Vue: `components/Table.vue`/`components/Form.vue`).

### 1.3 Concise Logic Units
*   **Concept**: Each function/method/component should do **one small thing**. Strict limits on individual logical units.
*   **Limits**:
    *   **Python**: Single function/method ≤ **50 lines**, single class ≤ **200 lines**.
    *   **Vue**: Single method/function ≤ **30 lines**, single sub-component ≤ **200 lines**.
*   **Enforcement**: Immediately split into sub-functions or sub-components if limits are exceeded.

### 1.4 Eliminate Redundancy
*   **Cleanup**: Remove unused variables, imports, commented-out code, and debug statements (`print`, `console.log`).
*   **Comments**: Explain "**Why**", not "What". Keep comment lines within **10%** of code lines.
*   **Formatting**: Avoid excessive blank lines (max 1 continuous blank line; logical sections separated by only 1 line).

---

## 2. Python-Specific Principles

### 2.1 Module Splitting Strategy
*   **Functional Split**: `data_utils.py` (Data), `api_client.py` (API), `config.py` (Config), `constants.py` (Constants).
*   **Layered Architecture**: MVC/MVT patterns - Separate `models/`, `views/`, and `controllers/`.
*   **Class Splitting**: If a class exceeds **200 lines**, split it by function (e.g., `User` -> `UserBasic` + `UserAuth`).

### 2.2 Logic Simplification
*   **Extract Complex Conditions**: Move complex `if-elif-else` logic into independent functions (e.g., `check_user_permission()` instead of inline checks).
*   **Reduce Nesting**: If nesting exceeds **3 layers** (for/if), split into multiple functions. Deep nesting increases line count and reduces readability.
*   **Leverage Libraries**: Use standard/third-party libraries (e.g., `requests`, `pandas`) instead of writing verbose manual implementations.

---

## 3. Vue-Specific Principles

Vue Single File Components (SFC) consist of `<script>`, `<template>`, and `<style>`, and each part must be controlled.

### 3.1 Component Splitting Strategy
*   **Page-Level**: One `.vue` file per page. Split page modules into sub-components (e.g., `OrderPage.vue` -> `OrderTable.vue` + `OrderFilter.vue` + `OrderDetail.vue`).
*   **Common Components**: Extract generic UI elements (buttons, inputs, modals) to `components/common/` and register globally.
*   **Logic Extraction (Vue 3)**: Use **composables** (`composables/`) to extract reusable stateful logic (e.g., `useUser()`, `useTable()`), reducing code in `<script>`.

### 3.2 Section-Specific Control
*   **`<script>`**:
    *   **Method Splitting**: Move complex logic to `@/utils/` (e.g., form validation -> `utils/validate.js`).
    *   **Setup**: Avoid massive `setup()` functions; use composables.
    *   **State**: Use Pinia/Vuex for global state; minimize local `data`/`ref` logic.
*   **`<template>`**:
    *   **Reduce Nesting**: If `div`/`el-form` nesting exceeds **3 layers**, extract to a sub-component.
    *   **Reuse**: Use `<component>` or slots to replace repetitive template code.
*   **`<style>`**:
    *   **Global Styles**: Move color variables and common layouts to `@/styles/`.
    *   **Mixins**: Use SCSS/LESS mixins and variables to reduce repetitive styling.

---

## Summary
1.  **Core Logic**: **Single Responsibility + Modular Splitting**. Split large files into smaller ones to control size at the source.
2.  **Granularity**: Strict line limits for functions/classes (Python) and methods/components (Vue).
3.  **Cleanliness**: Eliminate redundancy, keep comments concise, and reuse common logic.

**Goal**: Keep files under **1000 lines** while improving engineering standards, readability, and AI-assistability.

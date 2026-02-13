# Specification: Comprehensive ArtDeco V3.0 Web Redesign & Optimization

## 1. Overview
This track focuses on a comprehensive redesign and optimization of the MyStocks web frontend. The primary goal is to strictly implement the **ArtDeco V3.0 Design System** (aligned with `ARTDECO_MASTER_INDEX.md` and `ArtDeco_System_Architecture_Summary.md`), ensuring all pages function correctly with backend APIs, logic verification is error-free, and pages display normally as expected.

The implementation will follow a **Side-by-Side Migration** strategy to ensure stability. New pages will be built in `views/artdeco-pages/` following the "Container-Tabs" architecture and strict Base/Domain component separation.

## 2. Goals
*   **Visual Consistency:** Achieve 100% adherence to ArtDeco V3.0 standards (Cinzel font, 11-level spacing, A-share colors).
*   **Architectural Integrity:** Strictly enforce the "Container-Tabs" architecture and Base/Domain component separation.
*   **Functional Reliability:** Ensure 100% alignment with backend APIs using a centralized, strongly-typed service layer.
*   **Zero Regression:** Verify logic and display through a multi-layered validation process (Linter, Visual Regression, Manual Review).

## 3. Functional Requirements

### 3.1 Architecture & Directory Structure
*   **New Directory:** Create `web/frontend/src/views/artdeco-pages/` for all new pages.
*   **Sub-directory Structure:** Organize by domain (e.g., `trade/`, `market/`, `risk/`).
    *   **Containers:** `views/artdeco-pages/[domain]/index.vue` (Parent Container).
        *   **Container Responsibilities:** The parent container is responsible for global state management of the domain page, tab switching logic, and unified API request/response handling for the page, while delegating UI rendering and business logic of individual functional blocks to `[Domain]-tabs` components.
    *   **Tabs:** `views/artdeco-pages/[domain]/[Domain]-tabs/` (Page-specific logic blocks, strictly following the "Domain-tabs" rule in `ARTDECO_COMPONENT_GUIDE.md`).
*   **Component Separation:**
    *   **Base UI:** Use existing `src/components/artdeco/base/` components.
    *   **Domain Components:** Refactor/Create business components in `src/components/artdeco/[domain]/`.

### 3.2 API Integration
*   **Service Layer:** Create domain-specific, centralized API services in `web/frontend/src/api/artdeco-api/[domain].ts` (all API calls in `artdeco-pages` MUST go through these services; direct use of `axios`/`fetch` in components is strictly prohibited).
*   **Type Safety:** Strict use of `UnifiedResponse<T>` and generated frontend types.
*   **Error Handling:** Implement a global Axios interceptor in `web/frontend/src/api/artdeco-api/interceptor.ts` that captures all API errors (network errors, business errors, authentication errors, etc.) and triggers standard `ArtDecoAlert` or toast notifications in compliance with ArtDeco UI specifications.

### 3.3 Design Implementation
*   **Tokens:** All styles MUST use SCSS variables from `artdeco-tokens.scss`.
    *   Colors: `var(--artdeco-gold-primary)`, `var(--artdeco-rise)`, `var(--artdeco-down)`.
    *   Spacing: `var(--artdeco-spacing-1)` to `var(--artdeco-spacing-32)`.
    *   Typography: `var(--font-display)` (Cinzel), `var(--font-mono)` (JetBrains Mono).
*   **Layout:** Use the official `ArtDecoGrid` component from `src/components/artdeco/base/` or flexbox layouts, with all spacing values strictly using token-based spacing (`var(--artdeco-spacing-*)`), no hardcoded `px` values.

## 4. Non-Functional Requirements
*   **Performance:** New pages must load within standard performance budgets.
*   **Responsiveness:** Pages must adapt to standard breakpoints defined in `artdeco-tokens.scss`.
*   **Browser Compatibility:** Support Chrome, Firefox, Safari (latest versions).

## 5. Acceptance Criteria

### 5.1 Automated Validation
*   [ ] **Linter Pass:** Custom Stylelint rule (configured in `.stylelintrc.js`) scans all `.vue`/`.scss` files under `artdeco-pages` during CI/CD pipeline, and finds **zero** hardcoded colors (hex/rgb) or pixel values (px); all styles must use ArtDeco design tokens. The linter check is a mandatory gate for code merge.
*   [ ] **Type Check:** `vue-tsc` passes with **zero** errors for all new files.
*   [ ] **Visual Regression:** Key pages pass visual regression tests (referencing baselines).

### 5.2 Manual Verification
*   [ ] **Design Review:** All pages are verified against the checklist derived from `ARTDECO_COMPONENTS_CATALOG.md`, `artdeco-tokens.scss`, and `ARTDECO_V3_COMPLETE_SUMMARY.md` (the final acceptance benchmark for ArtDeco V3.0), confirming 100% visual fidelity to the ArtDeco design system.
*   [ ] **Functional Test:** All API interactions (success/error paths) verified against `docs/api/API_CONTRACT_ARCHITECTURE_ANALYSIS.md`.

## 6. Out of Scope
*   Refactoring of legacy pages in `views/old/` (these will be deprecated later).
*   Backend API modifications (strictly frontend adaptation).

## 7. Implementation Phases
To ensure incremental delivery and risk control (aligned with Side-by-Side Migration strategy):

### 7.1 Phase 1: Foundation Setup (1 week)
- Create core directory structure (`artdeco-pages`, `artdeco-api`, verify `artdeco/base` components).
- Implement Stylelint rules for design token checking and global API interceptor.
- Establish visual regression test baselines for key Base components (`ArtDecoAlert`, `ArtDecoGrid`, etc.).

### 7.2 Phase 2: Low-Risk Page Migration (2 weeks)
- Migrate low-complexity pages (e.g., `market/overview`, `user/settings`) to `artdeco-pages`.
- Complete automated + manual verification for migrated pages.

### 7.3 Phase 3: Core Page Migration (3 weeks)
- Migrate high-complexity core pages (e.g., `trade/order`, `risk/analysis`) to `artdeco-pages`.
- Focus on API alignment and logic verification for core business flows.

### 7.4 Phase 4: Full Verification & Deprecation Preparation (1 week)
- Conduct full-set automated (linter/type/visual) and manual verification.
- Prepare deprecation plan for legacy pages (no immediate removal, only after 2 weeks of stable running of new pages).

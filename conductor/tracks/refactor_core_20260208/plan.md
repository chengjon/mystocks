# Implementation Plan - Track: Refactor Core Modules to Enforce Size Limits

This plan outlines the steps to enforce the 1000-line limit across the codebase, prioritizing high-risk backend and frontend core modules. Adheres to Strict TDD and the Core Coding Principles.

## Phase 1: Discovery & Preparation [checkpoint: b21c642]

### Goal: Identify target files and establish baselines.

- [x] Task: Generate a definitive list of "User Source Code" files > 1000 lines. [03bef72]
- [x] Task: Establish dependency maps for top priority files. [03bef72]
- [x] Task: Conductor - User Manual Verification 'Discovery & Preparation' (Protocol in workflow.md)

## Phase 2: Refactor `risk_management.py` (Backend Priority 1) [checkpoint: phase-2-complete]

### Goal: Split `risk_management.py` (2112 lines) into modular units ≤ 1000 lines.

- [x] Task: Enhance Regression Test Suite for `risk_management.py`. [4108ef5]
- [x] Task: Refactor `risk_management.py` - Core Split. [bb3eaea]
- [x] Task: Refactor `risk_management.py` - Utils & Helpers. [01a1be9]
- [x] Task: Refactor `risk_management.py` - Route Split (V3.1). [d9cd699]
- [x] Task: Final Polish & Verification.
- [x] Task: Conductor - User Manual Verification 'Refactor risk_management.py' (Protocol in workflow.md)

## Phase 3: Refactor `data_adapter.py` (Backend Priority 2) [checkpoint: phase-3-complete]

### Goal: Split `data_adapter.py` (2016 lines).

- [x] Task: Enhance Regression Test Suite for `data_adapter.py`. [57d550c]
- [x] Task: Refactor `data_adapter.py` - Logic Separation. [57d550c]
- [x] Task: Conductor - User Manual Verification 'Refactor data_adapter.py' (Protocol in workflow.md)

## Phase 4: Frontend Refactoring (Vue Core) [checkpoint: phase-4-complete]

### Goal: Address largest Vue components.

- [x] Task: Identify and Refactor Top Priority Vue Component. [ae8a03a]
- [x] Task: Conductor - User Manual Verification 'Frontend Refactoring' (Protocol in workflow.md)

## Phase 5: Final Review & Cleanup [checkpoint: phase-5-complete]

### Goal: Ensure system-wide adherence.

- [x] Task: Global Line Count Check.
- [x] Task: Conductor - User Manual Verification 'Final Review & Cleanup' (Protocol in workflow.md)

## Phase 6: Extended Refactoring (Follow-up Tasks) [checkpoint: phase-6-complete]

### Goal: Refactor remaining large files and improve test integration.

- [x] Task: Refactor `ArtDecoDataAnalysis.vue` (Frontend ~2400 lines). [9146e50]
- [x] Task: Refactor `risk_management_v31.py` (Backend ~1100 lines). [4c15021]
- [x] Task: CI/CD Integration. [4c15021]

## Phase 7: Data API Refactoring [checkpoint: phase-7-complete]

### Goal: Split `data.py` (1785 lines).

- [x] Task: Enhance Regression Test Suite for `data.py`. [4498207]
- [x] Task: Modularize `data.py` into domain-specific routers. [4498207]
    - [x] Sub-task: Stocks Basic, Market, KLine, Margin, LHB, Futures.
- [x] Task: Verify with regression tests. [4498207]
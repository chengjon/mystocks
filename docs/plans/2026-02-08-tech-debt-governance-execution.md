# Tech Debt Governance Execution Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create OpenSpec change artifacts and execution-ready governance documents for technical debt management.

**Architecture:** OpenSpec change `tech-debt-governance-2026q1` defines governance requirements; `technical_debt/` holds execution docs and registers; root `TASK*.md` files track work.

**Tech Stack:** OpenSpec CLI, Markdown.

### Task 1: Scaffold OpenSpec change

**Files:**
- Create: `openspec/changes/tech-debt-governance-2026q1/proposal.md`
- Create: `openspec/changes/tech-debt-governance-2026q1/tasks.md`
- Create: `openspec/changes/tech-debt-governance-2026q1/design.md`
- Create: `openspec/changes/tech-debt-governance-2026q1/impact.md`
- Create: `openspec/changes/tech-debt-governance-2026q1/specs/architecture-governance/spec.md`

**Step 1: Create minimal proposal skeleton (acts as baseline check)**
- Write `proposal.md` with Why/What/Impact.

**Step 2: Add tasks checklist**
- Write `tasks.md` with T01-T10 and checkboxes.

**Step 3: Document decisions and impact**
- Write `design.md` and `impact.md` with concise scope.

**Step 4: Add spec deltas**
- Write `specs/architecture-governance/spec.md` with ADDED requirements and scenarios.

**Step 5: Verify structural correctness**
- Run: `openspec validate tech-debt-governance-2026q1 --strict`
- Expected: validation passes (no errors).

### Task 2: Create governance core documents

**Files:**
- Create: `technical_debt/governance/TECH_DEBT_AUDIT_2026Q1.md`
- Create: `technical_debt/governance/ARCHITECTURE_SOURCE_OF_TRUTH.md`
- Create: `technical_debt/governance/SPEC_CONFLICT_MATRIX.md`
- Create: `technical_debt/governance/DEBT_REGISTER.md`

**Step 1: Draft audit overview**
- Define scope, cadence, and owners.

**Step 2: Draft SoT**
- List authoritative sources by domain.

**Step 3: Seed conflict matrix**
- Add SC-001..SC-020 entries with status fields.

**Step 4: Seed debt register**
- Add TD-001..TD-015 entries with owner/DDL placeholders.

**Step 5: Verify internal consistency**
- Ensure IDs referenced match T01-T10 and conflict/debt IDs.

### Task 3: Create execution tracking artifacts

**Files:**
- Create: `TASK.md`
- Create: `TASK-REPORT.md`
- Create: `TASK-T01-REPORT.md`
- Create: `TASK-T02-REPORT.md`
- Create: `TASK-T03-REPORT.md`
- Create: `TASK-T04-REPORT.md`
- Create: `TASK-T05-REPORT.md`
- Create: `TASK-T06-REPORT.md`
- Create: `TASK-T07-REPORT.md`
- Create: `TASK-T08-REPORT.md`
- Create: `TASK-T09-REPORT.md`
- Create: `TASK-T10-REPORT.md`

**Step 1: Create master board**
- Add T01-T10 with owners/DDL placeholders, dependencies, acceptance criteria.

**Step 2: Create weekly rollup**
- Add snapshot table and metrics placeholders.

**Step 3: Create per-task templates**
- Use consistent headings for progress, risks, evidence.

**Step 4: Initialize T01-T04 as in-progress**
- Record first actions (drafts created).

### Task 4: Update indexes and references

**Files:**
- Modify: `technical_debt/INDEX.md`
- Modify: `openspec/changes/tech-debt-governance-2026q1/tasks.md`

**Step 1: Update technical debt index**
- Add governance docs and TASK artifacts.

**Step 2: Cross-link execution artifacts in OpenSpec tasks**
- Add Execution Artifacts section with paths.

### Task 5: Validate OpenSpec change

**Step 1: Run validation**
- Run: `openspec validate tech-debt-governance-2026q1 --strict`
- Expected: no errors.

# Frontend Navigation Consolidation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Consolidate navigation menu/route tasks into the active OpenSpec change `implement-web-frontend-v2-navigation`, encoding the agreed menu and routing decisions without touching product code.

**Architecture:** Documentation-only change set: update OpenSpec `tasks.md` files to centralize navigation work, record locked decisions, and remove duplication from other active changes. Follow OpenSpec checklist, validation, and archiving guidance.

**Tech Stack:** OpenSpec CLI (validation/inspection), Markdown documentation, Git (optional commit only).

---

## Scope & Constraints

- **Scope:** ONLY active changes under `openspec/changes/`.
- **Target consolidation:** All menu/route work lives in `openspec/changes/implement-web-frontend-v2-navigation/tasks.md`.
- **No code changes:** Only OpenSpec task management and documentation alignment.
- **No execution:** Do not run commands in this plan; provide explicit commands only.

## Locked Decisions (must be encoded in tasks.md)

1) **Top-level menus (6):** `market`, `stocks`, `analysis`, `risk`, `strategy+trading`, `system`.
2) **Dashboard:** home route `/` and **not** a left menu item.
3) **Stocks prefix:** canonical route prefix is `/stocks`.
4) **Strategy+trading default path:** `/strategy`.

## OpenSpec Compliance Notes (from openspec/AGENTS.md)

- **Before any task:** read relevant specs, check active changes, and run `openspec list` / `openspec list --specs`.
- **Task checklist discipline:** implement tasks sequentially; **only** mark `- [x]` after the work is complete.
- **Validation:** run `openspec validate <change-id> --strict` after updates.
- **Archiving (post-deploy):** move change to archive or use `openspec archive <change-id> --skip-specs --yes`, then run `openspec validate --strict`.

---

### Task 1: Update navigation consolidation tasks (implement-web-frontend-v2-navigation)

**Files:**
- Modify: `openspec/changes/implement-web-frontend-v2-navigation/tasks.md`

**Step 1: Add/refresh a locked-decision section** (2–5 min)

Insert (or replace) a clearly labeled section near the top of `tasks.md`:

```markdown
## 0. Locked Decisions (Navigation)
- [ ] 0.1 Top-level menus: market, stocks, analysis, risk, strategy+trading, system
- [ ] 0.2 Dashboard is home route `/` and not a left menu item
- [ ] 0.3 Canonical stocks route prefix is `/stocks`
- [ ] 0.4 Strategy+trading default path is `/strategy`
```

**Step 2: Add a consolidated navigation checklist** (2–5 min)

Add a dedicated checklist to centralize all navigation work here:

```markdown
## 1. Navigation Consolidation (Active)
- [ ] 1.1 Consolidate all menu/route tasks from other active changes into this change
- [ ] 1.2 Define/confirm six top-level menus: market, stocks, analysis, risk, strategy+trading, system
- [ ] 1.3 Ensure dashboard `/` remains home only (not a left menu item)
- [ ] 1.4 Enforce canonical stocks route prefix `/stocks` across stock routes
- [ ] 1.5 Set strategy+trading default path to `/strategy`
- [ ] 1.6 Add cross-reference note for migrated tasks in `refactor-web-frontend-menu-architecture`
```

**Step 3: Add a scope note** (2–5 min)

Include a brief “Scope” note reminding that navigation tasks are centralized here and code changes are **out of scope** for this change.

**Step 4: Verify OpenSpec validation** (2–5 min)

Run (do not execute here):

```bash
openspec validate implement-web-frontend-v2-navigation --strict
```

Expected: **PASS** with no validation errors.

---

### Task 2: Mark scope migration in refactor-web-frontend-menu-architecture

**Files:**
- Modify: `openspec/changes/refactor-web-frontend-menu-architecture/tasks.md`

**Step 1: Add a scope migration section** (2–5 min)

Add a top-level section that explicitly moves navigation consolidation work to the active change:

```markdown
## 0. Scope Migration (Navigation Consolidation)
- [ ] 0.1 Navigation consolidation tasks moved to `openspec/changes/implement-web-frontend-v2-navigation/tasks.md`
- [ ] 0.2 Do not implement duplicate menu/route work in this change
```

**Step 2: Remove or replace overlapping tasks** (2–5 min)

If the current checklist includes navigation/menu/route items, replace them with a short note pointing to the consolidated change. Keep it explicit that this change no longer owns those tasks.

**Step 3: Verify OpenSpec validation** (2–5 min)

Run (do not execute here):

```bash
openspec validate refactor-web-frontend-menu-architecture --strict
```

Expected: **PASS** with no validation errors.

---

### Task 3: Cross-check active changes for duplication (documentation-only)

**Files:**
- No edits unless overlap is confirmed

**Step 1: List active changes** (2–5 min)

Run (do not execute here):

```bash
openspec list
```

Expected: `implement-web-frontend-v2-navigation` and `refactor-web-frontend-menu-architecture` appear as active changes.

**Step 2: Optional validation sweep** (2–5 min)

Run (do not execute here):

```bash
openspec validate --strict
```

Expected: **PASS** for all active changes, or error output that highlights which change to fix.

---

## Optional: Commit (ONLY if explicitly requested)

```bash
git add openspec/changes/implement-web-frontend-v2-navigation/tasks.md \
        openspec/changes/refactor-web-frontend-menu-architecture/tasks.md
git commit -m "docs(openspec): consolidate frontend navigation tasks"
```

---

## Risks & Rollback

- **Risk:** Duplicate or conflicting navigation tasks remain in multiple changes.
  - **Mitigation:** Explicit “Scope Migration” section and cross-reference in both tasks files.
- **Risk:** OpenSpec validation fails due to malformed checklist structure.
  - **Mitigation:** Run `openspec validate <change-id> --strict` after each tasks update.
- **Rollback:** Revert the two `tasks.md` files to their previous state (git checkout of the files) if consolidation introduces confusion.

## Acceptance Criteria

- `implement-web-frontend-v2-navigation/tasks.md` contains the locked decisions and a consolidated navigation checklist.
- `refactor-web-frontend-menu-architecture/tasks.md` explicitly marks navigation work as migrated and avoids duplicates.
- Locked decisions are encoded exactly as specified:
  - 6 top-level menus: market, stocks, analysis, risk, strategy+trading, system
  - Dashboard is `/` and not a left menu item
  - Canonical stocks prefix `/stocks`
  - Strategy+trading default path `/strategy`
- OpenSpec strict validation passes for the affected changes.

---

Plan complete and saved to `docs/plans/2026-02-06-frontend-navigation-consolidation.md`.
Two execution options:

1) **Subagent-Driven (this session)** — I dispatch a fresh subagent per task, review between tasks.
2) **Parallel Session (separate)** — Open a new session with `superpowers:executing-plans` and run tasks with checkpoints.

Which approach?

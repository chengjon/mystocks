---
phase: 05
plan: 01
wave: 1
depends_on: []
files_modified:
  - architecture/STANDARDS.md
  - web/frontend/COMPOSABLES-AUDIT.md
  - .planning/REQUIREMENTS.md
  - .planning/PROJECT.md
  - .planning/STATE.md
requirements:
  - COMP-01
  - COMP-02
  - COMP-03
autonomous: true
---

# Phase 5 Plan 01: Composable Convention, Audit Dispositions & Traceability

<objective>
Document the view-local composable convention in STANDARDS.md, record final dispositions in COMPOSABLES-AUDIT.md, and close STRU-04 traceability across the planning layer. Zero file moves — both extraction candidates stay in place.
</objective>

<must_haves>
- architecture/STANDARDS.md contains a composable co-location rule in section 二.1 (前端开发红线)
- web/frontend/COMPOSABLES-AUDIT.md has a "Final Disposition" section with per-file decisions and tradingDashboardActions.ts flagged as audited exception
- .planning/REQUIREMENTS.md has COMP-01/02 checked off as Complete, COMP-03 as N/A (no extraction justified)
- .planning/PROJECT.md has STRU-04 moved from Active to Validated with phase reference
- npm run build succeeds (no files were moved, so build should be unchanged)
</must_haves>

<verification>
1. `grep -c "Composable 协作定位\|composable.*co-location\|view-local" architecture/STANDARDS.md` returns >= 1
2. `grep -c "Final Disposition" web/frontend/COMPOSABLES-AUDIT.md` returns >= 1
3. `grep "COMP-0[123]" .planning/REQUIREMENTS.md` shows all three as `[x]`
4. `grep "STRU-04" .planning/PROJECT.md` shows it under Validated section
5. `cd web/frontend && npm run build` exits 0
</verification>

---

## Task 1: Add composable convention to STANDARDS.md

<read_first>
- architecture/STANDARDS.md (lines 67-83 — section 二 and its frontend/backend subsections)
- .planning/phases/05-composables-disposition/05-CONTEXT.md (D-05, D-06 — exact rule text)
</read_first>

<action>
In `architecture/STANDARDS.md`, insert a new bullet point at the end of section 二.1 (前端开发红线), after the TRACE_ID rule (currently line 73). Use the exact same format as existing rules: `* **Rule name**: Description`.

Insert this text after line 73:

```
*   **Composable 协作定位（View-Local Canonical）**：Composable 按角色分类，再按消费者数量决定去向。（1）不是 composable 的文件（无 reactive state / Vue lifecycle）不得放入 `src/composables/`，按职能路由（transport → `src/api/`，types → `types/`，utils → `utils/`）。（2）真正的 composable 若只有 1 个消费者，使用 `./composables/` 相对导入与消费者视图同目录共存（idiomatic Vue co-location），这是 canonical pattern。（3）提取到 `src/composables/` 需满足 2+ 消费者。禁止基于"可能复用"的预防性提取。
```

This rule is derived from CONTEXT.md D-01 (role-first extraction criteria) and D-06 (the convention rule).
</action>

<acceptance_criteria>
- `architecture/STANDARDS.md` contains the string `Composable 协作定位`
- `architecture/STANDARDS.md` contains the string `View-Local Canonical`
- `architecture/STANDARDS.md` contains the string `src/composables/` within the 二.1 section
- The new bullet follows the same `*   **Name**: Description` format as the 4 existing rules in section 二.1
- No other sections of STANDARDS.md are modified
</acceptance_criteria>

---

## Task 2: Update COMPOSABLES-AUDIT.md with final dispositions

<read_first>
- web/frontend/COMPOSABLES-AUDIT.md (full file — understand current structure)
- .planning/phases/05-composables-disposition/05-CONTEXT.md (D-03, D-04 — per-file dispositions)
</read_first>

<action>
Append a new section at the end of `web/frontend/COMPOSABLES-AUDIT.md` (after the existing "Recommendation" section):

```markdown
## Final Disposition (Phase 5, 2026-04-08)

Per CONTEXT.md decisions D-01 through D-04 (role-first extraction criteria):

### Extraction Candidates

| File | Disposition | Rationale |
|------|-------------|-----------|
| useTradingDashboard.ts | **Keep view-local** | 1 consumer (TradingDashboard.vue), view-specific state management. No extraction case. |
| tradingDashboardActions.ts | **Keep view-local (AUDITED EXCEPTION)** | Not a composable — transport helper (CSRF + HTTP). 1 consumer (useTradingDashboard.ts). Kept for pragmatic reasons (move cost > semantic gain). **Naming debt:** this file is misnamed; presence in composables/ directory is NOT an endorsement of transport helpers in composable directories. If a second consumer appears, relocate to `src/api/` per STANDARDS.md rule. |

### View-Local Confirmation

The remaining 15/17 files remain classified "Keep view-local" as originally audited. Per STANDARDS.md section 二.1 (Composable 协作定位), view-local co-location is the canonical pattern for single-consumer composables.

### Convention Reference

Extraction criteria documented in `architecture/STANDARDS.md` section 二.1 — "Composable 协作定位（View-Local Canonical）".
```

Do NOT modify any existing content in COMPOSABLES-AUDIT.md — only append.
</action>

<acceptance_criteria>
- `web/frontend/COMPOSABLES-AUDIT.md` contains the string `## Final Disposition`
- `web/frontend/COMPOSABLES-AUDIT.md` contains the string `AUDITED EXCEPTION`
- `web/frontend/COMPOSABLES-AUDIT.md` contains the string `Naming debt`
- `web/frontend/COMPOSABLES-AUDIT.md` contains the string `Keep view-local` for useTradingDashboard.ts
- The original inventory table and recommendation section are unchanged
</acceptance_criteria>

---

## Task 3: Update traceability and verify build

<read_first>
- .planning/REQUIREMENTS.md (full file — check current checkbox states and traceability table)
- .planning/PROJECT.md (full file — find STRU-04 in Active section, understand Validated format)
</read_first>

<action>

### Step 1: Update REQUIREMENTS.md

Change the 3 COMP checkboxes from unchecked to checked:
- `- [ ] **COMP-01**` → `- [x] **COMP-01**`
- `- [ ] **COMP-02**` → `- [x] **COMP-02**`
- `- [ ] **COMP-03**` → `- [x] **COMP-03**`

Update the traceability table status for each:
- `| COMP-01 | Phase 5 | Pending |` → `| COMP-01 | Phase 5 | Complete — both candidates kept view-local per evidence |`
- `| COMP-02 | Phase 5 | Pending |` → `| COMP-02 | Phase 5 | Complete — convention added to STANDARDS.md |`
- `| COMP-03 | Phase 5 | Pending |` → `| COMP-03 | Phase 5 | N/A — no extraction justified; both candidates kept view-local per evidence. Build verified unchanged. |`

### Step 2: Update PROJECT.md

Move STRU-04 from the "Active" section to the "Validated" section:
- Remove `- [ ] STRU-04: Composables disposition (v1.0 audit: 15/17 view-local, accept as canonical, extract 2 candidates only)` from the Active list
- Add `- ✓ STRU-04: Composables disposition — view-local accepted as canonical, 2 candidates kept (Phase 5, 2026-04-08)` to the Validated list

Update the "Accumulated Context" section in STATE.md — add a note:
- `STRU-04 CLOSED (2026-04-08): view-local is canonical pattern per STANDARDS.md, 2 extraction candidates both kept view-local`

### Step 3: Verify build

```bash
cd web/frontend && npm run build
```

This confirms no files were inadvertently modified. Build must exit 0.
</action>

<acceptance_criteria>
- `.planning/REQUIREMENTS.md` contains `- [x] **COMP-01**`
- `.planning/REQUIREMENTS.md` contains `- [x] **COMP-02**`
- `.planning/REQUIREMENTS.md` contains `- [x] **COMP-03**`
- `.planning/REQUIREMENTS.md` traceability table shows "Complete" for COMP-01, COMP-02 and "N/A" for COMP-03
- `.planning/PROJECT.md` contains `STRU-04` in the Validated section
- `.planning/PROJECT.md` does NOT contain `STRU-04` in the Active section
- `.planning/STATE.md` contains `STRU-04 CLOSED`
- `cd web/frontend && npm run build` exits 0
</acceptance_criteria>

# ArtDeco OpenSpec Archive Ownership Preflight

> Date: 2026-05-29
> Scope: `add-artdeco-impeccable-design-gate` archive ownership check.
> Boundary: documentation only. No route changes, no API contract changes, no shared component extraction, no OpenSpec archive mutation in the root worktree.

## 1. Purpose

This preflight verifies whether the active root worktree can safely archive `openspec/changes/add-artdeco-impeccable-design-gate`.

The key question is whether the existing root `openspec/specs/artdeco-design-governance/` path belongs to this ArtDeco impeccable governance line or to another already-started OpenSpec governance line.

## 2. Current Root Worktree Evidence

Relevant root status:

```text
?? openspec/specs/artdeco-design-governance/
```

The root worktree already contains an untracked canonical spec file at:

```text
openspec/specs/artdeco-design-governance/spec.md
```

Current root spec summary:

```text
bytes=6708
sha256=69511d51818a723db1d0e8493541c23d70d105ddae7aea35f1263c0affcb5775
firstHeading=# artdeco-design-governance Specification
```

Root requirement titles:

1. Routed Pages Consume Canonical Status Surfaces
2. Routed Overlay Surfaces Follow Active Overlay Tokens
3. Routed Tooltip Debt Must Be Explicitly Proven
4. Routed-Page Cleanup Must Stay Distinct From Workbench Cleanup
5. ArtDeco Design Contract Precedence
6. Shared Primitive State-Machine Adoption
7. Canonical Shared Semantic Surfaces
8. Compatibility Layers Stay Non-Canonical
9. Decorative Corner Marker Exception Preservation

Interpretation:

- This canonical spec is not the direct archive output of `add-artdeco-impeccable-design-gate`.
- Its requirement set is about routed-page cleanup, overlays, tooltip debt, shared primitives, compatibility layers, and decorative markers.
- Those topics are adjacent to ArtDeco governance, but they are not the five impeccable gate requirements from the active change.

## 3. Archive Preflight Worktree Evidence

Existing worktree:

```text
.worktrees/artdeco-archive-preflight-de0c5b8c9
```

Branch:

```text
archive/artdeco-impeccable-design-gate
```

Archive commit:

```text
efa776cf0 chore(openspec): archive ArtDeco design gate change
```

Commit file list:

```text
R100 openspec/changes/add-artdeco-impeccable-design-gate/design.md
     openspec/changes/archive/2026-05-28-add-artdeco-impeccable-design-gate/design.md
R100 openspec/changes/add-artdeco-impeccable-design-gate/proposal.md
     openspec/changes/archive/2026-05-28-add-artdeco-impeccable-design-gate/proposal.md
R100 openspec/changes/add-artdeco-impeccable-design-gate/specs/artdeco-design-governance/spec.md
     openspec/changes/archive/2026-05-28-add-artdeco-impeccable-design-gate/specs/artdeco-design-governance/spec.md
R100 openspec/changes/add-artdeco-impeccable-design-gate/tasks.md
     openspec/changes/archive/2026-05-28-add-artdeco-impeccable-design-gate/tasks.md
A    openspec/specs/artdeco-design-governance/spec.md
```

Preflight archived spec summary:

```text
bytes=4612
sha256=c4d83df077d65e11319408ffe32b1ad2ca32e21274bb0446a971075a2a7213f0
firstHeading=# artdeco-design-governance Specification
```

Preflight requirement titles:

1. Impeccable Design Documentation Gate
2. Impeccable ArtDeco Audit Sequence
3. Approval Boundary Before Craft
4. ArtDeco Optimization Priority Classification
5. Post-Approval ArtDeco Implementation Sequence

Interpretation:

- The preflight worktree archive output exactly matches the `add-artdeco-impeccable-design-gate` change.
- It is the clean archive candidate for this line.
- It does not include the nine root-worktree canonical requirements listed above.

## 4. Ownership Verdict

Do not run `openspec archive add-artdeco-impeccable-design-gate` in the root worktree right now.

Reason:

- The root worktree already contains an untracked canonical `artdeco-design-governance` spec with a different requirement set.
- Running archive in root could overwrite, merge, or confuse ownership with that existing untracked spec work.
- A clean archive result already exists in the dedicated archive preflight worktree at commit `efa776cf0`.

The root worktree should treat archive as blocked by spec ownership, not by validation.

## 5. Validation Status

The active change itself remains valid:

```text
openspec validate add-artdeco-impeccable-design-gate --strict
Change 'add-artdeco-impeccable-design-gate' is valid
```

`openspec list` reports the change as complete.

The remaining question is integration ownership, not OpenSpec format correctness.

## 6. Recommended Integration Routes

### Option A: Use the Archive Preflight Branch

Use `archive/artdeco-impeccable-design-gate` as the archive deliverable.

Before merging:

1. Compare `efa776cf0` against the root worktree's untracked canonical spec.
2. Decide whether the five impeccable gate requirements should be appended to the nine existing root requirements.
3. Merge only after the canonical spec owner confirms the combined requirement set.

### Option B: Keep Root Change Active Temporarily

Keep `add-artdeco-impeccable-design-gate` active in root until the existing untracked canonical spec is committed or moved by its owner.

This avoids accidental ownership mixing in the dirty root worktree.

### Option C: Create a Fresh Archive Worktree

If the current preflight worktree is stale, create a fresh worktree from the current branch and re-run archive there.

Do this only after confirming what should happen to the existing canonical spec path.

## 7. Scope Confirmation

This preflight did not modify:

- `web/frontend/src/router/index.ts`
- `web/backend/app/api/**`
- `docs/api/**`
- `web/frontend/src/api/**`
- `web/frontend/src/components/**`
- routed Vue pages
- shared ArtDeco components

No route changes, API contract changes, or shared component extraction were performed.

## 8. Next Step

Recommended next step:

1. Confirm the owner / source of root `openspec/specs/artdeco-design-governance/spec.md`.
2. If it belongs to this ArtDeco line, merge the five impeccable gate requirements from `efa776cf0` into the root canonical spec in a deliberate spec-merge task.
3. If it belongs to another line, keep this archive isolated in `archive/artdeco-impeccable-design-gate` and do not archive from root.

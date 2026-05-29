# ArtDeco Spec Ownership Decision

> Date: 2026-05-29
> Scope: ownership decision for root `openspec/specs/artdeco-design-governance/spec.md`.
> Boundary: documentation only. No route changes, no API contract changes, no shared component extraction, no OpenSpec archive mutation.

## 1. Decision

The root worktree's untracked canonical spec:

```text
openspec/specs/artdeco-design-governance/spec.md
```

does not belong to the current `add-artdeco-impeccable-design-gate` line.

It belongs to the earlier ArtDeco governance work represented by two archived changes:

1. `openspec/changes/archive/2026-05-12-align-business-route-status-and-tooltip-surfaces/`
2. `openspec/changes/archive/2026-05-12-align-artdeco-stateful-primitives-with-design/`

Therefore, this impeccable line must not take ownership of the root canonical spec and must not run root `openspec archive add-artdeco-impeccable-design-gate` while that untracked canonical spec remains unresolved.

## 2. Evidence

Root canonical spec summary:

```text
sha=69511d51818a723db1d0e8493541c23d70d105ddae7aea35f1263c0affcb5775
requirements=9
```

Root canonical requirements:

1. Routed Pages Consume Canonical Status Surfaces
2. Routed Overlay Surfaces Follow Active Overlay Tokens
3. Routed Tooltip Debt Must Be Explicitly Proven
4. Routed-Page Cleanup Must Stay Distinct From Workbench Cleanup
5. ArtDeco Design Contract Precedence
6. Shared Primitive State-Machine Adoption
7. Canonical Shared Semantic Surfaces
8. Compatibility Layers Stay Non-Canonical
9. Decorative Corner Marker Exception Preservation

Archived change `2026-05-12-align-business-route-status-and-tooltip-surfaces` contributes the first four requirements:

1. Routed Pages Consume Canonical Status Surfaces
2. Routed Overlay Surfaces Follow Active Overlay Tokens
3. Routed Tooltip Debt Must Be Explicitly Proven
4. Routed-Page Cleanup Must Stay Distinct From Workbench Cleanup

Archived change `2026-05-12-align-artdeco-stateful-primitives-with-design` contributes the final five requirements:

1. ArtDeco Design Contract Precedence
2. Shared Primitive State-Machine Adoption
3. Canonical Shared Semantic Surfaces
4. Compatibility Layers Stay Non-Canonical
5. Decorative Corner Marker Exception Preservation

The current active change `add-artdeco-impeccable-design-gate` has a different requirement set:

1. Impeccable Design Documentation Gate
2. Impeccable ArtDeco Audit Sequence
3. Approval Boundary Before Craft
4. ArtDeco Optimization Priority Classification
5. Post-Approval ArtDeco Implementation Sequence

That current-change requirement set matches the dedicated archive preflight worktree:

```text
.worktrees/artdeco-archive-preflight-de0c5b8c9
branch: archive/artdeco-impeccable-design-gate
commit: efa776cf0 chore(openspec): archive ArtDeco design gate change
```

## 3. Ownership Classification

| Path | Owner / Source | Status |
|---|---|---|
| `openspec/specs/artdeco-design-governance/spec.md` | Earlier ArtDeco primitive + routed-page governance changes from 2026-05-12 | Untracked in root; not owned by this line |
| `openspec/changes/add-artdeco-impeccable-design-gate/**` | Current impeccable design-gate change | Active and valid |
| `.worktrees/artdeco-archive-preflight-de0c5b8c9` | Dedicated archive preflight for the current impeccable gate | Clean archive candidate |

## 4. Consequences

This line should continue to avoid:

- root OpenSpec archive mutation
- root canonical spec overwrite
- direct merging of impeccable gate requirements into the nine existing canonical requirements
- route changes
- API contract changes
- shared component extraction

If the impeccable gate requirements should become canonical in root later, that should be handled as a deliberate spec-merge task, not as a side effect of archiving from a dirty root worktree.

## 5. Recommended Next Action

Close this branch of work as a documented ownership decision.

Recommended follow-up options:

1. Keep `add-artdeco-impeccable-design-gate` active in root until the owner of the untracked root canonical spec commits or moves it.
2. Use the existing `archive/artdeco-impeccable-design-gate` branch as the isolated archive deliverable if a clean archive record is needed.
3. Open a separate OpenSpec spec-merge task if the five impeccable gate requirements should be appended to the nine existing canonical requirements.

## 6. Verification

Evidence commands completed before this decision:

- `openspec validate add-artdeco-impeccable-design-gate --strict`: valid
- requirement-title comparison across root canonical spec, archived ArtDeco governance changes, active impeccable change, and archive preflight worktree
- source scan showing the root canonical requirement titles align with the two 2026-05-12 archived ArtDeco governance changes

No implementation files were modified for this decision.

> Already resolved by the P3 implementation line. Do not publish this as a new
> GitHub issue. Retain the body file only as audit history.
>
> Evidence: P3-A3 decision record names the `risk/` package as canonical, and
> orphan risk files were deleted in commit `243d40a8a`.

## What to decide

Choose the canonical risk router contract and define how legacy risk surfaces
and v31 routes remain compatible.

## OpenSpec requirement

- C tasks 2.3, 2.6, 2.7

## Acceptance criteria

- Decision record names canonical risk route surface.
- v31 compatibility is retained, retired, or mapped with explicit approval.
- Service consumers and frontend/test callers are classified.
- Rollback trigger is named.
- Decision record states whether `web/backend/CONTEXT.md`,
  `docs/FUNCTION_TREE.md`,
  or related governance documents require updates.
- No route deletion or v31 compatibility change is approved by this issue alone.

## Publication status

Do not publish. The decision has already been made and implemented on the P3
line. This body file is retained only so the original draft package remains
auditable.

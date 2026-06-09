> Already resolved by the P3 implementation line. Do not publish this as a new
> GitHub issue. Retain the body file only as audit history.
>
> Evidence: P3-A1 decision record names the `announcement/` package as
> canonical, and `announcement.py` was deleted in commit `243d40a8a`.

## What to decide

Choose the canonical announcement router contract and compatibility path based
on route/OpenAPI evidence and consumer matrix.

## OpenSpec requirement

- C tasks 2.1, 2.6, 2.7

## Acceptance criteria

- Decision record identifies canonical path, retained compatibility paths, and
  retirement candidates.
- Decision cites current route table and OpenAPI evidence.
- Consumer matrix covers backend imports, frontend calls, tests, scripts, and
  documentation-only references.
- Rollback trigger is named.
- Decision record states whether `web/backend/CONTEXT.md`,
  `docs/FUNCTION_TREE.md`,
  or related governance documents require updates.
- No router deletion or prefix mutation is approved by this issue alone.

## Publication status

Do not publish. The decision has already been made and implemented on the P3
line. This body file is retained only so the original draft package remains
auditable.

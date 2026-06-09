> Already resolved by the P3 implementation line. Do not publish this as a new
> GitHub issue. Retain the body file only as audit history.
>
> Evidence: P3-A2 decision record names the `strategy_management/` package as
> canonical, and strategy router convergence landed in commit `1241c4b7e`.

## What to decide

Choose the canonical strategy router contract and define how `strategy.py`,
`strategy_mgmt.py`, `strategy_management.py`, `strategy_management/`, and
`strategy_list_mock.py` remain compatible or exit.

## OpenSpec requirement

- C tasks 2.2, 2.6, 2.7

## Acceptance criteria

- Decision record names canonical strategy route surface.
- Mock router behavior is classified as production, development-only, or
  compatibility surface.
- Frontend/test consumers are classified.
- Rollback trigger is named.
- Decision record states whether `web/backend/CONTEXT.md`,
  `docs/FUNCTION_TREE.md`,
  or related governance documents require updates.
- No flat module deletion is approved by this issue alone.

## Publication status

Do not publish. The decision has already been made and implemented on the P3
line. This body file is retained only so the original draft package remains
auditable.

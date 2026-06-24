# B4.012-M3a-E3b-A Repository Hygiene Docs Truth Baseline Decision Closeout

Date: 2026-06-24
Node: `b4-012-m3a-e3b-a-repository-hygiene-docs-truth-baseline-decision`
Program: `.governance/programs/artdeco-web-design-governance`
Closeout scope: governance-only baseline decision closeout

## Scope

This closeout closes the A baseline decision node as a consumed no-source decision package. It does not implement docs truth repair, unblock E3a, or change test policy.

Allowed paths used for this closeout:

- `.governance/active-gates.json`
- `.governance/active-gates.md`
- `.governance/programs/artdeco-web-design-governance/nodes.json`
- `docs/reports/worklogs/claude-auto/b4-012-m3a-e3b-a-repository-hygiene-docs-truth-baseline-decision-closeout-2026-06-24.md`

## Baseline Decision Recap

The original A decision package established that the broad repository-hygiene pytest failures were pre-existing docs truth baseline debt outside the narrow E3a lint/import scope.

It recommended:

- an E3a-R1 lint-only recovery package with an explicit focused-pytest baseline waiver;
- an E3b-B docs truth repair atlas;
- a later focused test-policy decision only after the docs truth repair decisions were complete.

## Downstream Consumption

- E3a-R1 is closed:
  - `b4-012-m3a-e3a-r1-repository-hygiene-lint-only-recovery-authorization`
- E3b-B repair atlas is closed:
  - `b4-012-m3a-e3b-b-repository-hygiene-docs-truth-repair-atlas`
- The B repair-atlas child families are closed:
  - `b4-012-m3a-e3b-c-repository-hygiene-reports-index-family`
  - `b4-012-m3a-e3b-d-root-task-report-index-artifacts-family`
  - `b4-012-m3a-e3b-e-docs-guides-family-split`

## Remaining Boundary

The E3a parent remains separately blocked:

- `b4-012-m3a-e3a-repository-hygiene-unit-script-authorization`

That blocker is not cleared by this A closeout. Any future test-policy split, focused repository-hygiene test refactor, or E3a unblock must be authorized as a separate node/package.

## Boundary Confirmation

- No source, runtime, test, OpenSpec, or root agent-rule files were modified by this closeout.
- No E3a parent unblock was performed.
- No docs truth repair, assertion update, skip/xfail addition, or test-policy implementation was performed.
- External untracked worklogs under `docs/reports/worklogs/claude-auto/` remain isolated and are not part of this closeout package.

## Verification

- `git diff --cached --check`
  - Result: passed with no output.
- `ft-governance validate`
  - Result: `governance validation passed`.
- `node .gitnexus/run.cjs verify-staged --repo mystocks`
  - Result: `4 files`, `0 symbols`, `0 affected processes`, `risk low`.
- `node .gitnexus/run.cjs detect-changes --scope staged --repo mystocks`
  - Result: `4 files`, `0 symbols`, `0 affected processes`, `risk low`.
- `OPENDOG verification --id mystocks --json`
  - Result: `fresh`, no failing runs, cleanup gate allowed.

## Closeout Decision

A is ready to close as a consumed no-source baseline decision. The closeout gate passed, downstream E3a-R1 and B repair-atlas decisions have been consumed, and remaining E3a/test-policy work remains outside this node.

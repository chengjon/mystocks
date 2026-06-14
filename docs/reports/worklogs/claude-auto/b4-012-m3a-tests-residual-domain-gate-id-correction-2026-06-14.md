# B4.012-M3a tests residual domain gate ID correction

Date: 2026-06-14
Mode: governance metadata only
Baseline HEAD: `77807e11d B4.012-M3a: audit tests residual domain`

## Scope

This correction normalizes the FUNCTION_TREE node identity for the B4.012-M3a tests residual no-source audit.

Canonical active node:

- `b4-012-m3a-tests-residual-domain-audit`

Archived duplicate node:

- `b4-012-tests-residual-domain-audit`

## Reason

The tests residual audit report was committed correctly, but the first governance node used a non-canonical ID that omitted the `m3a` segment. A canonical `b4-012-m3a-tests-residual-domain-audit` node already existed in `planning`, so the evidence was moved to the canonical node and the duplicate was archived.

## Metadata Action

- Recorded the existing audit report as evidence for `b4-012-m3a-tests-residual-domain-audit`.
- Transitioned `b4-012-m3a-tests-residual-domain-audit` to `decision-prepared`.
- Transitioned `b4-012-tests-residual-domain-audit` to `archived`.

## Boundary

No source, test, runtime, API, frontend, backend, OpenSpec, ST-HOLD, `marketKlineData`, config, or external dirty file was modified.

The M3a audit conclusions are unchanged:

- `tests/**` has 231 dirty entries in the audited baseline.
- No `tests/**` deletion-retirement action is authorized.
- No untracked tests are accepted or staged.
- Follow-up implementation must be split by test family and explicitly authorized.

## Verification

- `ft-governance validate` passes after the correction.
- Active gates should include the canonical M3a node and should not include the archived duplicate node.

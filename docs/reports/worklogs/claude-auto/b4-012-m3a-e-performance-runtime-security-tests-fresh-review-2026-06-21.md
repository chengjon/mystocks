# B4.012-M3a-E Performance / Runtime / Security Tests Fresh Review

Date: 2026-06-21
Repository: `/opt/claude/mystocks_spec`
Baseline HEAD: `c093808ed5d671d1d78c41db8558c40904f632ca`
Mode: no-source family reactivation review

## Scope

This review refreshes the B4.012-M3a-E performance/runtime/security tests parent after B4.013 closeout and the B4.012-M3a test-domain parent reactivation.

The immediate target is only:

- `b4-012-m3a-e-performance-runtime-security-tests-split`

This package does not authorize test edits, source edits, runtime edits, OpenSpec edits, OpenStock edits, deletion, restore, untracked staging, or broad test acceptance.

## Current Gate Truth

- `b4-012-m3a-tests-residual-domain-audit` is `decision-prepared`.
- `b4-012-m3a-e-performance-runtime-security-tests-split` is still `blocked` only because it was paused by the B4.013 runtime-first reset.
- The E parent may return to `decision-prepared` because B4.013 no longer blocks residual test-family decision work.

This reactivation is not implementation approval. It only restores the family-level decision point for later, narrower authorization packages.

## Fresh Dirty Surface

The current keyword-based performance/runtime/security scan remains broad and mixed:

| Group | Count | Notes |
| --- | ---: | --- |
| Total broad matches | 63 | Includes E candidates plus known overlaps that must stay routed to B/C/D/U families. |
| Tracked | 52 | Tracked dirty tests require narrower package authorization before staging. |
| Untracked | 11 | Provenance-only until the untracked review family explicitly decides preserve/delete/ignore. |
| `tests/performance/**` | 19 | Includes the original tracked E performance/runtime set plus untracked performance/deployment candidates. |
| `tests/security/**` | 7 | Tracked security/compliance scanner family. |
| `tests/e2e/**` | 6 | Explicitly belongs to D/D1, not E. |
| `tests/unit/**` runtime/governance-adjacent | 11 | Needs narrower owner review before any authorization. |
| `scripts/tests/**` performance/security-adjacent | 7 | Script-test family; do not mix with application runtime/performance tests. |
| `web/backend/tests/**` security/runtime-adjacent | 4 | API/backend/security overlap; route through B-family review. |
| `web/frontend/**` runtime-adjacent | 1 | Frontend/untracked provenance boundary; do not accept through E. |

The original E split identified these primary tracked subfamilies:

- Performance/runtime governance tests under `tests/performance/**`: 12 tracked candidates.
- Security/compliance scanner tests under `tests/security/**`: 7 tracked candidates.
- Repository hygiene/governance script test under `tests/unit/scripts/**`: 1 tracked candidate.
- Performance/deployment/script governance untracked candidates: provenance-only.

## Boundary Decisions

E remains a parent decision family, not a single implementation batch.

Routing stays fixed:

- API/backend overlap remains under `B4.012-M3a-B`.
- Adapter/data-source overlap remains under `B4.012-M3a-C`.
- E2E/frontend overlap remains under `B4.012-M3a-D` and `D1`.
- Untracked test provenance remains under `B4.012-M3a-U`.
- OpenStock/provider runtime remains outside MyStocks; MyStocks only consumes/adapts provider data.

## Risk Notes

- Performance/runtime tests can encode environment-specific assumptions. Future packages must separate syntax/contract cleanup from runtime acceptance changes.
- Security/compliance tests can weaken real guardrails if assertions are relaxed. Future packages must preserve scanner and compliance semantics unless separately approved.
- Deployment/runtime observability tests may depend on PM2, local ports, generated reports, or machine state. Any environment skip must be explicit and non-silent.
- Broad keyword matches include D1 E2E and B-family backend/security files; these must not be staged through E parent reactivation.

## Recommended Next Queue

1. `B4.012-M3a-E1 performance runtime tracked authorization prep`
   - Candidate scope: tracked `tests/performance/**` performance/runtime governance files.
   - Gate: performance baseline/runtime environment assumptions documented before implementation.

2. `B4.012-M3a-E2 security compliance tracked authorization prep`
   - Candidate scope: tracked `tests/security/**` security/compliance scanner files.
   - Gate: security ownership and assertion-preservation review.

3. `B4.012-M3a-E3 governance script test authorization prep`
   - Candidate scope: tracked repository hygiene / governance script tests after exact path recheck.
   - Gate: governance helper behavior review.

4. `B4.012-M3a-U untracked tests provenance review`
   - Candidate scope: untracked performance/deployment/script/frontend test candidates.
   - Gate: provenance and preserve/delete/ignore decision before any staging.

## Verification Plan

Before commit:

- `git diff --cached --check`
- FUNCTION_TREE validate
- GitNexus staged verification and staged change detection
- OPENDOG verification

After commit:

- GitNexus analyze
- staged index empty
- `b4-012-m3a-e-performance-runtime-security-tests-split` is `decision-prepared`
- no test/source/runtime/OpenSpec/OpenStock files staged

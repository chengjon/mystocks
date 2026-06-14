# B4.012-M3a-B4 tracked contract engine tests authorization prep

Date: 2026-06-14
Mode: no-source authorization preparation, no test/source edits
Parent split: `b4-012-m3a-b-api-backend-contract-tests-split`

## Scope

This package prepares a narrow future authorization boundary for tracked contract-engine and contract-impact unit tests only.

Current no-source status confirms 2 tracked modified candidates:

- `tests/unit/api/test_contract_impact_analyzer.py`
- `tests/unit/contract/test_contract_engine_runtime_source.py`

Both candidates are tracked modified files. No untracked contract or deployment test candidate is included in this batch.

## Explicit Exclusions

Excluded from this batch:

- `tests/api/**`
- `tests/backend/**`
- untracked contract/deployment candidates
- frontend/E2E specs
- security/compliance/performance families
- M3a-A test-infra/helper batch
- M3a-B1 API file_tests authorization batch
- M3a-B2 API root file-tests authorization batch
- M3a-B3 backend regression authorization batch
- M3a-U untracked test provenance review
- any source, runtime, OpenSpec, OpenStock, deletion, restore, or staging action

## Risk

Risk level: high.

These tests are tied to contract impact and runtime-source boundary behavior. Future implementation must verify contract engine expectations before accepting dirty deltas and must not modify runtime source, OpenSpec, generated contracts, or deployment tests without a separate explicit authorization.

## Gate Recommendation

Future implementation authorization, if approved, should allow only the 2 listed tracked test files plus a B4 closeout report. It should require:

- exact staged allowlist for B4 paths only
- contract engine/runtime-source boundary review
- focused contract unit verification
- GitNexus staged verification and staged change detection
- OPENDOG blocker check

## Verification

No source or test files were modified during this preparation.

Current evidence:

- `git status --porcelain=v1` confirms both candidates are tracked modified files
- untracked contract/deployment candidates remain excluded for M3a-U/M3a-E routing
- B4 remains no-source until explicit approval

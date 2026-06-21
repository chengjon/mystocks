# B4.012-M3a-E2 Security Compliance Tracked Authorization Prep

- Date: 2026-06-21
- Node: `b4-012-m3a-e2-security-compliance-tracked-authorization`
- Parent: `b4-012-m3a-e-performance-runtime-security-tests-split`
- Source edits authorized: false

## No-Source Boundary Review

This package is authorization preparation only. It does not modify tests, source/runtime code, OpenSpec, OpenStock provider/runtime implementation, frontend files, E2E files, unit tests outside the exact E2 scope, ST-HOLD, or `marketKlineData`.

The current `tests/security/**` dirty surface is fully tracked:

- Tracked modified: 7
- Untracked: 0

Tracked E2 candidate files:

- `tests/security/test_security_compliance/compliance_test_engine_methods/part1.py`
- `tests/security/test_security_compliance/compliance_test_engine_methods/part2.py`
- `tests/security/test_security_compliance/helpers.py`
- `tests/security/test_security_compliance/utils.py`
- `tests/security/test_security_vulnerabilities/security_vulnerability_scanner_methods/part1.py`
- `tests/security/test_security_vulnerabilities/security_vulnerability_scanner_methods/part2.py`
- `tests/security/test_security_vulnerabilities/utils.py`

## Risk Assessment

Risk is medium by domain even though the files are tests. These files encode compliance and vulnerability-scanner behavior; implementation must preserve scanner semantics and compliance assertions. Any assertion relaxation, security bypass, source/runtime change, or production security behavior change is out of scope and requires separate authorization.

Observed shape:

- Compliance family includes helper dataclasses/enums, test wrappers, and split compliance engine mixins.
- Vulnerability family includes scanner mixins and test wrappers for SQL injection, XSS, CSRF, authentication, and dependency vulnerability checks.
- No untracked `tests/security/**` provenance candidates are currently part of this package.

## Proposed Authorization

Allowed implementation files:

- the 7 tracked E2 candidate files listed above
- E2 closeout worklog under `docs/reports/worklogs/claude-auto/`

Allowed implementation actions:

- syntax/lint standardization
- import/type hygiene inside the exact E2 files
- test helper consistency cleanup
- focused fixture correction where needed to keep current security/compliance contracts executable

Forbidden actions:

- no assertion weakening or security threshold relaxation
- no production source/runtime changes
- no OpenSpec/OpenStock provider/runtime changes
- no E1 performance files, D/D1 E2E files, U untracked provenance candidates, frontend files, backend source, ST-HOLD, or `marketKlineData`
- no deletion, restore, migration, or broad refactor

## Required Gates For Future Implementation

- `python -m py_compile` for the 7 E2 Python files
- `ruff check` for the 7 E2 Python files
- focused pytest for the two security families, with any environment-only blockers documented instead of weakened
- `git diff --cached --check`
- FUNCTION_TREE validate
- GitNexus `verify-staged` and `detect-changes --scope staged`
- OPENDOG verification
- precise staged scope containing only E2 allowed files, generated governance state, and the E2 closeout worklog

## Disposition

E2 is ready for user review as an authorization-prepared package. No source/test implementation is authorized until the node is explicitly approved for implementation.

# Active Gates

| Program | Node | Status | Current blocker | Next allowed | FT ref |
|---------|------|--------|-----------------|--------------|--------|
| artdeco-web-design-governance | b4-012-m3-residual-dirty-atlas-rebaseline | decision-prepared | - | prepare authorization | B4.012-M3 |
| artdeco-web-design-governance | b4-012-m3a-tests-residual-domain-audit | decision-prepared | - | prepare authorization | B4.012-M3a |
| artdeco-web-design-governance | b4-012-m3a-b-api-backend-contract-tests-split | decision-prepared | - | prepare authorization | B4.012-M3a-B |
| artdeco-web-design-governance | b4-012-m3a-c-adapter-data-source-tests-split | decision-prepared | - | prepare authorization | B4.012-M3a-C |
| artdeco-web-design-governance | b4-012-m3a-d-e2e-frontend-tests-split | decision-prepared | - | prepare authorization | B4.012-M3a-D |
| artdeco-web-design-governance | b4-012-m3a-e-performance-runtime-security-tests-split | decision-prepared | - | prepare authorization | B4.012-M3a-E |
| artdeco-web-design-governance | b4-012-m3a-u-untracked-tests-provenance-review | decision-prepared | - | prepare authorization | B4.012-M3a-U |
| artdeco-web-design-governance | b4-012-m3a-e3-governance-script-tests-split | decision-prepared | - | prepare authorization | B4.012-M3a-E3 |
| artdeco-web-design-governance | b4-012-m3a-e3a-repository-hygiene-unit-script-authorization | blocked | No-source revalidation shows py_compile and ruff pass, but focused pytest for tests/unit/scripts/test_repository_hygiene_paths.py remains red at 58 failed / 44 passed due broad repository-hygiene docs truth drift outside E3a lint/import scope. | unblock to authorization-prepared | B4.012-M3a-E3a |

_Generated from `.governance/active-gates.json`._

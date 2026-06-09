> Superseded body: do not publish this issue body directly.
> Its scope is merged into `14-build-shared-evidence-package.md`.

## What to build

Generate singleton/getter inventory, classify candidates by lifecycle class, and
mark candidates blocked by F import compatibility. Do not change lifecycle
ownership in this issue.

Existing P3 evidence to reuse:

- P3-A4 singleton lifecycle inventory in
  `docs/reports/quality/backend-audit-phase3-decision-records.md`.

Remaining scope is to convert that inventory into the E proposal's DI-specific
lifecycle classification and explicitly mark candidates blocked by the F Core
import compatibility matrix.

## OpenSpec requirement

- E tasks 1.2-1.6

## Acceptance criteria

- Singleton baseline artifact is generated or refreshed.
- Getter inventory artifact is generated.
- Existing P3-A4 lifecycle inventory is cited or superseded with fresher
  evidence.
- Candidates are classified as stateless helper, heavy service, adapter factory,
  cache-backed service, connection-backed service, or compatibility getter.
- Shared-Core candidates are marked blocked by F matrix.
- No lifecycle mutation is performed.

## Verification

```bash
python scripts/dev/backend_audit_baseline.py docs/reports/quality/generated
rg -n "^def get_\\w+\\(" web/backend/app > docs/reports/quality/generated/backend-getter-inventory.txt
```

## Blocked by

BLOCKED_BY_TODO: issue 1 approval.

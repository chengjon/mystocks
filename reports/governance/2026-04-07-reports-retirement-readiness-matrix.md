# Reports Retirement Readiness Matrix (2026-04-07)

## Scope

- repo slice:
  - selected `reports/` directories that already received retirement-readiness audits on `2026-04-07`
- goal:
  - summarize the current deletion-readiness state in one governance matrix
  - make the current repo-truth scannable without reopening all four audit documents
- non-goal:
  - do not replace the detailed source audits
  - do not authorize any deletion
  - do not create new directory-level retirement verdicts beyond the audited set

## Measured Inputs

Commands used:

```bash
ls reports/governance/2026-04-07-reports-*-retirement-readiness-audit.md

python - <<'PY'
from pathlib import Path
import re
files = sorted(Path("reports/governance").glob("2026-04-07-reports-*-retirement-readiness-audit.md"))
summary = []
for f in files:
    text = f.read_text(encoding="utf-8")
    code_path = re.search(r'`code_path_verdict`: `([^`]+)`', text).group(1)
    function_tree = re.search(r'`function_tree_verdict`: `([^`]+)`', text).group(1)
    readiness = "not retirement-ready" if "not retirement-ready" in text else "unknown"
    summary.append((f.name, code_path, function_tree, readiness))
print("audits", len(summary))
print("unsafe_to_delete", sum(1 for _, cp, _, _ in summary if cp == "unsafe_to_delete"))
from collections import Counter
print("function_tree", Counter(ft for _, _, ft, _ in summary))
for row in summary:
    print("\\t".join(row))
PY
```

Source audits summarized here:

- [2026-04-07-reports-cli-retirement-readiness-audit.md](/opt/claude/mystocks_spec/reports/governance/2026-04-07-reports-cli-retirement-readiness-audit.md)
- [2026-04-07-reports-data-cleaning-retirement-readiness-audit.md](/opt/claude/mystocks_spec/reports/governance/2026-04-07-reports-data-cleaning-retirement-readiness-audit.md)
- [2026-04-07-reports-phase7-monitoring-retirement-readiness-audit.md](/opt/claude/mystocks_spec/reports/governance/2026-04-07-reports-phase7-monitoring-retirement-readiness-audit.md)
- [2026-04-07-reports-quant-retirement-readiness-audit.md](/opt/claude/mystocks_spec/reports/governance/2026-04-07-reports-quant-retirement-readiness-audit.md)

Metric stance for this matrix:

- measured:
  - number of audited directories summarized here
  - number of audited directories with `unsafe_to_delete`
  - distribution of `function_tree_verdict` values
  - per-directory verdicts already recorded in the source audits
- historical baseline:
  - `N/A`
- inferred:
  - comparative retirement priority ordering in later sections
- target:
  - `N/A`

## Current Measured Summary

Measured on `2026-04-07` from the four source audits above:

- audited directories summarized in this matrix: `4`
- directories with `code_path_verdict = unsafe_to_delete`: `4`
- directories with `function_tree_verdict = 有效`: `2`
- directories with `function_tree_verdict = pending_classification`: `2`
- directories explicitly marked `not retirement-ready`: `4`

## Retirement Readiness Matrix

| Directory | Code Path Verdict | Function Tree Verdict | Current Retirement Verdict | Primary blocker type | Detailed audit |
|---|---|---|---|---|---|
| `reports/cli/` | `unsafe_to_delete` | `pending_classification` | not retirement-ready | migration-tail ambiguity plus dual-path coexistence with `docs/reports/cli_reports/` | [cli audit](/opt/claude/mystocks_spec/reports/governance/2026-04-07-reports-cli-retirement-readiness-audit.md) |
| `reports/data_cleaning/` | `unsafe_to_delete` | `有效` | not retirement-ready | active scheduler output path plus user-facing docs still point here | [data-cleaning audit](/opt/claude/mystocks_spec/reports/governance/2026-04-07-reports-data-cleaning-retirement-readiness-audit.md) |
| `reports/phase7_monitoring/` | `unsafe_to_delete` | `有效` | not retirement-ready | active script output sink mixed with retained historical snapshots | [phase7 monitoring audit](/opt/claude/mystocks_spec/reports/governance/2026-04-07-reports-phase7-monitoring-retirement-readiness-audit.md) |
| `reports/quant/` | `unsafe_to_delete` | `pending_classification` | not retirement-ready | retained historical result with unresolved final ownership and remaining doc-plan references | [quant audit](/opt/claude/mystocks_spec/reports/governance/2026-04-07-reports-quant-retirement-readiness-audit.md) |

## Exit Condition Snapshot

| Directory | Minimum exit condition before any future deletion proposal |
|---|---|
| `reports/cli/` | choose the canonical home for retained CLI report payloads, cut references down to one path, and record migration closure |
| `reports/data_cleaning/` | retire or redirect the scheduler output path and update operational docs that still teach this directory |
| `reports/phase7_monitoring/` | stop both monitoring scripts from writing here and then relocate or formally retain the historical snapshots |
| `reports/quant/` | decide whether the retained JSON still needs a canonical home, then reduce remaining governance and cleanup-path references |

## Inference From Measured Data

The following comparative ordering is inferred from the four source audits. It is not an additional measured fact.

### Closest to retirement

1. `reports/quant/`
   - no active script output path was measured in the source audit
   - remaining blockers are primarily ownership and path-reference cleanup

### Middle

2. `reports/cli/`
   - no active output script was measured
   - but the directory still sits in a migration-tail split with `docs/reports/cli_reports/`

### Furthest from retirement

3. `reports/phase7_monitoring/`
   - still an active output sink for two scripts
4. `reports/data_cleaning/`
   - still an active output sink and still taught by current operational docs

The middle and lower ordering reflects comparative blocker weight, not deletion approval.

## Governance Verdict

- current matrix verdict:
  - none of the audited directories are deletion-ready
- current repo-truth:
  - the fastest safe governance work is not deletion
  - the fastest safe governance work is path-ownership clarification and output-path retirement on the relevant active producers

## Explicit Non-Recommendation

This matrix does **not** recommend:

- deleting any audited directory now
- collapsing all four directories into one common verdict
- using relative closeness to retirement as approval to delete
- treating this summary matrix as a substitute for the underlying detailed audits

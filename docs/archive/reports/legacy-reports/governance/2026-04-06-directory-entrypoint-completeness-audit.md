# Directory Entrypoint Completeness Audit (2026-04-06)

## Scope

- Repo slice:
  - `reports/`
  - `docs/reports/`
  - `docs/reports/tasks/legacy/`
- Goal:
  - identify directories that may need a directory-level entrypoint to avoid parallel truth or metric wording drift
- Non-goal:
  - do not bulk-add `README.md` / `INDEX.md` to every directory
  - do not delete, merge, or move directories in this audit

## Measured Inputs

Commands used:

```bash
find reports -maxdepth 2 -type d | sort
find docs/reports -maxdepth 2 -type d | sort
python - <<'PY'
from pathlib import Path
for rel in ["reports", "docs/reports"]:
    root = Path(rel)
    dirs = sorted([p for p in root.iterdir() if p.is_dir()])
    total = len(dirs)
    none = []
    readme_only = []
    index_only = []
    both = []
    for d in dirs:
        has_readme = (d / "README.md").exists()
        has_index = (d / "INDEX.md").exists()
        if has_readme and has_index:
            both.append(d.name)
        elif has_readme:
            readme_only.append(d.name)
        elif has_index:
            index_only.append(d.name)
        else:
            none.append(d.name)
    print(rel, total, len(none), len(readme_only), len(index_only), len(both))
    print("none_dirs=", none)
PY
find reports/analysis -maxdepth 1 -type f | sort
find reports/compliance -maxdepth 1 -type f | sort
find reports/plans -maxdepth 1 -type f | sort
find reports/performance -maxdepth 1 -type f | sort
find reports/reviews -maxdepth 1 -type f | sort
```

Metric stance for this audit:

- measured:
  - directory counts and sample file counts listed below
- historical baseline:
  - `N/A`
- target:
  - `N/A`
- inferred:
  - priority recommendations and governance conclusions in later sections

### `reports/` top-level directories

Measured on `2026-04-06`:

- total directories: `23`
- no `README.md` and no `INDEX.md`: `17`
- `README.md` only: `1`
- `INDEX.md` only: `5`
- both `README.md` and `INDEX.md`: `0`

No-entry directories:

- `reports/analysis`
- `reports/bugs`
- `reports/compliance`
- `reports/coverage`
- `reports/data_cleaning`
- `reports/debug`
- `reports/integration`
- `reports/performance`
- `reports/phase7_monitoring`
- `reports/plans`
- `reports/quant`
- `reports/reviews`
- `reports/security`
- `reports/structure-baseline`
- `reports/troubleshooting`
- `reports/type_check`
- `reports/unit`

### `docs/reports/` top-level directories

Measured on `2026-04-06`:

- total directories: `29`
- no `README.md` and no `INDEX.md`: `2`
- `README.md` only: `0`
- `INDEX.md` only: `24`
- both `README.md` and `INDEX.md`: `3`

No-entry directories:

- `docs/reports/screenshots`
- `docs/reports/security`

### Focused content samples

Measured file counts at first level:

- `reports/analysis`: `19` files
- `reports/compliance`: `5` files
- `reports/plans`: `2` files
- `reports/performance`: `3` files
- `reports/reviews`: `2` files

Observed content characteristics:

- `reports/analysis`
  - contains `tech-debt-baseline.json`, backups, generated JSON, and package metadata
- `reports/compliance`
  - contains policy/result style markdown reports
- `reports/plans`
  - contains backlog/workplan style files
- `reports/performance`
  - contains baseline-named artifacts
- `reports/reviews`
  - contains timestamped review outputs

## Inference From Measured Data

The following priority judgments are inferred from the measured inputs above. They are not additional measured facts.

### High-priority candidate directories

These are the strongest candidates for a future directory-level entrypoint because the directory name and contents can be mistaken for active truth:

1. `reports/analysis`
   - reason:
     - contains baseline files and backups in the same slice
     - high risk of metric wording drift between historical baseline and current measured state
2. `reports/plans`
   - reason:
     - directory name implies active planning truth
     - no directory entrypoint currently explains whether files are active plans, historical plans, or backlog snapshots
3. `reports/performance`
   - reason:
     - contains baseline artifacts
     - high risk of historical baseline being reused as current measured value without re-verification

### Medium-priority candidate directories

1. `reports/compliance`
   - policy/report mix may benefit from a canonical entrypoint
2. `reports/reviews`
   - likely archive-style outputs, but no directory rule states that explicitly

### Low-priority or no-action directories for now

No immediate entrypoint action recommended in this audit for:

- `reports/bugs`
- `reports/coverage`
- `reports/data_cleaning`
- `reports/debug`
- `reports/integration`
- `reports/quant`
- `reports/security`
- `reports/structure-baseline`
- `reports/troubleshooting`
- `reports/type_check`
- `reports/unit`
- `reports/phase7_monitoring`
- `docs/reports/screenshots`
- `docs/reports/security`

Reason:

- current evidence is insufficient to prove these directories are acting as parallel truth sources
- bulk-filling entrypoints here would violate the “no mechanical proliferation” spirit of directory governance

## Governance Verdict

### Single source of truth verdict

- confirmed issue:
  - directory-entrypoint coverage across `reports/` is inconsistent
- not yet proven:
  - every directory without `README.md` or `INDEX.md` is a governance bug

Therefore:

- do not bulk-add directory entrypoints
- only add new entrypoints where the directory meaning can plausibly compete with active truth or metric interpretation

### Compatibility / shim verdict

- no compatibility layer, shim, or `*_new.py` retirement action is triggered by this audit
- no temporary entrypoint should be added as a stopgap

### Deletion verdict

- no deletions recommended
- code-path verdict and function-tree verdict were not completed for any directory member in this audit

## Recommended Next Wave

If one follow-up wave is approved, prioritize only:

1. `reports/analysis` directory-level README
2. `reports/plans` directory-level README
3. `reports/performance` directory-level README

And for each, require:

- canonical role statement
- metric wording rule if numbers are present
- statement about whether files are current truth, historical baseline, or archive-only
- explicit avoidance of duplicate sibling summaries

## Explicit Non-Recommendation

This audit does **not** recommend:

- adding `README.md` to every directory under `reports/`
- treating `reports/INDEX.md` as a reliable current directory truth source
- deleting archive directories based on age alone
- using missing entrypoint files as a proxy for deletion eligibility

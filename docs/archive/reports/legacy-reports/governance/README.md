# Governance Records

## Role

This directory stores focused governance closeout records and governance playbooks.

- It is not the live task execution board.
- It is not a parallel replacement for repository-root `TASK.md` / `TASK-REPORT.md`.
- It is not a dumping ground for temporary migration notes, backups, or mechanical splits.

## Rule Source

The rule body does not live here.

- Structural governance and migration-closure rules:
  - `architecture/STANDARDS.md`
- Current task truth:
  - repository-root `TASK.md`
  - repository-root `TASK-REPORT.md`

Use this directory for focused evidence and closeout records after or around real work, not as a second active planning system.

## Single Source of Truth

### Current state

For active ownership, current status, and current acceptance, use only the canonical task sources above.

Files in this directory should answer one of these needs only:

- focused closeout for one work item or micro-batch
- governance classification or archive decision
- governance process/playbook guidance

If a work item already has one focused closeout record here, do not create sibling duplicates such as:

- `*-summary.md`
- `*-final.md`
- `*-final-v2.md`
- another file that restates the same verdict with slightly different wording

## Migration / Compatibility Reporting

When a record here covers migration, compatibility retention, shim handling, or archive convergence, it must keep these concepts explicit:

- canonical source
- compatibility surface
- callers or consumers
- verification command
- exit condition

If exit condition is unknown, the migration is not fully closed; record that gap explicitly instead of implying completion.

## Deletion Guard

Do not delete governance records only because they look old or unreferenced.

When a record here discusses deletion or retirement readiness:

- policy truth stays in `openspec/specs/directory-governance/spec.md`
- machine truth stays in `governance/deletion-evidence.yaml` and `governance/waivers/deletion-evidence-waivers.yaml`
- records in this directory are evidence and analysis only, not deletion authorization
- if a future deletion proposal is mentioned, the record must name which exact registry path would carry that authorization

Before deleting or relocating a file in this directory, complete both checks:

- code-path verdict:
  - confirm whether active indexes, docs, exporters, scripts, or task flows still point at it
- function-tree verdict:
  - classify it explicitly, for example `historical archive`, `duplicate archive`, `active governance evidence`, or another clear state

No deletion should be justified by static search alone.

## Metric Wording

Any numbers recorded here must keep these categories separate:

- measured
- baseline
- inferred
- target

Historical snapshots must stay labeled as historical.
Do not present an archived number as the current repo value unless it is freshly re-measured and cited from the current canonical source.

## Evidence Discipline

Progress or closeout claims recorded here must keep the evidence source explicit.

- If a statement says something is done, converged, retired, or blocked, it must cite:
  - a concrete evidence path, or
  - the command / generated source that established that result
- If evidence is absent, record the statement as unverified context or planned work, not as completion proof
- Historical drafts with blank evidence fields may remain for traceability, but they do not establish current status

## Temporary Files / Mechanical Splits / Backups

This directory must not accumulate:

- `*_new.py`
- shim placeholders
- temp entry files
- `.bak` / `.backup`
- `part1` / `part2` / `part3` style mechanical splits
- duplicate summary copies created only to preserve a temporary view

If archival grouping is needed, prefer one directory-level README or one canonical closeout file over multiple duplicated layers.

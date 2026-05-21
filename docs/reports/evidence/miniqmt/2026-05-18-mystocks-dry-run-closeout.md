# MyStocks miniQMT Dry-Run Evidence Closeout

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-18

## Scope

This closeout covers the MyStocks-side `mystocks_dry_run` evidence line for miniQMT dataset `kline_daily_20260518_v1`.

The completed line is the raw/candidate identity:

- `dataset_version`: `kline_daily_20260518_v1`
- `lineage_id`: `lin_kline_daily_20260518_v1`
- `payload_hash`: `61eedd9cd029f6c0a3324b3e66be0d9b83402279cbd0aed75885459822ec13d1`
- `rows_hash`: `0efbcdd407ff0461c8d3f06a4dc6ac315c6b6ec177f783705ce8f57c233c1152`
- `quality_status`: `raw`
- `maturity`: `candidate`

This is not evidence for the validated forward identity `268b...`.

## MyStocks Artifacts

| Artifact | Path | SHA-256 | Role |
|---|---|---:|---|
| Evidence JSON | `docs/reports/evidence/miniqmt/2026-05-18-kline_daily_20260518_v1-mystocks-dry-run.evidence.json` | `683314efa9d9b5ac80ac2f13274fd523840f3bf9a42fbfac3663d9522fa11860` | MyStocks generated `mystocks_dry_run` evidence |
| Raw report | `docs/reports/evidence/miniqmt/logs/mystocks_dry_run_kline_daily_20260518_v1.json` | `8513b2cb207e963347fec78142083527913718510363bed83a4ebbf543bbfd69` | Redacted dry-run source report referenced by evidence |
| Operator status snapshot | `docs/reports/evidence/miniqmt/operator-supplied-miniqmt-acceptance-status.json` | n/a | Operator-supplied miniQMT result snapshot; not a miniQMT business-state source and not proof of a PostgreSQL write |

The operator status snapshot deliberately includes `is_ledger_truth_source=false`. If PostgreSQL ledger backfill is required later, write it through the `market_dataset_evidence_runs` update path as an operator-supplied MyStocks consumer audit snapshot. The backfilled row must still not be treated as miniQMT promotion-state truth.

## Change Inventory

This slice is carried by the following MyStocks-side files:

| Area | Path | Role |
|---|---|---|
| Release client and evidence service | `src/adapters/miniqmt_market_data.py` | Consume miniQMT published dataset manifests/artifacts, verify hashes, run controlled dry-run checks, generate validator-compatible evidence, and preserve the public import facade |
| Consumer audit ledger module | `src/adapters/miniqmt_market_data_ledger.py` | Hold evidence run result metadata plus MyStocks-side `market_dataset_evidence_runs` insert/status-update helpers |
| Operator CLI | `scripts/market_data/run_miniqmt_controlled_evidence.py` | Make dataset identity, bundle/manifest/artifact inputs, output directory, and optional PostgreSQL DSN explicit and repeatable |
| Consumer audit ledger migration | `scripts/migrations/005_market_dataset_evidence_runs.sql` | Provide MyStocks-side `market_dataset_evidence_runs` audit storage; not a miniQMT promotion registry |
| Focused tests | `tests/unit/adapters/test_miniqmt_market_data.py` | Cover release loading, artifact verification, dry-run validation, evidence JSON, CLI output, and optional ledger writes |
| OpenSpec change | `openspec/changes/add-miniqmt-market-data-controlled-evidence-consumer/` | Record the contract, design, tasks, review, and spec deltas for this consumer capability |
| Evidence handoff | `docs/reports/evidence/miniqmt/` | Store generated evidence, raw report, operator snapshot, closeout report, and external follow-up tracker |

## Hard Rules

These rules remain fixed for this closeout:

- Closeout artifacts record completed facts only. They are not business state sources. PostgreSQL ledger backfill, if performed, is MyStocks consumer audit only and does not replace miniQMT promotion-state truth.
- Validated forward identity evidence is tracked separately from the completed raw/candidate `mystocks_dry_run` line.
- Authoritative-ready remains an explicit manual gate. MyStocks evidence apply must not trigger default promotion, source cutover, or Quantix ClickHouse writes.

## miniQMT Acceptance

miniQMT accepted the MyStocks raw/candidate evidence line.

- miniQMT commit: `05c5788 Record MyStocks dry-run evidence acceptance`
- miniQMT evidence target: `D:/MyCode3/miniQMT/DOCS/xtdata-api/evidence/2026-05-18-kline_daily_20260518_v1-mystocks-dry-run.evidence.json`
- miniQMT receive-attempt record: `D:/MyCode3/miniQMT/DOCS/xtdata-api/2026-05-18-mystocks-controlled-evidence-receive-attempt.md`
- miniQMT receive-attempt status lines: `local validator executed: yes`, `server preview executed: yes`, `server apply executed: yes`

Recorded MyStocks-side operator-supplied statuses:

- `miniqmt_validation_status`: `passed`
- `miniqmt_preview_status`: `passed`
- `miniqmt_apply_status`: `applied`

## Current State

`mystocks_dry_run` is completed for the raw/candidate identity. MyStocks should not continue adding functionality to this completed slot unless a new upstream contract change is opened.

Remaining work is external follow-up:

- Quantix validated forward `quantix_regression` evidence has since been accepted by miniQMT and is no longer the blocking follow-up.
- MyStocks validated forward `mystocks_dry_run` evidence for the `payload_hash=268b62bb0fb0891833ef1998d4993d6531cc6a9d84aaecb911da0cd559d2357e` identity has now been generated and accepted by miniQMT.
- miniQMT manual promote beyond `validated` to `authoritative-ready` has since been completed.
- Remaining miniQMT owner/operator gates are authoritative approval and rollback/fallback readiness.

See `docs/reports/evidence/miniqmt/2026-05-18-external-followups.md` for the external follow-up tracker. That tracker is not a MyStocks implementation backlog for the completed raw/candidate `mystocks_dry_run` slot.

MyStocks evidence apply does not imply source cutover, Quantix ClickHouse writes, or automatic final `authoritative` approval.

## Verification Refresh

Date: 2026-05-19

Latest local verification for this completed slice:

- Focused pytest for `tests/unit/adapters/test_miniqmt_market_data.py` passed with `--no-cov`: 19 passed.
- Ruff check passed for the release client, CLI, and focused unit tests.
- `openspec validate add-miniqmt-market-data-controlled-evidence-consumer --strict` passed.
- Evidence JSON hash matched the operator snapshot, raw report hash matched the operator snapshot, and the operator snapshot remained non-truth-source.
- Raw report checks stayed aligned with the accepted dry-run semantics: `writes_performed=false`, `failed_checks=0`, `row_count=2`, `field_mapping_version=miniqmt.kline_daily.v1`, `artifact_sha256_verified=true`, and `placeholder_count=0`.

Coverage note: the focused pytest refresh uses `--no-cov` because this repository enforces a global coverage fail-under threshold that is not meaningful for a single-file slice verification. A focused run with coverage collection still executed all 19 tests successfully, but failed the global coverage threshold.

## Reviewer Checklist

Use this checklist for review handoff:

- Confirm the MyStocks implementation remains consumer-only: no miniQMT promotion registry writes, no source cutover, and no Quantix ClickHouse writes.
- Confirm `mystocks_dry_run` evidence is bound only to the raw/candidate identity `payload_hash=61eedd9cd029f6c0a3324b3e66be0d9b83402279cbd0aed75885459822ec13d1`.
- Confirm `operator-supplied-miniqmt-acceptance-status.json` remains an operator-supplied audit snapshot and not a miniQMT business-state source.
- Confirm Quantix regression evidence and validated forward identity evidence remain separate external follow-up tracks.
- Confirm final `authoritative` remains an explicit owner/operator approval gate with rollback/fallback constraints.
- Re-run focused checks if needed: `pytest tests/unit/adapters/test_miniqmt_market_data.py -q --no-cov`, `ruff check src/adapters/miniqmt_market_data.py scripts/market_data/run_miniqmt_controlled_evidence.py tests/unit/adapters/test_miniqmt_market_data.py`, and `openspec validate add-miniqmt-market-data-controlled-evidence-consumer --strict`.

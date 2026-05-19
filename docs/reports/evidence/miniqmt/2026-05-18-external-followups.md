# miniQMT External Follow-Ups After MyStocks Dry-Run Closeout

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-18

Last updated: 2026-05-19

This tracker records work that remains outside the completed MyStocks raw/candidate `mystocks_dry_run` implementation line.

It must not be read as a MyStocks implementation backlog for the completed slot.

miniQMT follow-up reference: `D:\MyCode3\miniQMT\DOCS\xtdata-api\2026-05-19-post-quantix-remaining-gates-runbook.md`.

## Completed Baseline

- MyStocks raw/candidate `mystocks_dry_run`: completed
- miniQMT local validator: passed
- miniQMT server preview: passed
- miniQMT server apply: applied
- Completed identity: `payload_hash=61eedd9cd029f6c0a3324b3e66be0d9b83402279cbd0aed75885459822ec13d1`
- Evidence SHA-256: `683314efa9d9b5ac80ac2f13274fd523840f3bf9a42fbfac3663d9522fa11860`
- Quantix validated forward `quantix_regression`: completed and accepted by miniQMT validator / preview / apply
- Quantix accepted identity: `payload_hash=268b62bb0fb0891833ef1998d4993d6531cc6a9d84aaecb911da0cd559d2357e`

## Follow-Up Tracks

| Track | Owner | Current status | Entry condition | Done condition | Must not imply |
|---|---|---|---|---|---|
| Quantix regression evidence | Quantix / miniQMT gate owner | Completed | Quantix provides real `quantix_regression` evidence for the target dataset identity | miniQMT validates, previews, and applies the Quantix evidence; `quantix_regression` is no longer a promotion gap | Quantix acceptance does not cover MyStocks validated forward evidence |
| Validated forward MyStocks evidence | MyStocks / miniQMT receive | Pending | Authoritative-ready target requires MyStocks dry-run evidence for validated forward identity `payload_hash=268b62bb0fb0891833ef1998d4993d6531cc6a9d84aaecb911da0cd559d2357e`, not the completed raw/candidate identity | MyStocks generates validated forward `mystocks_dry_run` evidence and miniQMT validates, previews, and applies it | Raw/candidate acceptance does not cover validated forward |
| Manual promote to `validated` | miniQMT operator / owner | Pending after validated forward MyStocks evidence | Required evidence slots for validated state are accepted | Owner/operator promotes the dataset to `validated` through miniQMT's promotion path | `validated` does not imply `authoritative-ready` or source cutover |
| Authoritative-ready promotion | miniQMT operator / owner | Manual gate only | Dataset is `validated`, rollback/fallback metadata is available, and owner approval exists | Owner/operator explicitly promotes with rollback/fallback metadata available | No automatic promotion, source cutover, or ClickHouse writes |
| MyStocks ledger backfill | MyStocks operator | Optional audit backfill | PostgreSQL DSN and operator decision are available | `market_dataset_evidence_runs` receives an operator-supplied MyStocks consumer audit snapshot with `passed` / `passed` / `applied` statuses | Ledger backfill is not miniQMT business-state truth and does not supersede miniQMT records |

## Hard Rules

- Do not reopen MyStocks functional work for the completed raw/candidate `mystocks_dry_run` slot unless a new upstream contract change is opened.
- Do not merge Quantix regression and validated forward MyStocks evidence into one task; they are different gate dimensions.
- Do not use closeout or operator snapshot files as business state sources.
- Keep any MyStocks ledger backfill as an operator-supplied consumer audit snapshot, not a miniQMT business-state source.
- Do not infer authoritative-ready, source cutover, or Quantix ClickHouse writes from MyStocks evidence apply.

## Next Minimal Action

The next MyStocks-owned action is:

```text
Generate validated forward mystocks_dry_run evidence for:
dataset_version = kline_daily_20260518_v1
lineage_id = lin_kline_daily_20260518_v1
payload_hash = 268b62bb0fb0891833ef1998d4993d6531cc6a9d84aaecb911da0cd559d2357e
target miniQMT receive path = DOCS/xtdata-api/evidence/2026-05-19-kline_daily_20260518_v1-mystocks-dry-run-forward.evidence.json
```

Do not reuse `docs/reports/evidence/miniqmt/2026-05-18-kline_daily_20260518_v1-mystocks-dry-run.evidence.json`; it is bound to the raw/candidate identity.

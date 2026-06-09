# miniQMT Controlled Evidence Line Summary and Next Steps

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-19
Last updated: 2026-05-20
Status: Updated for review

> Boundary note: this document is a review summary for the MyStocks controlled-evidence line. It records completed facts and the next work plan only. It does not replace the closeout report, the external follow-up tracker, or the operator-supplied audit snapshot as the current business-state source.

## 1. What Was Completed

| Area | Result | Evidence / reference |
|---|---|---|
| Boundary alignment | MyStocks was kept in the consumer role only. It generates evidence and local audit records, while miniQMT owns validator, preview, apply, and registry promotion steps. | `src/adapters/miniqmt_market_data.py`, `docs/reports/evidence/miniqmt/README.md` |
| Controlled evidence generation | The controlled-evidence service now produces real dry-run evidence from an immutable miniQMT release identity and emits the raw report hash, row count, and field-mapping metadata needed for validator-compatible handoff. | `src/adapters/miniqmt_market_data.py` |
| Consumer audit ledger | The consumer audit helpers were split into `src/adapters/miniqmt_market_data_ledger.py` so the release client/evidence facade stays under the production Python file-size guardrail. | `src/adapters/miniqmt_market_data_ledger.py` |
| CLI handoff | `scripts/market_data/run_miniqmt_controlled_evidence.py` now accepts explicit operator inputs, including `--dataset-version`, `--bundle-path` / `--manifest-url` / `--manifest-path`, `--output-dir`, `--postgres-dsn`, and `--output-suffix`. | `scripts/market_data/run_miniqmt_controlled_evidence.py` |
| Raw / candidate acceptance | MyStocks raw/candidate `mystocks_dry_run` evidence was generated and accepted by miniQMT. The accepted identity is bound to `payload_hash=61eedd9cd029f6c0a3324b3e66be0d9b83402279cbd0aed75885459822ec13d1`. | `docs/reports/evidence/miniqmt/2026-05-18-mystocks-dry-run-closeout.md` |
| Validated-forward handoff | A separate validated-forward `mystocks_dry_run` evidence artifact was generated locally using the forward-suffix path, then accepted by miniQMT validator / preview / apply. It is bound to `payload_hash=268b62bb0fb0891833ef1998d4993d6531cc6a9d84aaecb911da0cd559d2357e`. | `docs/reports/evidence/miniqmt/2026-05-19-kline_daily_20260518_v1-mystocks-dry-run-forward.evidence.json` |
| Manual maturity promotion | miniQMT owner/operator manually promoted the dataset to `validated`, then to `authoritative-ready` on 2026-05-20 Beijing time. | `docs/reports/evidence/miniqmt/2026-05-18-external-followups.md` |
| Documentation closure | The closeout report, external follow-up tracker, README, review note, and OpenSpec tasks were updated so the completed raw/candidate line and the validated-forward follow-up are clearly separated. | `docs/reports/evidence/miniqmt/README.md`, `docs/reports/evidence/miniqmt/2026-05-18-external-followups.md`, `openspec/changes/add-miniqmt-market-data-controlled-evidence-consumer/tasks.md`, `openspec/changes/add-miniqmt-market-data-controlled-evidence-consumer/review.md` |
| Verification | Focused unit tests, Ruff, and OpenSpec strict validation passed for the controlled-evidence line. | `pytest tests/unit/adapters/test_miniqmt_market_data.py -q --no-cov`, `ruff check ...`, `openspec validate add-miniqmt-market-data-controlled-evidence-consumer --strict` |

### Recent commits on this line

- `0c9b383eb` - Add validated-forward evidence output suffix
- `84324ee52` - Add CLI forward suffix coverage
- `7996d8848` - Record validated-forward MyStocks evidence handoff

## 2. Current State

- The raw/candidate `mystocks_dry_run` slot is complete and closed on the MyStocks side.
- The validated-forward `mystocks_dry_run` evidence file was generated locally and accepted by miniQMT validator / preview / apply.
- miniQMT manual promote to `validated` is complete.
- miniQMT manual promote to `authoritative-ready` is complete as of 2026-05-20 Beijing time.
- The operator-supplied audit snapshot remains an audit artifact only. It is not the source of truth for miniQMT promotion state.
- Quantix validated-forward `quantix_regression` is a separate track and is already complete on the miniQMT side.
- Final `authoritative` approval remains a manual owner/operator gate. MyStocks evidence apply does not imply source cutover or ClickHouse writes.

## 3. Next Work Plan

| Priority | Next step | Owner | Outcome expected |
|---|---|---|---|
| 1 | Preserve the validated-forward acceptance and `authoritative-ready` promotion as completed external facts, not MyStocks business-state truth. | MyStocks / miniQMT receive path | The MyStocks audit chain remains aligned without becoming miniQMT registry truth. |
| 2 | Keep validated-forward identity tracking separate from raw/candidate `mystocks_dry_run`. | Both sides | No state drift and no mixing of closed raw/candidate facts with the forward path. |
| 3 | If needed, record a MyStocks consumer audit snapshot in PostgreSQL via the existing ledger path. | MyStocks operator | An audit backfill is available for later inspection, but it does not replace miniQMT truth. |
| 4 | Prepare final `authoritative` owner/operator approval and rollback / fallback readiness outside MyStocks implementation. | miniQMT operator / owner | Final source authority is granted only through an explicit miniQMT owner/operator gate. |
| 5 | Do not infer source cutover, Quantix ClickHouse writes, or production application from MyStocks evidence apply. | Both sides | Evidence acceptance remains distinct from operational cutover. |

## 4. Hard Rules to Keep

- Closeout and review artifacts record completed facts only. They are not business-state sources.
- Validated-forward identity must stay separate from the completed raw/candidate `mystocks_dry_run` line.
- `authoritative-ready` was a manual miniQMT gate and is now complete; final `authoritative` approval remains a manual owner/operator gate.
- MyStocks apply success must not be treated as final `authoritative` approval, source cutover, or ClickHouse write approval.

## 5. Key Artifact Index

| Artifact | Path | Role |
|---|---|---|
| Closeout report | `docs/reports/evidence/miniqmt/2026-05-18-mystocks-dry-run-closeout.md` | Final raw/candidate completion summary |
| External follow-up tracker | `docs/reports/evidence/miniqmt/2026-05-18-external-followups.md` | Tracks validated forward, manual promote, authoritative-ready, and optional ledger backfill |
| Raw/candidate evidence | `docs/reports/evidence/miniqmt/2026-05-18-kline_daily_20260518_v1-mystocks-dry-run.evidence.json` | Accepted MyStocks raw/candidate evidence |
| Validated-forward evidence | `docs/reports/evidence/miniqmt/2026-05-19-kline_daily_20260518_v1-mystocks-dry-run-forward.evidence.json` | Generated MyStocks validated-forward evidence accepted by miniQMT validator / preview / apply |
| Operator snapshot | `docs/reports/evidence/miniqmt/operator-supplied-miniqmt-acceptance-status.json` | Audit snapshot only; not business-state truth |

## 6. Review Checklist

- Confirm the summary correctly distinguishes the closed raw/candidate line from the validated-forward follow-up.
- Confirm the next-step plan now treats miniQMT validator / preview / apply and `authoritative-ready` as completed external gates, with final `authoritative` approval still pending.
- Confirm the hard rules still match the current boundary contract.
- Confirm the summary should remain a review document only, not an operational source of truth.

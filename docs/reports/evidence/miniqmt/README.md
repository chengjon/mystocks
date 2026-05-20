# miniQMT Controlled Evidence Handoff

> **导航说明**:
> 本文件是导航页或索引页，不是当前仓库共享规则或实现状态的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及具体执行入口，再按职责分别参考根目录 `AGENTS.md` 与根目录 `CLAUDE.md`。

This directory stores MyStocks-generated controlled evidence artifacts for miniQMT Market Data Platform promotion handoff.

Boundary:

- MyStocks generates `mystocks_dry_run` evidence from an immutable miniQMT release dataset and records a local consumer audit ledger row when `--postgres-dsn` is provided.
- miniQMT remains responsible for validating, previewing, applying, and registry-storing promotion evidence.
- MyStocks `miniqmt_validation_status`, `miniqmt_preview_status`, and `miniqmt_apply_status` values are operator-supplied audit updates. They are not automatic maturity promotion.

Acceptance state:

- miniQMT review accepts this MyStocks-side slice as boundary-correct, evidence-auditable, and aligned with the upstream M1 controlled evidence contract.
- The generated fixture evidence is a real dry-run artifact, not a template placeholder: it uses explicit dataset identity, reports real row counts, preserves `writes_performed=false`, and includes the raw report hash in `hash_or_size`.
- The evidence also carries the miniQMT review-aligned audit fields `artifact_sha256_verified=true`, `placeholder_count=0`, `field_mapping_version=miniqmt.kline_daily.v1`, plus artifact and raw-report SHA-256 summaries.
- MyStocks can now consume miniQMT-provided published dataset handoff files directly with `--manifest-path` and `--artifact-path`, including Parquet artifacts.
- The current generated evidence uses the miniQMT-confirmed published identity `payload_hash=61eedd9cd029f6c0a3324b3e66be0d9b83402279cbd0aed75885459822ec13d1`, `rows_hash=0efbcdd407ff0461c8d3f06a4dc6ac315c6b6ec177f783705ce8f57c233c1152`, `quality_status=raw`, and `maturity=candidate`.
- miniQMT committed acceptance as `05c5788` and the receive-attempt record now shows `local validator executed: yes`, `server preview executed: yes`, and `server apply executed: yes` for the raw/candidate identity.
- The accepted evidence is for the raw/candidate identity only.
- MyStocks has now generated a separate validated-forward `mystocks_dry_run` evidence artifact for the `268b...` identity using the forward-suffix handoff path, and miniQMT validator / preview / apply have now passed for that artifact.
- The `operator-supplied-miniqmt-acceptance-status.json` file is an operator-supplied audit snapshot, not proof of a PostgreSQL write and not a miniQMT business-state source.
- The `mystocks_dry_run` line is completed; there is no further MyStocks functional work on that slot unless a new upstream contract change is opened.
- Remaining work is external follow-up: optional MyStocks consumer-audit ledger backfill, plus miniQMT owner/operator `authoritative` approval / rollback readiness. The manual promote to `authoritative-ready` has already been completed by miniQMT.
- Validated forward identity tracking is separate from Quantix regression tracking.

Hard rules:

- Closeout report and operator snapshot record completed facts only; they are not business state sources. PostgreSQL ledger backfill, if performed, remains MyStocks consumer audit and does not replace miniQMT promotion-state truth.
- Validated forward identity remains distinct from the raw/candidate slot and must not be folded into `mystocks_dry_run`.
- Authoritative-ready was an explicit miniQMT manual gate and has now been completed. MyStocks apply success was not a default promotion signal and still does not imply final `authoritative` status.

Artifact index:

| Artifact | Path | Role |
|---|---|---|
| Closeout report | `2026-05-18-mystocks-dry-run-closeout.md` | Single entry point for final status, hashes, miniQMT commit, and external follow-up |
| External follow-up tracker | `2026-05-18-external-followups.md` | Tracks completed Quantix / validated-forward evidence, remaining miniQMT operator gates, and optional ledger backfill outside the completed MyStocks slot |
| Evidence JSON | `2026-05-18-kline_daily_20260518_v1-mystocks-dry-run.evidence.json` | Generated MyStocks `mystocks_dry_run` evidence accepted by miniQMT |
| Validated-forward evidence JSON | `2026-05-19-kline_daily_20260518_v1-mystocks-dry-run-forward.evidence.json` | Generated MyStocks validated-forward `mystocks_dry_run` evidence for `payload_hash=268b62bb0fb0891833ef1998d4993d6531cc6a9d84aaecb911da0cd559d2357e`; miniQMT validator / preview / apply passed |
| Raw report | `logs/mystocks_dry_run_kline_daily_20260518_v1.json` | Redacted dry-run report referenced by evidence `raw_source_file` |
| Operator status snapshot | `operator-supplied-miniqmt-acceptance-status.json` | Operator-supplied miniQMT validation/preview/apply result; not proof of PostgreSQL write and not miniQMT business-state truth |

Review entry point:

- Start with `2026-05-18-mystocks-dry-run-closeout.md`; it contains the scope, change inventory, hard rules, miniQMT acceptance, current state, 2026-05-19 verification refresh, and reviewer checklist.
- Use OpenSpec `tasks.md` items 7.9 and 7.10 to confirm the refreshed verification and review handoff were recorded.
- Do not treat this README, the closeout report, or the operator snapshot as a business-state source.

Downstream live chain:

1. MyStocks evidence JSON enters the miniQMT `mystocks_dry_run` evidence slot.
2. miniQMT runs the local validator against the received evidence.
3. miniQMT runs server preview on the same evidence payload.
4. miniQMT applies the promotion evidence after preview clears.
5. Promotion gaps are reduced once the `mystocks_dry_run` slot is no longer a blocker.
6. Quantix validated forward `quantix_regression` evidence is accepted by miniQMT; MyStocks validated forward evidence is also accepted after its own validator / preview / apply pass.
7. Manual authoritative-ready promotion has been performed by miniQMT owner/operator; final `authoritative` still requires explicit approval and rollback/fallback readiness.

Operator sequence:

1. Run `scripts/market_data/run_miniqmt_controlled_evidence.py` with explicit `--dataset-version` and either `--bundle-path` or `--manifest-url`.
2. Inspect the generated raw report and `*.evidence.json` file.
3. Copy or submit the evidence JSON to miniQMT's expected `DOCS/**/evidence/*.evidence.json` location.
4. Run miniQMT evidence validator.
5. Run miniQMT promotion evidence preview.
6. Apply evidence to miniQMT registry only after preview passes.
7. Feed the miniQMT validation/preview/apply result back into MyStocks ledger as operator-supplied status when a ledger DSN is used, or record it in the local MyStocks audit status artifact when no DSN is available.

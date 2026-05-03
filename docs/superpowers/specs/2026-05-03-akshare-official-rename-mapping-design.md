# AkShare Official Rename Mapping Design

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

## Context

`expand-akshare-data-sources` has already landed a wrapper-first governance chain for AkShare market expansion:

- `scripts/dev/quality_gate/collect_akshare_market_function_availability.py`
- `scripts/dev/quality_gate/validate_akshare_market_repo_truth.py`
- `scripts/dev/quality_gate/run_akshare_market_gates.py`

That chain currently emits three reports:

- availability
- repo-truth
- summary

It also keeps `help_candidates` and `summary.help_candidate_functions` strictly advisory. The current approved repo boundary is still "MyStocks only integrates locally present AkShare capabilities and does not borrow replacement implementations from `akquant` or third-party sources."

Local verification on `2026-05-03` shows that `akshare` is now `1.18.60`, and several section 6 targets in `expand-akshare-data-sources` have moved to official same-family renamed functions:

- `stock_news_main_em` is no longer present; `stock_news_main_cx` exists
- `stock_dt_pool_em` is no longer present; `stock_zt_pool_dtgc_em` exists
- `stock_strong_pool_em` is no longer present; `stock_zt_pool_strong_em` exists
- `stock_new_em` is no longer present; `stock_zt_pool_sub_new_em` exists
- `stock_weak_pool_em` has no accepted direct replacement in local `akshare`

This design updates the change boundary from "same-name only" to "approved official rename within the same family," while preserving the existing governance, audit, and wrapper-first delivery model.

## Goals

- Align `expand-akshare-data-sources` with the real function set exposed by local `akshare 1.18.60`
- Accept a narrow, explicit set of official rename mappings for section 6 targets
- Keep route semantics, task numbering, and business target naming stable where possible
- Upgrade the gate logic from `same-name only` to `canonical target + approved mapping`
- Retire `stock_weak_pool_em` as an upstream-removed target instead of leaving it as a permanent unresolved gap

## Non-Goals

- Do not accept third-party substitutes, cross-repo borrowed implementations, or self-invented equivalence
- Do not map `stock_dt_pool_em` to `stock_zt_pool_em`
- Do not map `stock_new_em` to `stock_zh_a_new_em`, because it models A-share new listings rather than the "次新股池" target in section 6.9
- Do not use `help_candidates` as automatic implementation approval
- Do not expand scope to unrelated pool functions such as `stock_zt_pool_previous_em` or `stock_zt_pool_zbgc_em`
- Do not close caching, batching, or broad test tasks unless those items are actually implemented and verified

## Section 1. Boundary And Target

This batch first changes the proposal boundary, not the runtime behavior. The change moves from:

- same-name only

to:

- approved official rename within the same family

The only accepted formal mappings are:

- `stock_news_main_em -> stock_news_main_cx`
- `stock_dt_pool_em -> stock_zt_pool_dtgc_em`
- `stock_strong_pool_em -> stock_zt_pool_strong_em`
- `stock_new_em -> stock_zt_pool_sub_new_em`

This accepted set already exists in advisory form inside `PREFERRED_HELP_CANDIDATES` in `collect_akshare_market_function_availability.py`. The proposal change here is not to invent a new mapping set from scratch, but to promote a subset of those advisory candidates into approved runtime mappings.

The following substitutions remain explicitly rejected:

- `stock_dt_pool_em -> stock_zt_pool_em`
- `stock_new_em -> stock_zh_a_new_em`
- any third-party source, provider drift without approval, cross-repo borrowing, or self-assembled replacement

### 1.1 Decision Record For `stock_news_main_cx`

Earlier OpenSpec material explicitly rejected `stock_news_main_em -> stock_news_main_cx` for two reasons:

- the change crossed provider family from `em` to `cx`
- under the old `same-name only` boundary, provider drift was treated as an automatic reject

That rejection is being reversed for this design because of three new facts:

1. local `akshare 1.18.60` no longer exposes `stock_news_main_em`, while `stock_news_main_cx` is the only upstream official function in the local package that serves the "财经内容精选" content family
2. the user explicitly approved approach `B`, which changes the proposal boundary from `same-name only` to `approved official rename within the same family`
3. task `6.3` is named "财经内容精选", not "个股新闻", so the target semantics can be fulfilled by a provider-shifted curated content feed if that shift is made explicit in the route, payload metadata, repo-truth, and risk model

This reversal does not mean `stock_news_main_cx` is treated as semantically identical to an `em` endpoint. It means MyStocks accepts it as the only approved upstream implementation of the `6.3` business target, under a stricter contract:

- canonical route moves to `/stock/news-main/cx`
- compatibility alias remains `/stock/news-main/em`
- payload metadata must disclose the `cx` provider and upstream function name
- schema and data-quality rules are defined separately from the `zt_pool` family and cannot be inferred from older `stock_news_em` expectations

`stock_weak_pool_em` is treated as an upstream-removed capability:

- it leaves the current implementation target set
- it remains documented for history and audit
- it no longer stays open as a normal pending implementation item

All later adapter, route, registry, test, and gate work in this change must use these four accepted mappings plus one retired item.

## Section 2. Change Surface And Delivery Order

The work is split into two layers.

### 2.1 Governance And Proposal Layer First

Files in scope:

- `openspec/changes/expand-akshare-data-sources/proposal.md`
- `openspec/changes/expand-akshare-data-sources/design.md`
- `openspec/changes/expand-akshare-data-sources/tasks.md`
- `docs/api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md`
- `scripts/dev/quality_gate/collect_akshare_market_function_availability.py`
- `scripts/dev/quality_gate/validate_akshare_market_repo_truth.py`
- `scripts/dev/quality_gate/run_akshare_market_gates.py`
- `tests/unit/scripts/test_collect_akshare_market_function_availability.py`
- `tests/unit/scripts/test_validate_akshare_market_repo_truth.py`
- `tests/unit/scripts/test_run_akshare_market_gates.py`
- `tests/unit/scripts/test_frontend_testing_akshare_runtime_gate.py`

This layer only changes the meaning of truth and gates:

- old task names stay as canonical targets for traceability
- gates stop using raw same-name presence as the only criterion
- `stock_weak_pool_em` moves to retired status
- frontend runtime / CI wiring assertions stay in scope as wrapper-chain verification, but they are not the canonical gate-logic tests

### 2.2 Runtime Integration Layer Second

Files in scope:

- `src/adapters/akshare/market_adapter/stock_sentiment.py`
- `web/backend/app/api/akshare_market/sentiment_monitor.py`
- `config/data_sources_registry.yaml`
- `tests/unit/adapters/test_akshare_stock_sentiment_incremental.py`
- `tests/backend/test_akshare_market_additional_routes.py`
- `tests/api/file_tests/test_akshare_market_api.py`

This layer keeps user-facing business semantics stable while switching internal upstream calls to the accepted renamed functions.

### 2.3 Delivery Order

Recommended execution order:

1. Update OpenSpec, repo-truth, and gate rules
2. Implement `stock_dt_pool_em`
3. Implement `stock_strong_pool_em`
4. Implement `stock_new_em`
5. Implement `stock_news_main_em`
6. Retire `stock_weak_pool_em`
7. Then close `6.10 / 6.11 / 6.12`
8. Then reassess `7.2 / 7.4 / 7.5`
9. Finally move into `8.x`

This keeps the `zt_pool` family together before handling the only provider-shifted mapping, `stock_news_main_cx`.

## Section 3. Gate Rules And Repo-Truth Semantics

The existing gate model answers only "does local `akshare` expose the same-named function?" That is no longer sufficient.

### 3.1 Availability Output Model

Each tracked target should resolve using the following semantics:

- `target_name`
- `target_available`
- `resolved_function`
- `resolution_status`
- `mapping_policy`

The allowed `resolution_status` values are:

- `native`
- `mapped`
- `missing`
- `retired`

Meaning:

- `native`: original function exists
- `mapped`: original function does not exist, but an approved upstream mapping exists
- `missing`: neither original nor approved mapped function exists
- `retired`: target was removed from the active implementation set

### 3.2 Gate Manifest Model

Each manifest item should carry:

- `task_id`
- `canonical_target`
- `accepted_upstream_functions`
- `registry_key`
- `adapter_method`
- `route_fragment`
- focused test tokens

Optional:

- `retired: true`

For example, `stock_dt_pool_em` remains the canonical target, while `stock_zt_pool_dtgc_em` becomes the accepted upstream function.

For the current proposal, the accepted mapping source is the existing advisory table in `PREFERRED_HELP_CANDIDATES`. The gate change upgrades those entries from "show as a hint" to "pass as approved mapping" only for the four explicitly accepted targets in this design.

### 3.3 Repo-Truth Status Semantics

`docs/api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md` should use four explicit status families:

- `已实现（原名）`
- `已实现（官方改名映射）`
- `未实现`
- `已下线/上游移除`

Expected outcomes for this batch:

- `stock_news_main_em`: `已实现（官方改名映射：stock_news_main_cx）`
- `stock_dt_pool_em`: `已实现（官方改名映射：stock_zt_pool_dtgc_em）`
- `stock_strong_pool_em`: `已实现（官方改名映射：stock_zt_pool_strong_em）`
- `stock_new_em`: `已实现（官方改名映射：stock_zt_pool_sub_new_em）`
- `stock_weak_pool_em`: `已下线/上游移除`

### 3.4 Gate Pass Rules

- `native` or `mapped`
  - OpenSpec task checked
  - registry, adapter, route, and focused tests must exist
- `missing`
  - OpenSpec task unchecked
  - runtime artifacts must not exist
- `retired`
  - no longer treated as a pending implementation target
  - runtime artifacts are not required
  - OpenSpec and repo-truth must document retirement explicitly

`stock_weak_pool_em` uses retirement validation, not runtime validation.

## Section 4. Runtime API And Adapter Design

### 4.1 Adapter Method Naming

Adapter methods keep business target naming stable:

- `get_stock_news_main_em()`
- `get_stock_dt_pool_em()`
- `get_stock_strong_pool_em()`
- `get_stock_new_em()`

But their implementations call the real upstream functions:

- `get_stock_news_main_em()` -> `ak.stock_news_main_cx()`
- `get_stock_dt_pool_em()` -> `ak.stock_zt_pool_dtgc_em()`
- `get_stock_strong_pool_em()` -> `ak.stock_zt_pool_strong_em()`
- `get_stock_new_em()` -> `ak.stock_zt_pool_sub_new_em()`

### 4.2 Response Stability With Mapping Metadata

Route payloads should keep business-facing fields stable. They should not expose upstream rename churn directly as a breaking response change.

Additional audit metadata should be included:

- `canonical_target`
- `upstream_function`
- `mapping_policy`
- `provider`

For example:

- `canonical_target: "stock_dt_pool_em"`
- `upstream_function: "stock_zt_pool_dtgc_em"`
- `mapping_policy: "approved_official_rename"`

### 4.2.1 Mapping-Specific Schema Contract

The four accepted mappings do not share a single schema story. The runtime contract must be defined per target.

| Canonical target | Upstream function | Observed upstream columns / signature | Contract consequence |
|---|---|---|---|
| `stock_dt_pool_em` | `stock_zt_pool_dtgc_em(date)` | 16 columns including `序号/代码/名称/涨跌幅/最新价/成交额/流通市值/总市值/动态市盈率/换手率/封单资金/最后封板时间/板上成交额/连续跌停/开板次数/所属行业` | Safe to normalize as a `zt_pool`-family market board with a dedicated `dt_pool` field mapping |
| `stock_strong_pool_em` | `stock_zt_pool_strong_em(date)` | 16 columns including `序号/代码/名称/涨跌幅/最新价/涨停价/成交额/流通市值/总市值/换手率/涨速/是否新高/量比/涨停统计/入选理由/所属行业` | Safe to normalize as a `zt_pool`-family strong-pool board, but it needs a reason/high-water-mark contract |
| `stock_new_em` | `stock_zt_pool_sub_new_em(date)` | 16 columns including `序号/代码/名称/涨跌幅/最新价/涨停价/成交额/流通市值/总市值/转手率/开板几日/开板日期/上市日期/是否新高/涨停统计/所属行业` | Safe to normalize as a `sub_new` board, but `转手率` and listing/open-board dates require explicit route-level field naming |
| `stock_news_main_em` | `stock_news_main_cx()` | signature `()` and 3 columns `tag/summary/url` | Not schema-equivalent to legacy stock-news expectations. It needs its own curated-content contract and must not reuse `stock_news_em`-style symbol/news columns |

The design assumption is therefore:

- `dt/strong/sub_new` are same-family board datasets that can share a normalization strategy
- `news_main_cx` is a separate curated-content contract and must be modeled independently

### 4.2.2 `news_main` Route Contract

`stock_news_main_cx()` is zero-argument and currently returns curated content rows with:

- `tag`
- `summary`
- `url`

Therefore the `6.3` route contract must not pretend to be a symbol-scoped stock-news feed. The runtime design for `news_main` is:

- no `symbol` query parameter
- response data rows normalized from `tag/summary/url`
- provider metadata set to `cx`
- canonical target still recorded as `stock_news_main_em`
- any future enrichment such as publish time or content classification must be treated as optional, not guaranteed by the upstream function

### 4.3 Pool Family Normalization

The `zt / dt / strong / sub_new` family should normalize output columns according to business target semantics, not leak raw upstream naming differences directly into route responses.

### 4.3.1 Normalized Pool Output Columns

The shared normalized column base for board-like responses should be:

| Normalized field | `dt_pool` source | `strong_pool` source | `sub_new` source |
|---|---|---|---|
| `sequence_no` | `序号` | `序号` | `序号` |
| `symbol` | `代码` | `代码` | `代码` |
| `stock_name` | `名称` | `名称` | `名称` |
| `change_percent` | `涨跌幅` | `涨跌幅` | `涨跌幅` |
| `latest_price` | `最新价` | `最新价` | `最新价` |
| `turnover_amount` | `成交额` | `成交额` | `成交额` |
| `circulating_market_cap` | `流通市值` | `流通市值` | `流通市值` |
| `total_market_cap` | `总市值` | `总市值` | `总市值` |
| `industry` | `所属行业` | `所属行业` | `所属行业` |
| `query_date` | request date | request date | request date |
| `query_timestamp` | generated locally | generated locally | generated locally |

Pool-specific normalized fields:

| Canonical target | Additional normalized fields |
|---|---|
| `stock_dt_pool_em` | `pe_ratio`, `turnover_rate`, `sealed_order_fund`, `last_limit_time`, `board_turnover_amount`, `consecutive_limit_down_count`, `reopen_count` |
| `stock_strong_pool_em` | `limit_up_price`, `turnover_rate`, `change_speed`, `is_new_high`, `volume_ratio`, `limit_up_stats`, `selection_reason` |
| `stock_new_em` | `limit_up_price`, `turnover_rate` mapped from upstream `转手率`, `open_board_days`, `open_board_date`, `listing_date`, `is_new_high`, `limit_up_stats` |

Empty-data days are valid outcomes for all three routes. The route contract must preserve an empty dataset plus metadata rather than converting emptiness into a schema failure.

### 4.4 No Runtime Implementation For `stock_weak_pool_em`

No adapter method, route, registry entry, or focused runtime test should be added for `stock_weak_pool_em`. Its only required handling is explicit retirement in specs, repo-truth, and gate semantics.

### 4.5 News Main Provider Decision

`stock_news_main_cx` is the only mapping that changes provider family.

Approved route policy:

- canonical route: `/stock/news-main/cx`
- compatibility alias: `/stock/news-main/em`

The response must explicitly disclose:

- `canonical_target: "stock_news_main_em"`
- `upstream_function: "stock_news_main_cx"`
- `provider: "cx"`
- `mapping_policy: "approved_official_rename"`

This keeps old callers working while making the new provider truth explicit.

### 4.5.1 Provider Drift Quality Gates For `news_main_cx`

Route compatibility alone is not enough for `news_main_cx`. The design must also require a content-quality gate because this mapping changes provider family from `em`-style expectations to a `cx` content feed.

Minimum quality checks for `news_main`:

- required row fields: `tag`, `summary`, `url`
- non-empty `summary` rate must remain acceptable for returned rows
- `url` values must remain present and routable
- no consumer may assume the presence of `symbol`, `title`, or `publish_time`

User-visible behavior may change:

- content becomes curated finance highlights instead of a symbol-scoped stock-news list
- provider label changes to `cx`
- route documentation and any frontend consumer must be updated if they previously assumed `em` semantics

If future runtime validation shows that `news_main_cx` cannot satisfy the curated-content target consistently, this mapping must be reconsidered as a separate proposal adjustment rather than silently treated as complete.

## Section 5. Registry And Route Compatibility Policy

### 5.1 Registry Keys Stay On Business Target Names

Registry keys should remain:

- `akshare_stock_news_main_em`
- `akshare_stock_dt_pool_em`
- `akshare_stock_strong_pool_em`
- `akshare_stock_new_em`

This avoids unnecessary churn across tasks, docs, and tests.

### 5.2 Registry Records Real Upstream Functions Explicitly

Each relevant registry entry should record:

- `canonical_target`
- `endpoint_name`

Recommended additional fields:

- `mapping_policy`
- `upstream_provider`

Example:

- `canonical_target: stock_dt_pool_em`
- `endpoint_name: akshare.stock_zt_pool_dtgc_em`

### 5.3 Route Compatibility Rules

For `dt / strong / new`, keep existing business semantic routes:

- `/stock/dt-pool/em`
- `/stock/strong-pool/em`
- `/stock/new/em`

For `news-main`, use canonical-plus-alias routing:

- canonical: `/stock/news-main/cx`
- compatibility alias: `/stock/news-main/em`

### 5.4 Compatibility Lifecycle

The `/stock/news-main/em` alias is a temporary compatibility layer, not the long-term canonical truth. Repo-truth should distinguish canonical route from compatibility alias, and alias retirement should happen in a separate later batch once callers have migrated.

### 5.5 Test Naming Policy

Test names may continue using business target names for continuity, but assertions must validate:

- mapped upstream function usage
- correct `mapping_policy`
- correct `provider`
- correct `upstream_function`

## Section 6. Verification And Rollout Rules

### 6.1 Governance Layer Verification

Required commands:

```bash
pytest tests/unit/scripts/test_collect_akshare_market_function_availability.py -q --no-cov
pytest tests/unit/scripts/test_validate_akshare_market_repo_truth.py -q --no-cov
pytest tests/unit/scripts/test_run_akshare_market_gates.py -q --no-cov
pytest tests/unit/scripts/test_frontend_testing_akshare_runtime_gate.py -q --no-cov
python scripts/dev/quality_gate/run_akshare_market_gates.py --output-dir /tmp/akshare-market-gates
openspec validate expand-akshare-data-sources --strict
```

Success criteria:

- `summary.pass = true`
- `repo_truth_violation_count = 0`
- OpenSpec strict validation passes

The `openspec validate expand-akshare-data-sources --strict` command was re-verified successfully in the local project environment on `2026-05-04`.

### 6.2 Runtime Micro-Batch Verification

For each integrated interface:

```bash
pytest tests/unit/adapters/test_akshare_stock_sentiment_incremental.py -q --no-cov
pytest tests/backend/test_akshare_market_additional_routes.py -q --no-cov
pytest tests/api/file_tests/test_akshare_market_api.py -q --no-cov
python -m py_compile src/adapters/akshare/market_adapter/stock_sentiment.py web/backend/app/api/akshare_market/sentiment_monitor.py
python scripts/dev/quality_gate/run_akshare_market_gates.py --output-dir /tmp/akshare-market-gates
openspec validate expand-akshare-data-sources --strict
```

Prefer narrower targeted tests before full group runs when only a single route or adapter method changes.

### 6.3 Task Closure Rules

- `6.3 / 6.5 / 6.6 / 6.9` are checked only after adapter, route, registry, focused tests, repo-truth, and gates are aligned
- `stock_weak_pool_em` is retired rather than kept as a normal open checkbox
- `6.10 / 6.11 / 6.12` close only after the four mapped interfaces plus retirement handling are complete
- `7.2` closes only after registry quality rules reflect mapping semantics
- `7.4 / 7.5 / 8.x` must not be checked unless truly implemented and verified

Task `6.7` in `tasks.md` should not remain as a normal unchecked implementation checkbox. The update plan is:

- remove `6.7` from the active executable checkbox set
- replace it with an explicit retirement note tied to `stock_weak_pool_em`
- record that the target is retired because local `akshare 1.18.60` exposes no accepted direct mapping

### 6.4 Commit Strategy

Continue using:

- one governance batch per commit, or one interface per commit
- path-level staging
- path-level commit review with `git show`

In the current dirty worktree, `gitnexus detect_changes(scope="staged")` is still required before commit but cannot be used as the precise micro-batch verdict if unrelated staged files remain present.

## Section 7. Documentation And OpenSpec Editing Plan

### 7.1 Keep The Existing Active Change

Do not open a second change. Update the existing active change:

- `openspec/changes/expand-akshare-data-sources/proposal.md`
- `openspec/changes/expand-akshare-data-sources/design.md`
- `openspec/changes/expand-akshare-data-sources/tasks.md`

### 7.2 OpenSpec Must Explicitly Record

- the four accepted formal mappings
- the explicit rejections
- retirement of `stock_weak_pool_em`
- `help_candidates` remain advisory only
- wrapper-first gate chain remains canonical

### 7.3 Repo-Truth Document Role

`docs/api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md` becomes the canonical mapping ledger for:

- canonical target
- canonical route
- upstream function
- current implementation state

### 7.4 Guide Document Role

The following remain explanatory and operational, not canonical truth:

- `docs/guides/akshare/AKSHARE_MARKET_EXTENSION_GUIDE.md`
- `docs/guides/akshare/AKSHARE_MARKET_TROUBLESHOOTING.md`
- `docs/guides/akshare/AKSHARE_MARKET_MAINTENANCE.md`
- `docs/reports/tasks/expand-akshare-data-sources-handoff-2026-05-03.md`

They should explain:

- why `stock_dt_pool_em` must map to `stock_zt_pool_dtgc_em`
- why `stock_new_em` maps to `stock_zt_pool_sub_new_em` instead of `stock_zh_a_new_em`
- why `stock_weak_pool_em` is retired
- why wrapper-first remains the default execution path

### 7.5 Design Draft Role

This file is the consolidated design draft for the mapping policy shift:

- `docs/superpowers/specs/2026-05-03-akshare-official-rename-mapping-design.md`

It is not repo-truth and not an OpenSpec delta. It exists so later implementation work can follow one approved design record instead of reconstructing decisions from chat history.

### 7.6 Documentation Update Order

1. Write this design draft
2. Update OpenSpec proposal, design, and tasks
3. Update repo-truth
4. Update gates and focused tests
5. Update guide and handoff documents as implementation results land

That update sequence must explicitly include:

- revising `tasks.md` item `6.7` from an open implementation task into a retirement record
- keeping runtime-delivery wiring assertions in sync with any gate script argument or output schema changes

## Section 8. Risks, Non-Goals, And Decision Record

### 8.1 Risks

- `stock_news_main_cx` provider drift risk
  - Mitigation: canonical `/cx` route, `/em` alias, explicit response metadata, and dedicated content-quality checks on `tag/summary/url`
- `stock_zh_a_new_em` accidental misuse risk
  - Mitigation: explicit rejection in design, gate, and repo-truth because it models A-share new listings rather than the "次新股池" target
- dirty worktree scope pollution
  - Mitigation: path-level stage, path-level commit, path-level `git show` review
- docs drifting ahead of runtime
  - Mitigation: update design and truth layers first, close runtime tasks only after verification

### 8.2 Non-Goals Reaffirmed

- no cross-repo borrowing
- no third-party replacements
- no unapproved adjacent pool expansions
- no implementation of `stock_weak_pool_em` parity by approximation
- no reclassification of `help_candidates` into automatic pass rules

### 8.3 Final Approved Decisions

- adopt approach `B`: approved official same-family rename mappings
- accept only these four mappings:
  - `stock_news_main_em -> stock_news_main_cx`
  - `stock_dt_pool_em -> stock_zt_pool_dtgc_em`
  - `stock_strong_pool_em -> stock_zt_pool_strong_em`
  - `stock_new_em -> stock_zt_pool_sub_new_em`
- retire `stock_weak_pool_em`
- upgrade gates from `same-name only` to `canonical target + approved mapping`
- use `/stock/news-main/cx` as canonical route and `/stock/news-main/em` as compatibility alias
- keep registry keys on business target names
- execute in the order `dt -> strong -> sub_new -> news_main -> weak retired`

## Next Step

After this document is reviewed, the next phase is to translate it into:

- OpenSpec proposal/design/tasks updates
- gate manifest and script updates
- runtime integration micro-batches

No implementation plan should start until this design draft is reviewed and accepted as a written artifact.

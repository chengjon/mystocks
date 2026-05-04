# AkShare Official Rename Candidate Evaluation Design

> **权威来源声明**:
> 本文件是专题设计草稿，不是仓库共享规则或当前实现真相的唯一事实来源。
> 仓库级共享规则与审批门禁以 `architecture/STANDARDS.md` 为准；当前变更真相以 `openspec/changes/expand-akshare-data-sources/`、`README.md`、`docs/FUNCTION_TREE.md` 和相关 repo-truth 文档为准。

## Context

`expand-akshare-data-sources` 的门禁基线已经在提交 `435bc8f00` (`akshare: add market repo-truth gates`) 中收口。该提交已经完成：

- wrapper-first AkShare 市场门禁链路
  - `scripts/dev/quality_gate/collect_akshare_market_function_availability.py`
  - `scripts/dev/quality_gate/validate_akshare_market_repo_truth.py`
  - `scripts/dev/quality_gate/run_akshare_market_gates.py`
- runtime / CI 汇总接线
- `README.md` 与 `docs/FUNCTION_TREE.md` 真相源补齐
- OpenSpec、AkShare 专题文档、handoff 台账与 Graphiti 同步

当前基线已经明确：

- MyStocks 只把本地已存在的 AkShare 同名函数视为已实现运行时能力
- 官方同源改名能力可以作为 `help_candidates` 暴露给人工评估
- advisory candidate 不自动升级为已实现能力
- 本仓库不自研替代函数，不跨到 `akquant` 或其他异源接口补缺

基于本地 `akshare 1.18.60` 的真实情况，当前 advisory candidate 只保留三项人工评估线索：

- `stock_dt_pool_em -> stock_zt_pool_dtgc_em`
- `stock_strong_pool_em -> stock_zt_pool_strong_em`
- `stock_new_em -> stock_zt_pool_sub_new_em`

同时确认：

- `stock_news_main_em` 本地缺失，`stock_news_main_cx` 仅作为邻近官方函数存在，不在当前保留候选集内
- `stock_weak_pool_em` 当前没有可接受候选，并已基于业务决策正式收口为 retired item

本设计稿的职责不是重写已经落地的 gate baseline，而是：

1. 记录 `435bc8f00` 已经落地的治理事实
2. 定义后续如何在不污染当前 repo-truth 的前提下评估官方改名候选

## Goals

- 记录 `435bc8f00` 已交付的 gate baseline
- 把后续候选评估与退役口径对齐到本地 `akshare 1.18.60` 的真实情况
- 将手工评估线与已退役条目统一收敛到 `Section 3.2`
- 如果未来某个候选被提升，保持 OpenSpec task 名、业务语义名、路由语义的稳定性
- 定义从 advisory candidate 升级为 approved runtime mapping 的前置条件

## Non-Goals

- 不在当前批次批准 `stock_news_main_em -> stock_news_main_cx`
- 不为已退役的 `stock_weak_pool_em` 保留任何伪 runtime 工件
- 不放宽当前 same-name gate baseline
- 不自研替代函数
- 不用异源接口补缺
- 不把 `help_candidates` 当作自动通过条件
- 不把 `stock_dt_pool_em` 映射到 `stock_zt_pool_em`
- 不把 `stock_new_em` 映射到 `stock_zh_a_new_em`，因为它描述的是更宽泛的 `新股`，不是 `次新股池`
- 不把 `stock_zt_pool_previous_em`、`stock_zt_pool_zbgc_em` 等相邻能力混进本批范围

## Section 1. Boundary And Target

本批首先改变的是“设计记录方式”，不是“当前运行时真相”。

当前真相已经是：

- same-name native 仍然有效
- `dt / strong / new` 已作为 approved mapping 落地
- `stock_weak_pool_em` 已改写为 retired item
- `stock_news_main_em` 仍只保留 advisory 线索

候选、排除项和 retired item 的唯一库存定义以 `Section 3.2 Current Candidate Inventory` 为准。

本节只补充边界性强调：

- `stock_dt_pool_em -> stock_zt_pool_em` 继续明确拒绝
- `stock_new_em -> stock_zh_a_new_em` 继续明确拒绝
- `stock_weak_pool_em` 的任何近似替代继续明确拒绝
- 任何第三方或跨仓库借用实现继续明确拒绝

### 1.1 Decision Record For `stock_news_main_cx`

`stock_news_main_cx` 在当前批次继续排除，原因如下：

1. `435bc8f00` 收口后的 repo-truth 已明确只把 `dt / strong / new` 保留为人工评估候选
2. `stock_news_main_cx` 不是同名函数
3. 它的本地签名是 `() -> DataFrame`
4. 实测返回列是 `tag / summary / url`
5. 这说明它更像 provider-drift 的内容精选接口，而不是一个可直接视为同源平移的市场池类接口

因此当前结论是：

- `stock_news_main_cx` 可以继续作为 help candidate 或邻近官方线索存在
- 它不是当前 change line 中的 approved runtime mapping
- 如果未来要提升，必须单独补一份 decision record，并单独做实现微批

### 1.2 Decision Record For `stock_weak_pool_em`

`stock_weak_pool_em` 当前已正式改写为 `retired / removed with reason`。

原因是：

1. 本地 AkShare 1.18.60 未提供 `stock_weak_pool_em` 同名函数
2. 当前未找到可接受的官方同源候选
3. 业务侧已明确决定不再承接弱势股池能力

这意味着它不再作为 open gap 保留，也不再要求任何 runtime 工件。

#### 1.2.1 Re-entry Rule

如果未来要重新引入 `stock_weak_pool_em`，应视为新的 capability re-entry，而不是恢复当前 retired 项。新的重新引入批次至少需要：

1. 本地 AkShare 恢复同名函数，或出现经单独批准的新官方候选
2. 业务侧重新确认弱势股池能力仍有需求
3. gate、repo-truth、OpenSpec 和 runtime code 一起重新闭环

## Section 2. Change Surface And Delivery Order

### 2.1 What `435bc8f00` Already Delivered

该提交已经落地的范围包括：

- gate 脚本本体
- gate 测试
- `tests/unit/scripts/test_frontend_testing_akshare_runtime_gate.py` 所代表的 runtime / CI wiring verification
- runtime / CI 汇总接线
- `README.md`
- `docs/FUNCTION_TREE.md`
- OpenSpec 与 AkShare 专题文档
- Graphiti 记忆更新

这部分不应在本设计稿里被重新表述成“待设计”或“待确认”。

### 2.2 What This Design Adds

本设计稿只新增三类内容：

1. advisory candidate 与 approved runtime mapping 的明确分层
2. `Section 3.2` 中 approved mapping 与 retired item 的统一库存
3. `Section 1.1` 和 `Section 1.2` 所述排除项 / retired item 的明文说明

### 2.3 Recommended Delivery Order For Future Promotion

历史上实际采用的实现微批顺序是：

1. 先改 OpenSpec / repo-truth / gate 口径
2. 再做 `stock_dt_pool_em`
3. 再做 `stock_strong_pool_em`
4. 再做 `stock_new_em`
5. 再重新评估 `stock_news_main_em`
6. 最后再把 `stock_weak_pool_em` 以 retired / removed with reason 收口

排序依据明确如下：

1. `dt` 排第一，因为它与现有板池类归一化管线最接近，且 `跌停股池` 语义最收敛，复用成本最低
2. `strong` 排第二，因为仍属于同一家族，但比 `dt` 多出 `入选理由`、`是否新高`、`量比` 等扩展字段，归一化复杂度略高
3. `new` 排第三，因为它引入 `转手率`、`开板日期`、`上市日期` 等次新语义字段，字段解释和前端消费差异最大

这个顺序既保持了 `zt_pool` 家族的一致性，也避免在早期批次过早处理 `news_main_cx` 的 provider drift 风险。

## Section 3. Gate Rules And Repo-Truth Semantics

### 3.1 Current Gate Truth

当前 gate 语义已经从 `435bc8f00` 的 same-name baseline 扩展为：

1. `native`：OpenSpec 目标函数在本地 AkShare 中同名存在
2. `mapped`：命中已批准的官方改名映射
3. `retired`：业务已决定不再承接，且当前没有保留 runtime 工件
4. `help_candidates` 仍只用于人工排查和评估，不自动变成 runtime approval

### 3.2 Current Candidate Inventory

| Canonical target | Current local status | Advisory candidate | Current repo decision |
| --- | --- | --- | --- |
| `stock_news_main_em` | missing | `stock_news_main_cx` | excluded from current candidate set |
| `stock_dt_pool_em` | mapped | `stock_zt_pool_dtgc_em` | approved runtime mapping |
| `stock_strong_pool_em` | mapped | `stock_zt_pool_strong_em` | approved runtime mapping |
| `stock_new_em` | mapped | `stock_zt_pool_sub_new_em` | approved runtime mapping |
| `stock_weak_pool_em` | retired | none | retired / removed with reason |

### 3.3 Relationship To `PREFERRED_HELP_CANDIDATES`

`PREFERRED_HELP_CANDIDATES` 已存在于
`collect_akshare_market_function_availability.py`。

这里必须明确：

- 它是 advisory discovery 机制
- 它是当前 gate baseline 的一部分
- 它不是 runtime approval 清单

本设计稿使用它作为“后续人工评估的输入”，而不是“当前自动通过的真相源”。

### 3.4 Future Promotion Rule

如果未来某个候选被提升，语义才会从：

- missing + advisory candidate

升级为：

- approved official rename mapping

这种升级只能在以下内容一起更新后发生：

1. OpenSpec proposal / design / tasks
2. repo-truth 文档
3. gate 语义
4. adapter / route / registry 实现
5. focused tests

在这些条件满足之前，当前 gate baseline 仍然是唯一真相。

## Section 4. Runtime API And Adapter Design For Future Promotion

本节描述的是“如果未来提升候选，运行时该怎么做”，不是“现在已经这样做了”。

### 4.1 Candidate Promotion Order

推荐的候选提升顺序：

这里的有序集合与 `Section 3.2` 中的 retained candidate subset 完全一致。

1. `stock_dt_pool_em -> stock_zt_pool_dtgc_em`
2. `stock_strong_pool_em -> stock_zt_pool_strong_em`
3. `stock_new_em -> stock_zt_pool_sub_new_em`

`stock_news_main_cx` 不在当前提升顺序内。

### 4.2 Observed Local Signatures And Payload Shapes

以下表格记录的是本地 `akshare 1.18.60` 观测结果，用于后续人工评估，不代表当前已批准映射。

| Canonical target | Observed candidate | Local signature | Observed payload shape | Current decision |
| --- | --- | --- | --- | --- |
| `stock_news_main_em` | `stock_news_main_cx` | `() -> DataFrame` | columns: `tag`, `summary`, `url` | excluded from current promotion set |
| `stock_dt_pool_em` | `stock_zt_pool_dtgc_em` | `(date: str = '20241011') -> DataFrame` | 16 columns, includes `代码`, `名称`, `涨跌幅`, `最新价`, `封单资金`, `最后封板时间`, `连续跌停`, `所属行业` | retained candidate |
| `stock_strong_pool_em` | `stock_zt_pool_strong_em` | `(date: str = '20241231') -> DataFrame` | 16 columns, includes `代码`, `名称`, `涨跌幅`, `换手率`, `是否新高`, `涨停统计`, `入选理由` | retained candidate |
| `stock_new_em` | `stock_zt_pool_sub_new_em` | `(date: str = '20241231') -> DataFrame` | 16 columns, includes `代码`, `名称`, `最新价`, `转手率`, `开板几日`, `开板日期`, `上市日期` | retained candidate |

### 4.2.1 Supporting Observations For Section 1.1

下面这些观测项是 `Section 1.1 Decision Record For stock_news_main_cx` 的技术支撑：

1. 它不是 pool 风格接口
2. 它不是 `zt_pool` 家族的同类数据表
3. 它暴露的是 curated content feed，而不是板块池快照
4. 它的 payload contract 与其他三项没有共用归一化策略

因此如果以后再评估它，至少要补：

- 独立路由契约评审
- 独立前端消费评审
- 独立 repo-truth decision

### 4.3 Normalized Pool Output Contract For Future Promotion

如果 `dt / strong / new` 将来被提升，后端应把它们归一化成稳定 contract，而不是把 AkShare 原始列直接泄漏成公共 API 契约。

建议的归一化字段如下，要求实现者按“是否必填 + 候选适用性”一起实现：

| Normalized field | Required / Optional | `dt` applicability / source | `strong` applicability / source | `new` applicability / source | Notes |
| --- | --- | --- | --- | --- | --- |
| `symbol` | Required | `代码` | `代码` | `代码` | stable primary key |
| `name` | Required | `名称` | `名称` | `名称` | stable display name |
| `change_percent` | Required | `涨跌幅` | `涨跌幅` | `涨跌幅` | numeric normalization required |
| `latest_price` | Required | `最新价` | `最新价` | `最新价` | numeric normalization required |
| `turnover_rate` | Optional | `换手率` | `换手率` | `转手率` | absent values normalize to `null` |
| `turnover_amount` | Optional | `成交额` | `成交额` | `成交额` | numeric normalization when present |
| `circulating_market_value` | Optional | `流通市值` | `流通市值` | `流通市值` | numeric normalization when present |
| `total_market_value` | Optional | `总市值` | `总市值` | `总市值` | numeric normalization when present |
| `industry` | Optional | `所属行业` | `所属行业` | `所属行业` | string or `null` |
| `selection_reason` | Optional | not provided -> `null` | `入选理由` | not provided -> `null` | never coerce to empty string |
| `board_time` | Optional | `最后封板时间` | not provided -> `null` | not provided -> `null` | string or normalized time token |
| `board_metrics` | Optional | see fixed object schema below | see fixed object schema below | see fixed object schema below | always object when present, never free-form text |
| `listed_date` | Optional | not provided -> `null` | not provided -> `null` | `上市日期` | date-like string or `null` |
| `open_board_date` | Optional | not provided -> `null` | not provided -> `null` | `开板日期` | date-like string or `null` |

`board_metrics` 不应是自由形式的 dict。建议固定为如下 optional object schema：

```json
{
  "consecutive_limit_down_count": null,
  "reopen_count": null,
  "board_turnover_amount": null,
  "limit_up_stats": null,
  "is_new_high": null,
  "volume_ratio": null,
  "change_speed": null,
  "open_board_days": null
}
```

按候选适用性填充：

- `dt`
  - `consecutive_limit_down_count <- 连续跌停`
  - `reopen_count <- 开板次数`
  - `board_turnover_amount <- 板上成交额`
- `strong`
  - `limit_up_stats <- 涨停统计`
  - `is_new_high <- 是否新高`
  - `volume_ratio <- 量比`
  - `change_speed <- 涨速`
- `new`
  - `limit_up_stats <- 涨停统计`
  - `is_new_high <- 是否新高`
  - `open_board_days <- 开板几日`

### 4.3.1 Contract Evolution Policy

该归一化 contract 采用保守演进策略：

1. 只允许 additive extension，不删除已公开字段
2. 新字段默认 `optional`
3. 前端按 feature detection 消费新增字段，不预设所有候选都完整提供
4. 若某字段语义需要破坏性调整，应通过单独 proposal / contract change 处理，而不是静默重载旧字段

### 4.3.2 Mapping-Specific Notes

- `stock_zt_pool_dtgc_em`
  - 是 `stock_dt_pool_em` 的最佳候选
  - 不能回退成 `stock_zt_pool_em`，因为本地 docstring 和 payload 都指向 `跌停股池`
- `stock_zt_pool_strong_em`
  - 与 `stock_strong_pool_em` 语义最接近
  - `入选理由` 应保留进归一化结果
- `stock_zt_pool_sub_new_em`
  - 比 `stock_zh_a_new_em` 更合理
  - `stock_zh_a_new_em` 是更宽泛的 `新股`，而 `sub_new_em` 更接近 `次新股池` 语义

### 4.4 Adapter And Route Policy For Future Promotion

如果未来提升某个候选，应遵循以下兼容规则：

1. 公共 API key 和 route 名继续沿用 canonical OpenSpec target name
2. 上游函数改名细节隐藏在 adapter / service / registry 内部
3. 不把上游 candidate 函数名直接暴露成公共 route 名

例子：

- public contract 仍可叫 `stock_dt_pool_em`
- internal upstream call 才解析到 `stock_zt_pool_dtgc_em`

### 4.5 Provider Drift Guardrail

`dt / strong / new` 这三项仍然只是 official rename candidate，不是当前已批准 alias。

将来提升前必须确认：

1. 语义对齐
2. payload 稳定
3. 归一化成本可控
4. 不与现有前端契约假设冲突

`stock_news_main_cx` 的门槛更高，因为它属于 provider-drift candidate，不是简单同家族 rename candidate。

### 4.5.1 Upstream Re-rename Contingency

如果 AkShare 后续版本再次改名，例如某个保留候选再次漂移，当前策略应是“显式失败并重新评估”，而不是静默兜底。

具体规则：

1. gate 应重新把该目标标记为 `missing` 或 `missing with advisory candidate`，CI 中断属于预期保护行为
2. `PREFERRED_HELP_CANDIDATES` 如需支持多版本候选，应升级为有序候选列表，并在 repo-truth 中记录适用的 AkShare 版本窗口
3. runtime adapter 不应对未批准的新上游名做静默 fallback；最多只允许抛出显式错误并提示 repo-truth 已失配
4. 任何再改名修复都应重新经过 candidate evaluation，而不是把新的 help candidate 自动视为兼容升级

## Section 5. Registry, Route, And Naming Rules

### 5.1 Current Truth

当前：

- 还没有任何 rename mapping 在 runtime 层被正式批准
- 不能把新的 adapter alias 当作既成 canonical reality
- gate 与 repo-truth 文档仍然是当前真相源

### 5.2 Future Promotion Rule

如果未来某个候选被提升：

1. registry key 仍使用 canonical OpenSpec target name
2. adapter method 可以在内部 dispatch 到批准后的 upstream candidate
3. route name 继续保持 canonical target 语义
4. tests 必须同时覆盖实现正确性和 repo-truth 对齐

### 5.3 Explicit Non-Rule

本设计稿当前不批准：

- `/stock/news-main/cx` 作为公共 canonical route
- 以 `stock_zt_pool_dtgc_em` 为名的公共 registry key
- 以 `stock_zt_pool_strong_em` 为名的公共 route
- 以 `stock_zt_pool_sub_new_em` 为名的公共 route

如果未来提升，这些 upstream 名仍然只应是内部实现细节。

## Section 6. Verification And Rollout Rules

### 6.1 Governance Baseline Verification

当前基线的验证命令保持：

```bash
pytest tests/unit/scripts/test_collect_akshare_market_function_availability.py -q --no-cov
pytest tests/unit/scripts/test_validate_akshare_market_repo_truth.py -q --no-cov
pytest tests/unit/scripts/test_run_akshare_market_gates.py -q --no-cov
pytest tests/unit/scripts/test_frontend_testing_akshare_runtime_gate.py -q --no-cov
python scripts/dev/quality_gate/run_akshare_market_gates.py --output-dir /tmp/akshare-market-gates
openspec validate expand-akshare-data-sources --strict
```

当前已知通过结果来自收口提交 `435bc8f00` 对应批次：

- 相关脚本 / 门禁测试 `8 passed, 4 skipped`
- `python scripts/dev/quality_gate/run_akshare_market_gates.py --output-dir /tmp/akshare-market-gates` 返回 `pass=true`
- `openspec validate expand-akshare-data-sources --strict` 通过

本轮于 `2026-05-04` 额外复核：

- `openspec validate expand-akshare-data-sources --strict` 当前仍可执行且返回 `Change 'expand-akshare-data-sources' is valid`
- `tests/unit/scripts/test_frontend_testing_akshare_runtime_gate.py` 在这里被视为 runtime / CI wiring verification，而不是 gate 逻辑真相源本身

### 6.2 Promotion Batch Verification

如果未来真的提升某一个保留候选，批次必须额外补：

1. focused adapter tests
2. focused backend route tests
3. API contract tests
4. repo-truth 和 gate regression tests

提升应保持“一次一个 candidate”的微批模式。

### 6.3 Task Closure Rules

当前任务语义应保持：

- `6.3 stock_news_main_em`
  - remains open
  - excluded from current promotion set
- `6.5 stock_dt_pool_em`
  - already closed as approved runtime mapping
- `6.6 stock_strong_pool_em`
  - already closed as approved runtime mapping
- `6.7 stock_weak_pool_em`
  - retired / removed with reason
  - should not retain registry / adapter / route / focused test artifacts
- `6.9 stock_new_em`
  - already closed as approved runtime mapping

`6.10`、`6.11`、`6.12`、`7.2`、`7.4`、`7.5`、`8.x` 这些下游任务，不能因为 advisory candidate 存在就提前闭合。

### 6.4 Commit Strategy

未来如果进入实现微批，应继续：

1. 一次一个 candidate
2. docs / gates 先行，或与 runtime code 同批但严格限定路径
3. 只 stage 当前 candidate 相关路径
4. 用路径级 `git show` 复核提交文件集

## Section 7. Documentation And OpenSpec Editing Plan

### 7.1 What Is Already Landed

以下仓库真相已由 `435bc8f00` 同步完成：

- `README.md`
- `docs/FUNCTION_TREE.md`
- OpenSpec proposal / design / tasks
- AkShare guide / troubleshooting / handoff docs
- Graphiti memory

本设计稿必须与这条已落地基线一致，不能静默把 repo-truth 提前升级成“已批准映射”。

### 7.2 What This Document Adds

本设计稿只新增：

1. advisory candidate 与 approved runtime mapping 的明确分层
2. `Section 3.2` retained candidate queue 的提升蓝图
3. `Section 1.1` 与 `Section 1.2` 的排除 / gap 记录
4. 如果将来提升候选，adapter / route / normalization 应如何落地的蓝图

### 7.3 Required Follow-Up If Promotion Happens Later

如果未来某个 retained candidate 被正式提升，以下文件需要一起更新：

| File | Typical change type |
| --- | --- |
| `openspec/changes/expand-akshare-data-sources/proposal.md` | update scope wording / approval boundary |
| `openspec/changes/expand-akshare-data-sources/design.md` | record promoted mapping and runtime contract |
| `openspec/changes/expand-akshare-data-sources/tasks.md` | move candidate task state forward |
| `README.md` | append or revise high-level truth note |
| `docs/FUNCTION_TREE.md` | append function-tree truth note |
| `docs/api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md` | append mapping ledger entry or change status |
| `docs/guides/akshare/AKSHARE_MARKET_EXTENSION_GUIDE.md` | update operator guidance |
| `docs/guides/akshare/AKSHARE_MARKET_TROUBLESHOOTING.md` | update failure / fallback notes |
| `docs/reports/tasks/expand-akshare-data-sources-handoff-2026-05-03.md` | append delivery and verification record |

## Section 8. Final Decisions

本设计稿最终记录的结论是：

1. `435bc8f00` 落地的 gate baseline 已完成，并继续作为 canonical truth
2. 当前已批准的 runtime boundary 仍然只有本地 AkShare 同名函数
3. `help_candidates` 继续保持 advisory 语义，不代表已实现能力
4. 当前仅保留三个 official rename evaluation candidate
   - `stock_dt_pool_em -> stock_zt_pool_dtgc_em`
   - `stock_strong_pool_em -> stock_zt_pool_strong_em`
   - `stock_new_em -> stock_zt_pool_sub_new_em`
5. `stock_news_main_em -> stock_news_main_cx` 当前继续排除在提升批次之外
6. `stock_weak_pool_em` 当前已是 no-candidate retired item
7. 未来如要提升任一候选，必须用单独微批同时更新 gate、repo-truth、runtime code 和 tests

## Next Step

这份设计稿 review 通过后，下一步不是直接写运行时代码，而是先决定：

- 是否把 `stock_dt_pool_em` 作为第一个 candidate promotion 微批
- 还是先只把 OpenSpec / repo-truth / gate 文案进一步细化为可执行 implementation plan

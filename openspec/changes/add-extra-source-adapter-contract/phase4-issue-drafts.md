# Phase 4 双仓 issue 草稿

> 提案 `add-extra-source-adapter-contract` 的 Phase 4 治理跟踪。
> 用户需要在两个仓各开一个 issue, 互相链接, 然后把 URL 填回
> `tasks.md` Phase 4.1 的占位符。
>
> 本文件列出可直接复制粘贴的 issue 正文。开 issue 完成后,
> 可删除本文件 (它不是契约文档, 只是协助工具)。

---

## Issue #1 — mystocks_spec 仓 (chengjon/mystocks)

**标题**:
```
[ExtraSource] Wave 2/3 八方法归属清单 + TEMP_OVERRIDE 治理 (cross-repo dependency)
```

**标签**: `cross-repo-dependency`, `temp-override-backlog`, `tech-debt`

**正文**:

```markdown
## 背景

OpenSpec 提案 `add-extra-source-adapter-contract` (Layer 1 已落地,
分支 `feat/c3-extra-source-adapter-stage2`, 提交 `88d64a77f`)
为消费者侧 auxiliary data source 建立了契约层。
提案 `design.md` §4 据此判定 B4.014 Wave 2/3 涉及的 8 个 akshare 直连方法的归属。

本 issue 跟踪:
1. 8 方法的最终归属判定
2. OpenStock 仓的对应 issue (双向链接, 见下方)
3. TEMP_OVERRIDE 到期后的处置流程

## 八方法归属清单 (来源: design.md §4 附录)

| akshare 函数 | OpenStock category | 归属 |
|---|---|---|
| `stock_em_bigdeal` | `MARKET_BIG_DEAL` (规划中) | TEMP_OVERRIDE ExtraSource |
| `stock_hsgt_fund_flow_detail_em` | 无规划 | 常规 ExtraSource |
| `stock_hsgt_south_net_flow_in_em` | 无规划(南向) | 常规 ExtraSource |
| `stock_hsgt_south_acc_flow_in_em` | 无规划(南向) | 常规 ExtraSource |
| `stock_hsgt_north_net_flow_in_em` | `NORTHBOUND_FLOW` (已注册) | **禁止 ExtraSource**, 迁移走 OpenStock |
| `stock_hsgt_north_acc_flow_in_em` | `NORTHBOUND_FLOW` (已注册) | **禁止 ExtraSource**, 迁移走 OpenStock |
| `stock_hsgt_hold_stock_em` | `NORTHBOUND_HOLDING` (已注册) | **禁止 ExtraSource**, 迁移走 OpenStock |
| `stock_fund_flow_big_deal` | 同 `stock_em_bigdeal` | TEMP_OVERRIDE ExtraSource |

## TEMP_OVERRIDE 跟踪 (需要 expires_on)

- `stock_em_bigdeal` / `stock_fund_flow_big_deal` → 共用一个 adapter
  `MARKET_BIG_DEAL`, `expires_on` 待 OpenStock issue 关闭后回填
  (提案默认 90 天上限, 即 `2026-09-30` 若本 issue 在 2026-07-02 后开启)

## 跨仓依赖

- **OpenStock 仓对应 issue**:
  <!-- 填入 OpenStock issue URL, 形如 https://github.com/<owner>/openstock/issues/<n> -->
  `<填入>`

- **OpenSpec 提案**:
  `openspec/changes/add-extra-source-adapter-contract/`

## 完成标志

- [ ] OpenStock 仓 `MARKET_BIG_DEAL` category 上线
- [ ] OpenStock issue 关闭后, 本仓删除对应 TEMP_OVERRIDE adapter
- [ ] 删除前 OpenStock issue 不得关闭 (design.md §4 状态联动规则)

## 关联

- 提案: `openspec/changes/add-extra-source-adapter-contract/`
- 实施分支: `feat/c3-extra-source-adapter-stage2`
- Layer 1 落地 commit: `88d64a77f`
```

---

## Issue #2 — OpenStock 仓

**标题**:
```
[Category Request] MARKET_BIG_DEAL (cross-repo dependency with mystocks_spec)
```

**标签**: `category-request`, `cross-repo-dependency`

**正文**:

```markdown
## Background

mystocks_spec has implemented the `ExtraSourceAdapter` Layer 1 contract
(commit `88d64a77f` on branch `feat/c3-extra-source-adapter-stage2`),
which formalizes how OpenStock consumers fill gaps for categories that
OpenStock does not cover.

B4.014 Wave 2/3 in mystocks_spec uses the akshare function
`stock_em_bigdeal` to fetch market big-deal data. Per the contract's
`design.md` §4 attribution rule, since `MARKET_BIG_DEAL` is a
**standard market primitive that multiple consumers would benefit
from**, it should be a first-class OpenStock category rather than
a mystocks-specific ExtraSource.

This issue requests OpenStock to register the `MARKET_BIG_DEAL` category
so that mystocks_spec's TEMP_OVERRIDE ExtraSource can be retired.

## Requested category

- **Name**: `MARKET_BIG_DEAL`
- **Description**: 大单成交数据 (单股或市场级别, 资金流向相关)
- **Suggested source**: akshare `stock_em_bigdeal` (current TEMP_OVERRIDE
  in mystocks_spec uses this)
- **OpenStock static inventory status**: not in current
  `DATA_CAPABILITY_SCOPE.md` snapshot (70 categories, 2026-07-02)

## Cross-repo tracking

- **mystocks_spec issue (this request's pair)**:
  <!-- 填入 mystocks_spec issue URL -->
  `<填入>`

- **mystocks_spec OpenSpec proposal**: `add-extra-source-adapter-contract`
  (specifically `design.md` §4 attribution appendix)

## Acceptance criteria

- [ ] `MARKET_BIG_DEAL` registered in `DATA_CAPABILITY_SCOPE.md`
- [ ] At least one provider (akshare `stock_em_bigdeal` or equivalent)
      wired up via `register_provider()`
- [ ] Snapshot date in `DATA_CAPABILITY_SCOPE.md` updated
- [ ] mystocks_spec Layer 1 `OPENSTOCK_STATIC_CATEGORIES` re-synced
      (will be done in a follow-up PR after this issue closes)

## State coupling rule

Per `design.md` §4 of the mystocks_spec proposal:

> OpenStock issue 关闭(category 已上线) → mystocks_spec CI 提醒删除 TEMP_OVERRIDE
> mystocks_spec 删除 TEMP_OVERRIDE 前, OpenStock issue 不得关闭

i.e. this issue MUST NOT be closed until mystocks_spec has confirmed
removal of the TEMP_OVERRIDE adapter on their side.
```

---

## 开 issue 操作步骤

1. **先开 OpenStock 仓 issue** (Issue #2), 复制上述正文, 占位符暂时留着。
2. 拿到 OpenStock issue URL 后, **回到本仓 (mystocks_spec) 开 Issue #1**,
   把 OpenStock URL 填入 Issue #1 的占位符。
3. **回到 OpenStock issue** 编辑正文, 把 Issue #1 的 URL 填入 Issue #2 的占位符。
4. 把两个 URL 填入本提案 `tasks.md` Phase 4.1:
   ```
   - mystocks_spec issue URL: `https://github.com/chengjon/mystocks/issues/<n>`
   - OpenStock issue URL: `https://github.com/<owner>/openstock/issues/<m>`
   ```
5. 勾选 Phase 4.1 的所有 checkbox, 把 Phase 4.2 也勾上。
6. (可选) 删除本文件 `phase4-issue-drafts.md` — 它是协助工具, 不属提案契约。
7. 提交 tasks.md 更新 (可放在提案合并前最后一次 commit)。

## 备注

- 若 OpenStock 仓不在 GitHub (自托管 / 其他平台), URL 格式相应调整。
- 若 OpenStock 暂无 `category-request` 标签, 用 `enhancement` / `feature-request`
  代替, 在正文里说明即可。
- 提案合并的 48h deadline (proposal.md §Impact 末尾) 从 Layer 1 合并起算,
  不是从本 issue 起算。本 issue 的开启是 Layer 1 合并后的治理动作, 不阻塞
  代码合并。

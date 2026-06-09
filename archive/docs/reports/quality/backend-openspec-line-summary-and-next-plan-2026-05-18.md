# Backend OpenSpec Line Summary And Next Plan

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> 本文是本条后端审计 / OpenSpec / Issue publication 线的阶段总结与下一步计划，供人工审核。
> 本文不是实现批准，不解锁 backend 代码变更，也不表示 GitHub Issues 已发布。

## 一、当前结论

本条线已经从“9 份 backend 审计/子方案文档审核”推进到“OpenSpec proposal 审批包 + GitHub Issue 发布草稿包”。

当前状态：

- 9 份 backend 审计/子方案文档已经完成审核和修订收口。
- 4 个 OpenSpec change 已创建并通过 `openspec validate --strict`。
- Matt Pocock 风格 review、review-of-review、addendum、post-review summary 已完成状态校准。
- 已新增跨 proposal orchestration 文档，解决 C/E/F/G 的执行顺序、共享 surface、blocked-by 和 rollback owner 问题。
- 已形成 human approval packet、compressed issue readiness blueprint、15 个 GitHub issue body 草稿和 manifest；经 P3 与 G 线跨线对齐并按人工审核偏好压缩后，其中 3 个可发布，3 个保留为 already-resolved audit-only，2 个 G 线草稿进入 publication hold，7 个旧草稿作为 superseded source bodies 留存。
- 已参考 `docs/reports/quality/cross-line-alignment-P3-impl-openspec-2026-05-18.md` 更新 publication package：C announcement / strategy / risk canonical router 决策不再发布新 issue。
- 已新增 `docs/reports/quality/cross-line-alignment-P3-impl-openspec-response-2026-05-18.md` 记录本次跨线对齐处理结果、验证证据和剩余计划。
- 已新增 `docs/reports/quality/backend-openspec-issue1-publication-runbook-2026-05-18.md`，作为只发布 issue 1 的 dry-run 执行清单。
- 已根据 `docs/reports/quality/backend-openspec-issue1-publication-runbook-mattpocock-review-2026-05-18.md` 收紧 runbook：补批准机制、检查命令、引用文档、认证失败停机条件，并移除后续发布层内容。
- 已记录 G 线最新并线判断：`docs/reports/quality/backend-openspec-g-line-integration-decision-2026-05-18.md`。结论是不与本线合并推进，只吸收状态事实。
- 已执行 publication review 修复：补 category label、验证 OpenAPI 生成、补 label setup、补 agent-readiness 候选和 publication tracks。
- 已在远端 GitHub repo `chengjon/mystocks` 创建并验证 4 个 triage state labels。
- 尚未发布任何 GitHub Issue。
- 本条线尚未执行任何 backend 实现代码变更；另一条 P3 implementation 线已完成部分 router 收口工作，已在本文和 issue package 中对齐。

## 二、已完成工作

### 1. 原始审计文档审核与收口

已审核并修订/收口的文档范围：

| 文档 | 状态 |
|---|---|
| `docs/reports/quality/backend-audit-2026-05-14.md` | 已审核 |
| `docs/reports/quality/backend-logging-fix-2026-05-14.md` | 已审核 |
| `docs/reports/quality/backend-residual-files-inventory-2026-05-14.md` | 已审核 |
| `docs/reports/quality/api-flat-to-package-migration-2026-05-14.md` | 已审核 |
| `docs/reports/quality/backend-singleton-to-di-2026-05-14.md` | 已审核 |
| `docs/reports/quality/backend-core-split-plan-2026-05-14.md` | 已审核 |
| `docs/reports/quality/health-endpoint-consolidation-2026-05-14.md` | 已审核 |
| `docs/reports/quality/backend-strategy-domain-governance-2026-05-14.md` | 已审核 |
| `docs/reports/quality/backend-risk-domain-governance-2026-05-14.md` | 已审核 |

主收口文档：

```text
docs/reports/quality/backend-audit-documents-review-2026-05-15.md
```

该阶段的核心结果是：原审计文档不能直接进入实现，必须先转换为 OpenSpec proposal 和 evidence/decision gates。

### 2. OpenSpec proposals

已创建并维护 4 个 OpenSpec changes：

| Change | 目标 | 当前任务数 | 状态 |
|---|---|---:|---|
| `consolidate-backend-api-domain-routers` | C：announcement / strategy / risk 路由治理；trading / backup 明确 deferred | 31 total / 11 checked | Valid |
| `consolidate-backend-health-endpoints` | G：health/status endpoint taxonomy 与 probe compatibility | 29 total / 27 checked | Valid |
| `migrate-backend-singletons-to-lifecycle-di` | E：singleton/getter 生命周期分类与首个低风险 DI pilot | 24 | Valid |
| `split-backend-core-modules-with-compatibility-wrappers` | F：Core import compatibility matrix 与 wrapper-safe split | 24 | Valid |

验证结果：

```text
openspec validate consolidate-backend-api-domain-routers --strict
Change 'consolidate-backend-api-domain-routers' is valid

openspec validate consolidate-backend-health-endpoints --strict
Change 'consolidate-backend-health-endpoints' is valid

openspec validate migrate-backend-singletons-to-lifecycle-di --strict
Change 'migrate-backend-singletons-to-lifecycle-di' is valid

openspec validate split-backend-core-modules-with-compatibility-wrappers --strict
Change 'split-backend-core-modules-with-compatibility-wrappers' is valid
```

### 3. Cross-change orchestration

新增：

```text
docs/reports/quality/backend-openspec-change-orchestration-2026-05-18.md
```

该文档解决的问题：

- C/G 都会触碰 route exposure、OpenAPI diff、consumer matrix。
- E/F 都会触碰 Core import surface、database/cache/security/socketio/logger 生命周期。
- Health/status consolidation 依赖 prefix-expanded final full-path route table。
- DI migration 对 Core import compatibility matrix 敏感。
- 所有 implementation issues 都必须有 `Blocked by` 链和 rollback owner。

当前执行顺序建议：

```text
approval/orchestration
  -> route/OpenAPI evidence
  -> C/G decisions
  -> F import compatibility matrix
  -> E singleton/getter inventory
  -> E first pilot / F first low-risk split batch
```

### 4. Review / addendum / post-review 收口

已处理以下 review 文件：

| 文档 | 处理结果 |
|---|---|
| `backend-openspec-drafts-mattpocock-review-2026-05-18.md` | 顶部已标注为 earlier draft snapshot review |
| `backend-openspec-drafts-mattpocock-review-2026-05-18-review.md` | 顶部已标注 task count 和 current status 已被 addendum/post-review supersede |
| `backend-openspec-drafts-mattpocock-review-2026-05-18-addendum.md` | 已吸收到 post-review summary |
| `backend-openspec-drafts-post-mattpocock-review-2026-05-18.md` | 当前 review stance 和 resolved/stale blocker disposition |

关键修正：

- 原 review 中的 blocker 已经多数变成 stale/resolved。
- 当前不是“缺 section 所以阻塞实现”，而是“proposal 结构已补齐，但 implementation 仍需 human approval 和 artifact completeness”。
- 当前 task count 总量为 C=31、G=29、E=24、F=24；其中 C 因跨线对齐已有 11/31 标记完成，这属于治理线 checklist 更新，不表示治理线执行了 backend 实现。

### 5. Approval packet

新增：

```text
docs/reports/quality/backend-openspec-human-approval-packet-2026-05-18.md
```

它是当前人工审批入口，明确：

- 批准什么：C/E/F/G 作为 proposal-level governance changes。
- 不批准什么：不批准 implementation。
- 审批人需要确认哪些 scope boundary。
- 批准后哪些 issue 可以先进入 evidence / decision-record。
- 何时才允许 implementation issues。

### 6. Issue readiness blueprint

新增：

```text
docs/reports/quality/backend-openspec-issue-readiness-blueprint-compressed-2026-05-18.md
```

原始拆出 13 个候选 issue bodies；当前新增 14/15 两个聚合 body，并压缩为 3 个可发布 issues：

| # | 类型 | 主题 | 发布状态 |
|---:|---|---|---|
| 1 | HITL | Approve backend OpenSpec orchestration and C/E/F/G proposal scope | publishable |
| 14 | AFK-after-approval | Build shared C/E/F evidence package | publishable |
| 15 | HITL / design | Decide post-approval implementation plan and follow-up boundaries | publishable |
| 2 | AFK-after-approval | Refresh shared route table and OpenAPI evidence | superseded / merged into 14 |
| 3 | HITL | Decide C announcement canonical router | audit-only / P3 resolved |
| 4 | HITL | Decide C strategy canonical router | audit-only / P3 resolved |
| 5 | HITL | Decide C risk canonical router | audit-only / P3 resolved |
| 6 | HITL | Create trading follow-up OpenSpec | superseded / merged into 15 |
| 7 | HITL | Create backup follow-up OpenSpec | superseded / merged into 15 |
| 8 | AFK-after-approval | Build G health/status taxonomy | publication hold / G-line superseded original scope |
| 9 | HITL | Decide G canonical health/status paths | publication hold / G-line superseded original scope |
| 10 | AFK-after-approval | Build F Core import compatibility matrix | superseded / merged into 14 |
| 11 | AFK-after-approval | Build E singleton/getter lifecycle inventory | superseded / merged into 14 |
| 12 | HITL | Select E first low-risk DI pilot | superseded / merged into 15 |
| 13 | AFK-after-approval / design-only | Draft first F low-risk Core split batch | superseded / merged into 15 |

当前规则：

- issue 1 是 approval gate。
- issue 14 是 approval 后最强的 `ready-for-agent` 候选。
- issue 15 保持 `ready-for-human` 或 `needs-triage`，因为它聚合多个 HITL/design 决策。
- `.planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md` 已作为 issue 15 / future proposal 输入基线审核通过，但不加入 issue 1 发布门禁。
- issue 8/9 不再作为原样可发布候选；如需继续，应重分类为 G residual-tail issue。
- 所有 implementation work 仍不得提前标 `ready-for-agent`。

### 7. GitHub issue draft package

新增草稿目录：

```text
docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/
```

包含：

- 15 个 issue body files，其中 3 个可发布，3 个 audit-only，2 个 publication-hold，7 个 superseded / merged。
- `manifest.md`。
- 3 条 `gh issue create` 草稿命令。
- Publication tracks：
  - Compressed order: `1 -> 14 -> 15`
  - G residual-tail: held issues 8/9 must be reclassified before any publication.
  - Track A/B 是依赖图和可并行准备口径，不是唯一发布顺序；实际发布以 manifest command order 为准。
- Audit-only / do-not-publish：issues 3/4/5，对应 P3 已解决的 announcement、strategy、risk canonical router 决策。
- Publication-hold：issues 8/9，对应 G 线已覆盖原 taxonomy / canonical-path scope，需重分类后才可发布。
- Superseded / merged：issues 2/6/7/10/11/12/13，仅作为 14/15 的来源细节留存。
- 所有命令现在都有：
  - 1 个 state label：`ready-for-human` 或 `needs-triage`
  - 1 个 category label：`enhancement`
- 没有任何命令使用 `ready-for-agent`。

### 8. Publication preflight 与 review response

新增：

```text
docs/reports/quality/backend-openspec-issue-publication-preflight-2026-05-18.md
docs/reports/quality/backend-openspec-issue-publication-review-response-2026-05-18.md
```

publication review 提出的 must-fix 已处理：

| Review finding | 当前状态 |
|---|---|
| M1: triage labels 不存在 | 已创建并验证 |
| M2: `openapi-before.json` 缺失 / generator 未验证 | 已运行成功并生成 artifact |
| M3: issue 缺 category label | manifest 10 条可发布命令已补 `--label enhancement` |
| S1: 需标出 future `ready-for-agent` candidates | manifest 已补 issue 2、8、10、11 |
| S2: publication order 应拆 tracks | manifest 已补 Track A / Track B |
| O3: decision issues 需说明 CONTEXT / docs/FUNCTION_TREE 更新 | issues 3/4/5/9/12 已补验收项 |
| O4: issue 4 是否遗漏 `strategy_management.py` | 当前 issue 4 已包含 |
| O5: `generate_openapi.py` 未测试 | 已测试成功 |

### 9. GitHub label setup

已在 `chengjon/mystocks` 创建并验证：

| Label | Color | Description |
|---|---|---|
| `needs-triage` | `FBCA04` | Awaiting maintainer evaluation |
| `needs-info` | `0052CC` | Waiting for more information from reporter |
| `ready-for-agent` | `0E8A16` | Fully specified, safe for AFK agent |
| `ready-for-human` | `B60205` | Needs human judgment or implementation |

记录：

```text
docs/reports/quality/backend-openspec-label-setup-2026-05-18.md
```

### 10. OpenAPI baseline

已生成：

```text
docs/reports/quality/generated/openapi-before.json
```

验证结果：

```text
OpenAPI version: 3.1.0
paths: 501
```

非阻塞 warning：

```text
Duplicate Operation ID redirect_to_canonical_api_strategy_mgmt__path__get
for function redirect_to_canonical at app/api/_strategy_mgmt_compat.py
```

## 三、当前未做事项

明确未做：

- 未发布任何 GitHub Issue。
- 未执行任何 `gh issue create`。
- 本条线未修改 backend 实现代码；P3 implementation 线的既有变更只作为对齐输入引用。
- 未将 G 线 residual verification、PM2 gate、strategy refactor 合并进本线 approval gate。
- 未执行 route deletion、router registry mutation、Core file move、DI migration。
- 未将任何 implementation issue 标为 `ready-for-agent`。
- 未创建 trading / backup follow-up OpenSpec proposal。

## 四、当前验证快照

| 检查项 | 当前结果 |
|---|---|
| C OpenSpec strict validate | pass |
| G OpenSpec strict validate | pass |
| E OpenSpec strict validate | pass |
| F OpenSpec strict validate | pass |
| C task count | 31 total / 11 checked |
| G task count | 29 total / 27 checked |
| E task count | 24 |
| F task count | 24 |
| GitHub triage state labels | created and verified |
| `enhancement` category label | exists |
| issue body files | 15 retained / 3 publishable / 3 audit-only / 2 held / 7 superseded |
| manifest `gh issue create` commands | 3 |
| premature `ready-for-agent` label | none |
| published `[Backend OpenSpec]` issue 1 | `#80` — `https://github.com/chengjon/mystocks/issues/80` |
| issue 1 GitHub state | `OPEN`; 2 status comments at 2026-05-18 23:38:55 CST |
| issue 14 / issue 15 publication status | not published |
| issue 14 triage dry-run | keep `needs-triage`; blocked by issue `#80` remaining open without approval / close decision |
| issue 14 publication runbook | prepared; blocked by issue `#80` remaining open without approval / close decision |
| codebase map input baseline | approved as issue 15 / future proposal input; not part of issue 1 gate |
| Route table baseline | refreshed after P3-D scanner fix: 538 routes, 0 full-path duplicate groups, 2 remaining orphan route files |
| OpenAPI baseline | exists, valid JSON, 501 paths |
| G line current status | `27 done / 2 open`; `4.6` blocked by cross-domain OpenAPI documentation/schema debt; `4.7` blocked by PM2 workflow approval |
| Issue 1 publication package scoped markdown governance gate | pass: 10 files, 0 errors |
| Approval + issue 14 dry-run / publication-runbook + issue 15 input + issue 80 status-comment scoped markdown governance gate | pass: 16 files, 0 errors |
| Global markdown governance gate | exits 1 due pre-existing historical docs outside this batch |

## 五、下一步工作计划

### P0. 人工审核当前材料

审核入口：

```text
docs/reports/quality/backend-openspec-human-approval-packet-2026-05-18.md
docs/reports/quality/backend-openspec-issue1-publication-runbook-2026-05-18.md
```

建议重点审核：

1. 是否批准 orchestration artifact。
2. 是否批准 C/E/F/G 作为 proposal-level governance changes。
3. 是否接受当前 scope boundary：
    - C 不实施 trading / backup，只登记 follow-up。
    - G 包含 health/status taxonomy，但不吞掉 backup domain ownership。
    - G 当前 `27 done / 2 open` 只作为事实更新吸收；不合并进 issue 1 approval gate。
    - E 只能先做一个低风险 DI pilot。
   - F 必须先完成 import compatibility matrix。
4. 是否接受 compressed issue readiness blueprint 的 3 个可发布 issues、3 个 already-resolved audit-only body、2 个 G-line publication-hold body，以及 7 个 superseded source bodies。
5. 是否允许开始发布 GitHub issues。

### P1. 若批准发布 issues

第一步只发布 issue 1：

```text
docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/01-approve-orchestration.md
```

执行前检查：

- `manifest.md` 中 issue 1 命令仍为 `ready-for-human + enhancement`。
- 不发布其他 2 个可发布 issues。
- 不发布 audit-only issues 3/4/5。
- 不发布 publication-hold issues 8/9。
- 不发布 superseded issues 2/6/7/10/11/12/13。

发布后：

- 记录真实 issue number。
- 替换其他 body 中的 `BLOCKED_BY_TODO: issue 1`。

### P2. 若 issue 1 审批通过

按 manifest command order 发布剩余可发布草稿。Issues 8/9 必须先重分类，不在当前 command order 中发布；issues 2/6/7/10/11/12/13 已合并进 14/15，不直接发布。

Manifest command order:

```text
1 -> 14 -> 15
```

Preparation Track A (C/G):

```text
1 -> 14 -> 15
```

Preparation Track B (E/F):

```text
1 -> 14 -> 15
```

发布规则：

- 每发布一个 blocker issue 后，替换依赖 issue 里的 `BLOCKED_BY_TODO`。
- Issue 14 可在 triage 复核后考虑转 `ready-for-agent`。
- Decision issues 仍应保持 `ready-for-human` 或 `needs-triage`，直到 human decision 完成。
- Issues 3/4/5 不发布；它们只作为 P3 already-resolved 审计留痕。
- Issues 8/9 暂不发布；它们只作为 G-line reclassification records。
- Issues 2/6/7/10/11/12/13 不发布；它们只作为 14/15 的 merged source records。

### P3. 若进入 evidence work

优先执行：

1. Issue 14：shared C/E/F evidence package。

这是最安全的 AFK-after-approval candidate，因为它是 evidence-only，不应改实现。原 issues 2/10/11 已合并进 14；原 issue 8 已进入 publication hold，不再作为 `ready-for-agent` 候选。

G 线已由另一条 implementation line 推进到 `27 done / 2 open`。本线可引用:

```text
docs/reports/quality/backend-health-status-implementation-boundary-2026-05-18.md
docs/reports/quality/backend-health-status-residual-blockers-2026-05-18.md
docs/reports/quality/backend-openspec-g-line-integration-decision-2026-05-18.md
```

但 `4.6` 应拆为独立 OpenAPI documentation stabilization，`4.7` 仍需 PM2 workflow 或 approved named equivalent 的显式批准。

### P4. 若进入 decision work

按依赖推进：

1. E first DI pilot selection。
2. trading / backup follow-up OpenSpec proposal strategy。
3. G residual-tail reclassification: OpenAPI documentation stabilization 与 PM2 workflow approval 是否拆成新 issues。
4. codebase map concerns classification: issue 14 evidence、issue 15 decision、future separate proposal candidate 或 quality debt lane。

C announcement / strategy / risk canonical router decisions 已由 P3 线完成，不再作为待发布 HITL decision issues。

Decision record 必须说明：

- 是否更新 `web/backend/CONTEXT.md`。
- 是否更新 `docs/FUNCTION_TREE.md`。
- 是否更新相关治理文档。
- rollback trigger。
- consumer matrix / compatibility state。

### P5. 暂不建议做的事

当前不建议：

- 直接发布全部 13 个 body files。
- 发布 issues 3/4/5 作为新的 HITL decision issues。
- 直接把 evidence issues 标为 `ready-for-agent`，除非 issue 1 已批准。
- 创建 implementation issues。
- 把 G 线 residual verification 或 strategy refactor 合并为本线 issue 1 发布前置条件。
- 未经显式批准执行会 stop/delete PM2 的完整 integration workflow。
- 删除 flat API 文件或 router shim。
- 移动 Core 文件。
- 开始 DI migration。
- 归档 OpenSpec changes。

## 六、需要你审核 / 决策的问题

请重点决定：

1. 是否认可当前 approval packet 作为人工审批入口。
2. 是否允许发布 GitHub issue 1。
3. 是否要求我在发布前先 stage/整理本条线相关文件。
4. 是否需要把本条线当前 artifacts 先单独提交一个 docs/OpenSpec commit。
5. 是否需要我继续生成 `BLOCKED_BY_TODO` 替换脚本，方便 issue 发布后批量回填真实 issue number。

## 七、推荐下一步

推荐先执行：

```text
人工审核 backend-openspec-human-approval-packet-2026-05-18.md
```

审核通过后，再发布 issue 1。不要直接发布剩余 12 个 issues，也不要进入 backend implementation。

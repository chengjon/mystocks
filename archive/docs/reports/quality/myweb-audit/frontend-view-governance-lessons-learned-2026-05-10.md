# 前端 View 治理历史经验教训（2026-05-10 整理）

> **用途**: 从前四轮 Vue 页面治理工作中提取经验教训，供当前 View Governance Spec 吸收、回避或优化。
>
> **来源**: `frontend-view-governance-history-2026-05-10.md` 所列全部文档的交叉分析。

---

## 一、当前 Spec 已吸收的经验

以下经验已明确体现在 `2026-05-10-frontend-view-governance-design.md` 中：

| 经验 | Spec 中的体现 |
|------|-------------|
| "不在路由中" ≠ "可删除" | Context 第 8-9 行明确警告 |
| 先分类后迁移 | Classification Model + Execution Plan Step 1 |
| artdeco-pages 仍含活跃资产 | Truth Sources 未将 artdeco-pages 标为废弃 |
| 小批次强验证 | Verification 节要求每个 mutation batch 报告 |
| 隐藏引用链很深 | Hidden Reference Checks 列出 7 类检查 |

---

## 二、应回避的陷阱（前批次踩过的坑）

### 陷阱 1：把文件移动本身当成进度

**发生了什么**: 第三轮目录重构中，部分批次将"路由入口切到 `views/<domain>/`"视为完成，但页面主体实现仍留在 `artdeco-pages/`。

**后果**: 产生了"路由指向新目录，实际代码还在旧目录"的双重真相。34 个活跃路由中 31 个仍指向 `artdeco-pages`。

**本批应如何回避**: Spec 的 Execution Plan Step 3 明确要求 "absorb reusable assets into canonical pages"，但需要额外约束——每个 archive-candidate 必须确认其业务逻辑已被 canonical 页面吸收或显式标记为不需要，而非仅检查路由入口是否已切换。

### 陷阱 2：用机械规则替代功能树判定

**发生了什么**: 04-07 composables 审计发现 `usePhase4Dashboard.ts` 有两份实现（root 380 行 / demo 355 行），表面看是"同一文件被不同页面复用"，实际是两套独立的历史页面实现。机械合并会丢失功能。

**后果**: `duplicate-candidate` 标签挂了两个月没有进一步处理，因为没有退场条件判定流程。

**本批应如何回避**: Spec 的 Classification Model 定义了 6 个状态但没有退场条件。应补充：每个 `archive-candidate` 必须附带 "successor page or explicit no-successor-needed rationale"。

### 陷阱 3：忽略测试守护文件

**发生了什么**: 04-07 审计发现 `monitoring/` 目录虽然不在 router 中，但有 `monitoring-*.spec.ts` 和旧 `router/index.js` 仍直接导入。`freqtrade-demo/`、`tdxpy-demo/`、`advanced-analysis/` 等都有对应的 `*-mainline-gate.spec.ts` 守护。

**后果**: 如果按 "router 未导入 = 可删除" 执行，会破坏测试套件，且这些测试往往守护的是样式/布局契约而非功能。

**本批应如何回避**: Spec 的 Hidden Reference Checks 提到了 "Tests and snapshots"，但应将 "mainline-gate spec" 列为高优先级检查项。建议在 inventory 步骤中先 grep `*-mainline-gate.spec.ts` 建立守护关系表。

### 陷阱 4：多入口变体未清理导致真相模糊

**发生了什么**: `web/frontend/src/` 下有 8 个 `main-*.ts/js` 变体文件。`index.html` 只加载 `main-standard.ts`，但 `verify-mount.js` 仍读取 `main.js`。

**后果**: 每次审计都要重新确认"哪个是真正的入口"，消耗重复验证成本。

**本批应如何回避**: 当前 Spec 聚焦 views/，但入口变体清理应作为前置任务。至少应将 `main-standard.ts` 的唯一入口地位写入 Truth Sources 表（目前 Spec 未提及前端入口真相）。

### 陷阱 5：治理停在本地，从未走完完整门禁

**发生了什么**: 第三轮 Phase 0-5 在本地仓库关闭，但 Phase 6-9（formal review、merge to main、CI/staging deploy、post-deploy validation）从未完成。

**后果**: 本地做了大量工作但从未合并到 main，部分改动可能已与 main 分叉。

**本批应如何回避**: Spec 的 Verification 节只要求本地验证。应补充：每个 mutation batch 的完成条件应包含 "can be merged to main without conflict" 的检查。

---

## 三、应优化的工作路径

### 优化 1：先建立守护关系表，再开始分类

**历史做法**: 04-07 审计中逐目录搜索引用关系，每个目录都是临时发现隐藏依赖。

**建议优化**: 在 Execution Plan Step 1（inventory）之前，增加一个 Step 0：

```
Step 0: 建立 full guard map
  - grep 所有 *-mainline-gate.spec.ts 的 import 目标
  - grep 所有 *.spec.ts 中对 views/ 的引用
  - grep 所有 main-*.ts/js 的加载关系
  - 输出: guard-map.csv (page -> guards)
```

这样 Step 2（classification）时可以直接查表，不用临时搜索。

### 优化 2：用双维度分类替代单一状态

**历史做法**: 第三轮对每个目录/文件标一个状态（有效/失效/待判定）。

**问题**: `views/stocks/` 被标为 "失效主路由层，但兼容保留中"——这个单一标签无法表达 "路由层失效 + composables 依赖仍活跃 + screener 功能已被复用" 的多维状态。

**建议优化**: 在当前 Spec 的 6 状态分类之上，增加两个维度标签：

| 维度 | 值 | 含义 |
|------|---|------|
| 路由状态 | active / redirect / dead | 是否被 router/index.ts 直接或间接导入 |
| 守护状态 | test-guarded / unguarded | 是否有 spec 文件守护 |

例如 `views/stocks/` = `archive-candidate` + `redirect` + `test-guarded`，比单一 `archive-candidate` 信息量大得多。

### 优化 3：双分叉页面处理模板化

**历史做法**: Phase4Dashboard 和 TechnicalAnalysis 的双分叉处理各写了一套独立的审计文档，步骤不同，格式不同。

**建议优化**: 为双分叉页面建立标准处理模板：

```
双分叉页面处理模板:
1. 列出所有实现版本（路径 + 行数）
2. 列出每个版本的消费者
3. 判断: wrapper? fork? parallel evolution?
4. 判断 canonical truth（哪个是主路由实际使用的）
5. 判断退场条件（非 canonical 版在什么条件下可以归档）
```

### 优化 4：archive 前先确认 test 迁移路径

**历史做法**: 第三轮没有处理测试文件。归档页面后发现 spec 仍引用旧路径。

**建议优化**: Spec 的 Execution Plan Step 4（move to archive）应增加前置条件：

```
archive-candidate 的退场检查表:
  [ ] 路由无引用
  [ ] 菜单无引用
  [ ] 布局 tab 无引用
  [ ] import.meta.glob 无匹配（当前代码库为 0，可跳过）
  [ ] *-mainline-gate.spec.ts 无引用，或已迁移到 canonical 页面
  [ ] 其他 spec 文件无引用，或已更新
  [ ] composable 消费者已归档或已迁移
```

### 优化 5：区分 "治理完成" 和 "合并就绪"

**历史做法**: 第三轮的 Phase 0-5 标记为 "materially closed in local repo truth"，但从未合并。

**建议优化**: 当前 Spec 应明确定义两种完成状态：

- **治理完成**（inventory + classification + archive moves done）
- **合并就绪**（治理完成 + type check pass + tests pass + no merge conflict with main）

只有 "合并就绪" 的批次才算真正关闭。

---

## 四、历史数据可直接复用的部分

以下 04-07 审计结论仍有效（需轻量验证但无需从零开始）：

| 已有结论 | 验证成本 | 建议 |
|---------|---------|------|
| 入口真相 `index.html → main-standard.ts → router/index.ts` | 低：确认 index.html 未变 | 直接复用 |
| artdeco-pages 仍含大量活跃资产 | 中：需重新计数 dynamic imports | 复用结论方向，更新数量 |
| demo / freqtrade-demo / tdxpy-demo 为实验资产 | 低：grep router 无变化 | 直接复用 |
| 双分叉 Phase4Dashboard / TechnicalAnalysis | 中：确认 root 版是否已退场 | 复用判定框架，更新状态 |
| monitoring 不在 router 但有测试守护 | 低：确认 spec 是否仍存在 | 直接复用 |
| composables 主要服务 root-level legacy pages | 中：需重新确认消费者 | 复用方向，逐文件验证 |

---

## 五、对当前 Spec 的具体修改建议

| 编号 | 建议 | 对应陷阱/优化 |
|------|------|-------------|
| S1 | 在 Truth Sources 表中补充前端入口真相 | 陷阱 4 |
| S2 | 为每个 `archive-candidate` 增加 successor/rationale 必填字段 | 陷阱 2 |
| S3 | 增加 Step 0：建立 guard map（spec → page 引用表） | 优化 1 |
| S4 | 分类时增加路由状态 + 守护状态两个辅助标签 | 优化 2 |
| S5 | archive 退场检查表补充 test/spec 迁移条件 | 优化 4 / 陷阱 3 |
| S6 | Verification 补充 "合并就绪" 定义 | 优化 5 / 陷阱 5 |
| S7 | 增加 mainline-gate spec 为高优隐藏引用检查项 | 陷阱 3 |

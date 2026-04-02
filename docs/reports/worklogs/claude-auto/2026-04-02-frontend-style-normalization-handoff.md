# 前端样式收敛工作交接清单 - 2026-04-02

## 1. 工作背景

- 当前工作线的核心目标，是继续把前端活跃页面和组件中的静态内联样式、硬编码中性色值、默认 fallback 样式，逐步收敛到主题变量或语义化 class。
- 本轮不是做大规模样式重构，也不是做视觉改版，而是严格按“单文件、单语义、低风险”的微批次推进。
- 早期已完成错误页批次化处理，后续持续消化 `P1/P2/P3` 中风险较低的样式债：
  - `P1`：静态 token 的 `:style` -> CSS class
  - `P2`：静态内联 `style="..."` -> CSS class
  - `P3`：低风险离散状态色 `:style` -> `:class`

## 2. 当前执行约束

- 隔离 worktree：
  - 分支：`codex/push-decision-orders-20260330`
  - 路径：`/tmp/mystocks-push-decision-orders`
- 主工作区 ` /opt/claude/mystocks_spec ` 很脏，包含用户自己的 Git 清理动作，不应直接触碰。
- 每个微批次固定流程如下：
  1. 先读取 `architecture/STANDARDS.md`
  2. 先做 `gitnexus impact`
  3. 只改一个很小的样式点
  4. 补最小 source-lock `vitest` 规格测试
  5. 跑对应 `vitest`
  6. 跑对应 `eslint`
  7. 只暂存本批次文件
  8. 跑 `gitnexus_detect_changes(scope="staged")`
  9. 提交并推送到 `main`
- worktree 跑前端验证时，需要临时软链：
  - `ln -s /opt/claude/mystocks_spec/web/frontend/node_modules /tmp/mystocks-push-decision-orders/web/frontend/node_modules`
  - 验证结束后删除：
  - `rm /tmp/mystocks-push-decision-orders/web/frontend/node_modules`
- 推送经常遇到远端快进，安全恢复流程：
  1. `git fetch origin main`
  2. `git rebase origin/main`
  3. `git push origin HEAD:main`

## 3. 已完成工作的总结

### 3.1 已完成的总体方向

- 已完成错误页样式收敛批次，包含 `Forbidden.vue`、`NetworkError.vue` 等页面的独立 worktree 验证、单测、lint、类型检查与主分支合并。
- 已持续完成大量前端样式微批次，覆盖：
  - 监控 / 风控 / 任务 / 策略 / Watchlist / Example / Market / SSE 组件
  - 静态 `:style` -> CSS class
  - 硬编码 `#xxxxxx` -> 主题 token
  - 离散状态色 -> 语义 class
  - 对应 source-lock `vitest` 规格测试

### 3.2 近期已推送到 `main` 的代表性提交

- `16c9abffa` `refactor(frontend): normalize backtest panel result palette`
- `245196fcc` `refactor(frontend): normalize strategy dialog shell tones`
- `4922c6a25` `refactor(frontend): normalize execution history preview color`
- `1a1e3d71b` `refactor(frontend): normalize strategy card neutral palette`
- `c9e14755d` `refactor(frontend): normalize task form divider color`
- `c9c86a519` `refactor(frontend): normalize enhanced risk dialog header tones`
- `6c21f9ad3` `refactor(frontend): normalize enhanced risk monitor tabs chrome`
- `df4de8da7` `refactor(frontend): normalize watchlist group palette`
- `1cd8e6755` `refactor(frontend): normalize strategy card panel gradient`
- `12a35a1ee` `refactor(frontend): normalize risk monitor state colors`
- `89aaa5b6d` `refactor(frontend): normalize websocket example text colors`
- `26eb1d326` `refactor(frontend): normalize portfolio progress token colors`

说明：
- 上述只是近期代表性提交，不是完整清单。
- 更早一批微提交已经覆盖 Heatmap、Stop Loss、Health Radar、Portfolio、FilterBar、RiskAlerts、TrainingProgress、PageConfig、LongHuBang、EnhancedDashboard 等多处页面和组件。

### 3.3 最近两批的具体内容

#### 批次 A：`StrategyDialog.vue`

- 提交：`245196fcc`
- 内容：
  - 将对话框外壳中性色收敛到主题变量
  - 范围只包括：
    - modal 容器背景
    - header 分隔线
    - 标题色
    - 关闭按钮色
    - 关闭按钮 hover 背景
- 新增测试：
  - `web/frontend/tests/unit/config/strategy-dialog-style-normalization.spec.ts`

#### 批次 B：`BacktestPanel.vue`

- 提交：`16c9abffa`
- 内容：
  - 将结果卡片与 footer 分隔线的中性色收敛到主题变量
  - 范围只包括：
    - 结果卡片渐变背景
    - 结果卡片边框
    - label / value 文字色
    - footer 顶部分隔线
- 新增测试：
  - `web/frontend/tests/unit/config/backtest-panel-style-normalization.spec.ts`

## 4. 当前状态

- 当前最新相关提交：
  - `16c9abffa refactor(frontend): normalize backtest panel result palette`
- 当前 worktree 状态：
  - 干净
  - 无未提交改动
- 最近两个批次的验证结论：
  - `gitnexus impact`：均为 `LOW`
  - 对应 `vitest`：均为 `1/1` 通过
  - 对应 `eslint`：均通过
  - `gitnexus_detect_changes(scope="staged")`：均为 `low`

## 5. 尚未完成的工作

当前没剩下需要一次性处理的大块功能，主要剩余的是零散、低风险、可继续拆分的样式债：

- 少量单文件静态背景色、边框色、标题色
- 少量默认 fallback 样式
- 少量仍可安全拆分的离散状态色

这些项仍然存在于少数 dialog / panel / market / task / strategy 同级组件中，但已不适合做“大扫除”，应继续保持微批次策略。

## 6. 下一步工作方向

建议继续按下面优先级推进：

### 6.1 第一优先级：同级 dialog / panel 的中性色小批次

- 目标特征：
  - 单文件
  - 单语义
  - `LOW` 风险
  - 可直接补 source-lock spec
- 优先处理对象：
  - `BacktestPanel.vue` 中剩余可单独切出的中性色小点
  - 同级别 dialog / modal / panel 组件里的默认背景、边框、标题色、辅助文本色

### 6.2 第二优先级：默认 fallback 样式

- 目标特征：
  - 原本只是默认值，不是业务状态色
  - 替换为主题变量后不会改变交互逻辑
- 例如：
  - 默认文本色
  - 默认边框色
  - 默认背景色

### 6.3 第三优先级：低风险离散状态色

- 仅在以下条件同时满足时继续推进：
  - 颜色状态离散且语义清楚
  - 改造范围局部
  - 不牵动图表运行时逻辑
  - 能通过 class 抽象表达

## 7. 明确不要做的事

除非单独审批，否则不建议直接扩大到以下范围：

- 纯动态图表配色
- 运行时计算颜色
- 跨多文件主题体系重构
- 纯视觉层面的“大一统重写”
- 仅凭“未使用”信号做删除或清理

原因：
- 这些方向更容易把低风险样式收敛工作，扩展成高扰动重构。
- 当前这条工作线的价值，正是通过小步、可验证、可回退的方式持续消化技术债，而不是追求一次性清仓。

## 8. 这项工作的价值

- 降低主题分裂和视觉漂移，减少不同页面继续新增硬编码色值的概率。
- 把样式清理从“人工感知”变成“可验证工程动作”，后续能靠 source-lock spec 防回归。
- 微提交边界清晰，出现问题时更容易定位、回退和审查。
- 隔离 worktree 作业避免污染用户正在进行的 Git 清理工作。
- 为后续更大范围的 token 统一、设计系统治理和样式债盘点提供干净基线。

## 9. 接手时可直接执行的 checklist

- [ ] 在 `/tmp/mystocks-push-decision-orders` 工作，不要直接碰主工作区脏文件
- [ ] 写操作前先读 `architecture/STANDARDS.md`
- [ ] 每次修改前先做 `gitnexus impact`
- [ ] 只选一个单文件、单语义的低风险样式点
- [ ] 用 `apply_patch` 修改文件
- [ ] 补一个最小 source-lock `vitest` 规格测试
- [ ] 运行对应 `vitest`
- [ ] 运行对应 `eslint`
- [ ] 只暂存本批次文件
- [ ] 运行 `gitnexus_detect_changes(scope="staged")`
- [ ] 提交并推送到 `main`
- [ ] 若推送被拒绝，执行 `fetch + rebase + re-push`
- [ ] 清理 worktree 中临时 `node_modules` 软链

## 10. 一句话总结

这条工作线已经进入“低风险样式债精修期”：大部分明显、可机械化处理的点已经清完，后续应继续坚持单文件、单语义、可验证的小批次推进，而不是扩成大规模视觉重构。

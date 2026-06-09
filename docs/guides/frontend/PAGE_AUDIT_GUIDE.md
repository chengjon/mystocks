# 页面审核指引：Impeccable + MyWeb Audit 多维度审核流程

> 版本: 1.0 | 日期: 2026-05-10
> 适用范围: MyStocks 项目所有前端页面
> 参考来源: `IMPECCABLE_WORKFLOW.md`、myweb-audit skill v2.1、Dashboard 双工具对比审计实践

---

## 1. 两个工具的定位

| 维度 | Impeccable | MyWeb Audit |
|------|-----------|-------------|
| **回答的问题** | 这个页面「设计得好不好」 | 这个页面「有没有工程缺陷」 |
| **审核视角** | 设计者（品牌、美学、UX） | 质检员（功能、数据、代码） |
| **核心输入** | PRODUCT.md + DESIGN.md | 路由真相 + 源代码 + API 行为 |
| **分析深度** | 视觉结果 → 设计法则对照 | 代码行为 → 检查清单逐项验证 |
| **输出粒度** | 评分 + 判断 + 设计方向建议 | 结构化发现 + 文件行号 + 修复目标 |
| **独有能力** | AI 痕迹检测、启发式评分、认知负荷、Persona 验证 | 数据状态一致性、API/render 对齐、stale data 逻辑、多角色并行审计 |
| **修复建议** | `/impeccable` 子命令引导 | 精确到文件:行号的 repair_target |

**互补关系**: Impeccable 覆盖"品牌合规 + UX 质量"，MyWeb Audit 覆盖"功能正确性 + 数据一致性"。两者重叠约 60%（视觉问题、a11y 基础、反模式），各自独有约 40%。

---

## 2. 场景判定：该用哪个工具

### 场景 A: 新页面上线前审核

**目标**: 确保页面在设计和工程两个维度都达标

**推荐流程**: Impeccable 先行 → MyWeb Audit 跟进 → 合并去重 → 修复

新页面最容易出现设计方向问题（AI 痕迹、反模式、认知负荷），Impeccable 的 critique 能在早期发现这些。功能正确性和数据状态问题则由 MyWeb Audit 补齐。

### 场景 B: 已有页面例行审计

**目标**: 排查工程缺陷，验证数据流正确性

**推荐流程**: MyWeb Audit 为主 → 仅在设计变更时追加 Impeccable

已有页面的设计方向通常已经稳定，主要风险在于代码层面的 bug（数据状态、交互正确性、stale data 逻辑）。MyWeb Audit 的 4 角色审计能系统覆盖。

### 场景 C: 设计系统 token 合规检查

**目标**: 确认页面是否遵守设计系统规范

**推荐流程**: 两者结合 — Impeccable 判断方向，MyWeb Audit 验证细节

Impeccable 能判断"这个页面是否应该用 display font"，MyWeb Audit 能列出"哪些具体 CSS 属性用了非标准 token 值"。方向 + 细节 = 完整覆盖。

### 场景 D: 批量多页面审计

**目标**: 对整个站点或某个业务模块做系统性扫描

**推荐流程**: MyWeb Audit（Full Mode）的 batch + manifest 机制

MyWeb Audit 有成熟的批量流程（route-inventory → batch 分组 → 并行角色审计 → 合并去重 → closeout checklist）。Impeccable 不适合批量场景，但可在每批次完成后对重点页面做一次 critique。

### 场景 E: 设计重构评审

**目标**: 评估页面是否需要视觉/交互重构

**推荐流程**: Impeccable `critique` + `bolder`/`quieter`/`distill` 迭代

设计重构是 Impeccable 的核心场景。先用 critique 获得评分和问题清单，再用专项命令逐步调整。MyWeb Audit 可在重构完成后做一轮回归验证。

### 场景 F: 单一问题快速排查

**目标**: 用户报告了一个具体问题（如"按钮点不动"、"数据显示不对"）

**推荐流程**: MyWeb Audit Quick Mode

Quick Mode 跳过 batch 和 manifest，直接在单页面内运行 4 个审计维度，产出简化报告。适合快速定位问题。

---

## 3. 推荐审核流程（标准流程）

以下流程适用于**场景 A（新页面上线前审核）**，即覆盖最全面的场景。其他场景可按需裁剪。

```
Phase 1: 设计评审 (Impeccable)
  Step 1  /impeccable critique <页面>       → 设计评审报告
  Step 2  记录评分、启发式问题、认知负荷、Persona 红标

Phase 2: 工程审计 (MyWeb Audit)
  Step 3  myweb-audit Quick Mode <页面>     → 工程审计报告
  Step 4  记录功能缺陷、数据状态问题、token 违规、a11y 问题

Phase 3: 合并与去重
  Step 5  对照两份报告，标记重叠问题
  Step 6  建立统一修复清单，按严重度排序

Phase 4: 修复
  Step 7  Impeccable 专项命令修复设计问题
  Step 8  直接代码修复工程问题

Phase 5: 验证
  Step 9  /impeccable polish <页面>         → 设计打磨
  Step 10 重新运行 myweb-audit 验证修复       → 回归确认
```

### Phase 1 详细说明: Impeccable 设计评审

```bash
# 确保上下文已加载（每个项目只需一次）
node .claude/skills/impeccable/scripts/load-context.mjs

# 运行设计评审
/impeccable critique <页面名称或路径>
```

**产出物关注点:**

| 审核维度 | 产出 | 判定标准 |
|----------|------|---------|
| Nielsen 启发式评分 | X/40 分 | < 28 分需要修复 |
| 认知负荷检查 | N/8 失败 | > 1 项失败需要修复 |
| AI slop 反模式表 | 检测结果 | YES 项需要修复 |
| Persona 红标 | 用户场景风险 | 红标项需要修复 |

**判定**: 如果评分 >= 32 且无 AI slop 检测和 Persona 红标，可跳过 Phase 4 的 Impeccable 修复步骤。

### Phase 2 详细说明: MyWeb Audit 工程审计

```
/myweb-audit <页面路径>
```

**产出物关注点:**

| 审核角色 | 覆盖范围 | 关注的发现类型 |
|----------|---------|---------------|
| functional-audit | 按钮、链接、Tab、表单、导航 | 交互不通、装饰性控件、空操作 |
| data-state-audit | API 调用、渲染一致性、状态覆盖 | 零值初始化、数据源混用、stale data 逻辑 |
| visual-artdeco-audit | token 合规、排版、间距、层级 | 非标准值、display font 误用、装饰干扰 |
| responsive-a11y-audit | 断点、ARIA、focus、语义 HTML | 缺少 ARIA 角色、reduced-motion、语义标记缺失 |

**判定**: 无 Blocking/High 发现时，Phase 4 的工程修复可降级为 Low 优先级。

### Phase 3 详细说明: 合并与去重

建立一张合并表，每个问题只出现一次:

| 列 | 说明 |
|----|------|
| Issue ID | 统一编号 (I-01, I-02, ...) |
| 来源 | impeccable / myweb-audit / 两者共有 |
| 严重度 | 统一为 P0-P3 |
| 问题描述 | 一句话 |
| Impeccable 编号 | 对应 critique 报告中的编号（如有） |
| MyWeb Audit 编号 | 对应 audit 报告中的编号（如有） |
| 修复目标 | 文件:行号 |
| 修复方式 | impeccable 命令 或 直接代码修改 |

**去重规则**: 以下情况合并为一条:
- 两份报告描述同一问题的同一根因（如"display font 用在按钮"）
- 两份报告的修复目标指向同一文件和同一代码位置

**不合并的情况**:
- 两份报告描述同一表面现象但根因不同（如 Impeccable 说"信息过载"是设计层级问题，MyWeb Audit 说"collapsible 默认展开"是交互逻辑问题）

### Phase 4 详细说明: 修复

**Impeccable 可修复的设计问题:**

| 问题类型 | 修复命令 |
|----------|---------|
| 字体层级混乱 | `/impeccable typeset <页面>` |
| 色彩策略问题 | `/impeccable colorize <页面>` |
| 间距/网格不一致 | `/impeccable layout <页面>` |
| 缺少交互反馈 | `/impeccable animate <页面>` |
| 设计太安全/无聊 | `/impeccable bolder <页面>` |
| 设计太吵/过载 | `/impeccable quieter <页面>` |
| 冗余元素过多 | `/impeccable distill <页面>` |

**MyWeb Audit 发现的工程问题**: 直接代码修改，参考报告中的 `repair_target` 和 `evidence` 字段定位到具体文件行号。

---

## 4. 裁剪指南

根据场景裁剪标准流程:

| 场景 | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 |
|------|---------|---------|---------|---------|---------|
| A: 新页面上线 | 完整 | 完整 | 完整 | 完整 | 完整 |
| B: 已有页面例行 | 跳过 | 完整 | 简化 | 仅工程修复 | MyWeb Audit 回归 |
| C: Token 合规 | critique 仅看排版/色彩 | 完整 | 去重 | typeset/layout | polish |
| D: 批量审计 | 仅重点页面 | Full Mode batch | 批量去重 | 批量修复 | closeout checklist |
| E: 设计重构 | 完整 + 迭代 | 重构完成后跑一轮 | 去重 | 专项命令 | critique 再评分 |
| F: 单一问题排查 | 跳过 | Quick Mode | 跳过 | 定向修复 | 验证修复项 |

---

## 5. 报告命名与归档

| 工具 | 报告路径 | 命名规则 |
|------|---------|---------|
| Impeccable critique + audit | `docs/reports/DASHBOARD_CRITIQUE_AUDIT.md` | `<页面名>_CRITIQUE_AUDIT.md` |
| MyWeb Audit | `docs/reports/quality/myweb-audit/<页面名>-myweb-audit-YYYY-MM-DD.md` | 含日期 |
| 合并报告 | `docs/reports/<页面名>-AUDIT-MERGED-YYYY-MM-DD.md` | 含日期 |

---

## 6. 检查清单维度对照

以下是两个工具在审核维度上的完整对照，帮助理解各自的覆盖范围:

| 审核维度 | Impeccable | MyWeb Audit | 说明 |
|----------|:----------:|:-----------:|------|
| **AI 生成痕迹** | ■ | □ | 仅 Impeccable: hero-metric、glassmorphism、side-stripe 等 |
| **Nielsen 启发式** | ■ | □ | 仅 Impeccable: 10 项 0-4 分评分 |
| **认知负荷** | ■ | □ | 仅 Impeccable: 8 项通过/失败检查 |
| **Persona 验证** | ■ | □ | 仅 Impeccable: 以具体用户场景验证设计 |
| **品牌性格合规** | ■ | □ | 仅 Impeccable: 对照 PRODUCT.md 品牌原则 |
| **信息架构层级** | ■ | ○ | Impeccable 系统评估; MyWeb Audit 部分涉及（card grid 层级） |
| **功能交互正确性** | □ | ■ | 仅 MyWeb Audit: 按钮、Tab、链接、表单实际行为 |
| **数据状态一致性** | □ | ■ | 仅 MyWeb Audit: API/render 对齐、loading/empty/error 覆盖 |
| **Stale data 逻辑** | □ | ■ | 仅 MyWeb Audit: 刷新失败时的数据保留和降级 |
| **API 数据语义** | □ | ■ | 仅 MyWeb Audit: 数据来源是否与展示含义匹配 |
| **Token 合规** | ○ | ■ | MyWeb Audit 精确到行号; Impeccable 部分涉及 |
| **响应式断点** | □ | ■ | 仅 MyWeb Audit: 检测低于最低分辨率的断点 |
| **ARIA 无障碍** | ○ | ■ | MyWeb Audit 系统化检查; Impeccable 表格式扫描 |
| **语义 HTML** | ○ | ■ | MyWeb Audit 更详细; Impeccable 标记为 PARTIAL |
| **视觉反模式** | ■ | ■ | 两者重叠: display font 误用、emoji、identical grid、gradient |
| **inline styles** | ■ | ■ | 两者都检测: 6+ inline style 实例 |
| **prefers-reduced-motion** | ■ | ■ | 两者都检测 |
| **focus-visible** | ■ | ■ | 两者都检测 |
| **A-share 色彩惯例** | ■ | ■ | 两者都验证: 红涨绿跌 |

图例: ■ 完整覆盖 | ○ 部分涉及 | □ 不覆盖

---

## 7. 产出物示例

### Dashboard 审核合并清单示例（2026-05-10）

| ID | 严重度 | 来源 | 问题 | 修复方式 |
|----|--------|------|------|---------|
| I-01 | P1 | 两者 | Display font (Cinzel) 用在 UI 标签和按钮 | `/impeccable typeset dashboard` |
| I-02 | P1 | 两者 | 3 列相同卡片网格，无视觉层级 | `/impeccable layout dashboard` |
| I-03 | P1 | 两者 | Emoji 作为导航图标 | `/impeccable polish dashboard` |
| I-04 | P2 | 两者 | 渐变覆盖层干扰数据展示 | `/impeccable quieter dashboard` |
| I-05 | P2 | impeccable | 信息密度过高，缺少层级分档 | `/impeccable distill dashboard` |
| I-06 | P2 | impeccable | 认知负荷 5/8 失败（Critical） | `/impeccable distill dashboard` |
| I-07 | P2 | impeccable | 帮助/文档完全缺失（Heuristic 10 = 1/4） | `/impeccable onboard dashboard` |
| I-08 | P1 | myweb-audit | Tab 缺少 ARIA 角色 | 代码修改 |
| I-09 | P1 | myweb-audit | 股票池 Tab 无数据支撑（装饰性控件） | 代码修改 |
| I-10 | P1 | myweb-audit | 零值初始化数据在首次加载前渲染 | 代码修改 |
| I-11 | P1 | myweb-audit | Sentiment 指标源自行业数而非个股数 | 代码修改 |
| I-12 | P2 | myweb-audit | Stress test 纯本地公式无持久标注 | 代码修改 |
| I-13 | P2 | myweb-audit | captureCoreTrace 并行请求互相覆盖 | 代码修改 |
| I-14 | P2 | myweb-audit | Collapsible 默认展开 | 代码修改 |
| I-15 | P2 | myweb-audit | 非标准 token 值（opacity 86%, padding 2rem） | 代码修改 |
| I-16 | P2 | myweb-audit | 4 个低于最低分辨率的响应式断点 | 代码修改 |
| I-17 | P2 | 两者 | 无 prefers-reduced-motion | 代码修改 |
| I-18 | P2 | myweb-audit | 语义 HTML 不完整 | 代码修改 |
| I-19 | P3 | 两者 | 品牌名 QUANTIX 重复出现 | 代码修改 |

---

## 8. 命令速查

### Impeccable

```
# 准备（每个项目一次）
/impeccable teach                          → PRODUCT.md
/impeccable document                       → DESIGN.md

# 审核
/impeccable critique <页面>                → 设计评审
/impeccable audit <页面>                   → 技术审计

# 专项修复
/impeccable typeset / colorize / layout / animate / bolder / quieter / distill <页面>

# 打磨
/impeccable polish <页面>                  → 上线前检查
/impeccable harden <页面>                  → 边界情况
/impeccable clarify <页面>                 → 文案优化

# 新页面
/impeccable shape <描述>                   → UX/UI 方案
/impeccable craft <描述>                   → 完整实现

# 实时迭代
/impeccable live                           → 浏览器内变体选择
```

### MyWeb Audit

```
# 单页面快速审核
/myweb-audit <页面路径>                    → Quick Mode 4 维度报告

# 批量审核
/myweb-audit <模块名或路由范围>            → Full Mode batch + manifest

# 输出 MD 文档
# 在 myweb-audit 请求中追加 "把审核结果保存为 MD 文档"
```

---

*页面审核指引 v1.0 | 2026-05-10 | 基于 Dashboard 双工具对比审计实践*

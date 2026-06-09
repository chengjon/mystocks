# MyWeb Audit Skill & Agents 设计审核报告

> **审核日期**: 2026-04-25
> **审核范围**: `.claude/skills/myweb-audit/`（SKILL.md + 7 references）及 `.claude/agents/myweb-audit-*.md`（5 agents）
> **关联提案**: `openspec/changes/add-page-audit-orchestration-governance/`
> **审核目标**: 审计设计质量，识别结构性问题与优化机会，不修改任何代码

---

## 总体评价

MyWeb Audit 是一套设计完整度较高的前端页面审计编排系统。角色边界清晰、Artifact 体系（manifest / findings / closeout）合理、ArtDeco 对齐规则务实。但在**执行模型定义、Agent 工具适配、环境前置条件、桌面端一致性**等方面存在结构性缺陷，直接影响真实执行效果。

以下按优先级分类列出具体优化建议。

---

## A. 高优先级（影响正确性与可执行性）

### A1. 执行模型未定义：代码审查 vs 活页面检查

**问题**: SKILL.md 描述的审计行为（按钮点击、表单提交、loading 状态、breakpoint 检查）明确需要访问**运行中的前端应用**，但整份 Skill 和所有 Agent 都只声明了 `Read, Bash` 工具，没有任何地方说明：
- 应该使用 Playwright MCP、Chrome DevTools MCP，还是仅通过代码阅读推断
- 前端服务是否必须在审计前启动
- 当浏览器工具不可用时如何降级

这导致实际执行时，执行者（Claude 或 subagent）无法确定用什么手段完成审计，往往会退化为纯代码阅读——与 Skill 声明的交互验证目标不一致。

**建议**:
1. 在 SKILL.md 增加 `Environment Prerequisites` 小节，明确要求：
   - 前端 dev server 或 PM2 服务必须 reachable
   - 后端 API 可达（至少 health check 通过）
   - 浏览器 MCP 工具（Playwright 或 Chrome DevTools）可用
2. 在每个 Agent 的 frontmatter 中声明实际需要的工具（见 A2）
3. 增加降级分支：当浏览器工具不可用时，明确说明只能做代码审查级别的审计，并标记 findings 为 `verification: partial`

### A2. Agent 工具声明与实际需求不匹配

**问题**: 5 个 Agent 全部声明 `tools: Read, Bash`，但各角色的实际需求差异很大：

| Agent | 当前声明 | 实际需要 |
|-------|---------|---------|
| route-inventory | Read, Bash | Read, Bash（仅代码审查，匹配） |
| functional-audit | Read, Bash | 需要**浏览器交互工具**（click、fill、navigate）来验证按钮/表单/对话框 |
| data-state-audit | Read, Bash | 需要**网络请求检查工具**（list_network_requests、console_messages）来验证 API/render 一致性 |
| visual-artdeco-audit | Read, Bash | 需要**截图工具**（take_screenshot）来做视觉判断 |
| responsive-a11y-audit | Read, Bash | 需要**视口调整工具**（resize_page、emulate）来检查 1440→390 各断点 |

**建议**:
1. 为每个 Agent 更新工具声明，匹配其实际职责
2. 在 Agent 的 Workflow 中显式说明每一步使用什么工具完成
3. 当工具不可用时，Agent 应输出 `verification_surface: code-review-only` 标记

### A3. 响应式检查断点与项目定位矛盾

**问题**: SKILL.md、audit-checklist.md、responsive-a11y-agent 一致要求检查 `1440, 1280, 1024, 768, 390` 五个断点。但项目 `CLAUDE.md` 明确声明：

> **平台支持**: 仅桌面端 Web（最小分辨率 1280x720），禁止移动端/平板适配和 `@media (max-width)` 响应式规则。

`768` 和 `390` 断点在桌面端 workbench 场景下是无效检查维度。强制检查这些断点会：
- 产生大量无效 findings（因为项目不承诺这些尺寸的适配）
- 浪费审计资源
- 与项目标准文档直接矛盾

**建议**:
1. 将响应式检查断点调整为桌面端范围：`1920, 1440, 1280`（最小支持分辨率）
2. `1024` 以下可标记为 `informational` 而非 defect
3. 删除 `768` 和 `390` 的强制检查要求
4. 在 audit-checklist.md 第 5 节增加说明：本项目为桌面端 workbench，低于 1280 的断点仅做 informational 记录，不作为 defect 判定依据

### A4. 修复前缺少用户确认门禁

**问题**: SKILL.md Workflow 第 7 步 "Fix issues that are within the approved frontend scope" 中的 "approved" 没有定义审批机制。Workflow 从 Audit → Fix → Verify 是连续执行的，没有用户确认环节。这意味着审计发现的问题会被自动修复，用户无法：
- 选择哪些问题优先修复
- 拒绝某些修复
- 调整修复优先级

**建议**:
1. 在 Workflow 的第 6 步（Merge findings）和第 7 步（Fix）之间增加显式门禁：
   ```
   6.5. Present merged findings to the user for approval before repair.
        - List all findings by severity
        - Ask user to confirm which to fix now vs defer
        - Record user decision in the batch manifest
   ```
2. 在 Repair Scope Rules 中明确 "approved" 的含义：用户在步骤 6.5 的确认

---

## B. 中优先级（影响效率与一致性）

### B1. Agent 调度模式未定义

**问题**: SKILL.md 定义了 4 个并行审计角色（functional / data-state / visual / responsive-a11y），但没有说明：
- 这 4 个角色应该并行调度还是顺序执行
- 每个角色是作为独立 subagent 还是在主上下文中按 prompt 模板执行
- 并行调度时的上下文传递方式
- 当某个角色失败时的处理（是否阻塞其他角色）

**建议**:
1. 在 SKILL.md Role Handoff 小节增加执行模式声明：
   ```
   Execution Mode:
   - route-inventory: sequential (must complete before other roles start)
   - functional-audit, data-state-audit, visual-artdeco-audit, responsive-a11y-audit:
     parallel (can run concurrently as independent subagents)
   - merge/dedup: sequential (after all parallel roles complete)
   ```
2. 说明当单个角色失败时不阻塞其他角色，但标记其 findings 为 `incomplete`

### B2. Findings Schema 缺少正式校验定义

**问题**: `findings-schema-example.md` 使用 YAML 示例说明结构，但没有提供 JSON Schema 或等效的形式化校验定义。这意味着：
- 不同 Agent 产出的 finding 格式可能不一致
- 去重逻辑的 `dedupe key` 没有形式化定义（仅靠 `finding_id` 命名惯例）
- Merge 过程缺少可编程的校验规则

**建议**:
1. 在 `references/` 下增加 `findings-schema.json`（JSON Schema 定义），包含：
   - 必填字段与类型约束
   - `severity` 的枚举值校验
   - `issue_type` 的枚举值校验
   - `finding_id` 的命名模式约束
2. 定义 `dedupe_key` 的计算规则：基于 `page + issue_type + repair_target` 组合去重

### B3. Shared Impact 定位与 OpenSpec 提案冲突

**问题**: SKILL.md 的 report-template.md 将 `Shared Impact` 放在 Issue Summary 之后、Repair Plan 之前，作为报告的一个章节。但 OpenSpec proposal `add-page-audit-orchestration-governance/design.md` 明确提出应将 `Shared Impact` 升级为**前置判定**（pre-judged），在修复前就识别跨页面影响。当前的报告章节定位无法实现前置判定。

**建议**:
1. 在 Workflow 中增加 Shared Impact 前置判定步骤：
   ```
   6.5. Identify Shared Impact before repair:
        - Check whether findings involve shared components, global styles, or shared composables
        - Mark cross-page impact candidates
        - Record impact basis and potentially affected pages
   ```
2. 在 findings schema 中增加 `shared_impact_candidate: boolean` 和 `cross_page_impact: list<route>` 字段

### B4. 缺少轻量模式（Single Page Quick Audit）

**问题**: 当前 Skill 设计了完整的 batch → manifest → 4-role audit → merge → fix → verify → closeout 流程。对于单页快速检查（如"帮我看一下 market overview 页面有没有明显问题"），这套流程过重，会导致：
- 用户不愿为简单检查启动完整流程
- 执行者在简单场景下跳过 Skill 直接操作，失去标准化

**建议**:
1. 在 SKILL.md 增加 `Quick Mode` 小节：
   ```
   Quick Mode:
   When the user requests a single-page quick check without full batch orchestration:
   - Skip manifest and batch setup
   - Run all audit dimensions inline (not as separate agents)
   - Output a simplified inline report
   - Skip closeout checklist
   ```
2. 在 `When to Use` 中区分 full mode vs quick mode 的触发条件

### B5. Agent Output Contract 不统一

**问题**: 5 个 Agent 的 Output Contract 字段各不相同：

| Agent | Output 字段 |
|-------|------------|
| route-inventory | page list, module/group, page purpose, canonical entry, special-route notes, batch suggestion, priority notes |
| functional-audit | severity, title, reproduction steps, expected, actual, likely repair target |
| data-state-audit | severity, issue type, trigger, expected vs actual, evidence, dependency |
| visual-artdeco-audit | severity, title, visible symptom, why it harms, repair direction, file target |
| responsive-a11y-audit | severity, breakpoint/surface, trigger, expected vs actual, evidence note, repair target |

4 个审计角色的输出结构不完全对齐，增加 merge/dedup 阶段的工作量。

**建议**:
1. 统一 4 个审计角色的 Output Contract 为相同结构：
   ```
   - severity (enum: Blocking | High | Medium | Low)
   - title (string)
   - trigger (reproduction steps)
   - expected (string)
   - actual (string)
   - evidence (string)
   - repair_target (file or component)
   - dependency (string | null)
   ```
2. route-inventory 的输出结构可以不同（它是 scope-setting 角色而非 finding-producing 角色），但应明确与 findings schema 的关系

---

## C. 低优先级（改善体验与维护性）

### C1. 版本管理缺少变更记录

**问题**: SKILL.md 提到 `v1.3` 但没有版本历史。每次 "clarifies" 的内容无法追溯。

**建议**:
1. 在 `references/` 下增加 `CHANGELOG.md`
2. 每次修改 SKILL.md 或 references 时记录版本号、日期、变更摘要

### C2. ArtDeco 参考文件优先级链缺少可达性校验

**问题**: SKILL.md 列出了 5 个 ArtDeco 参考文件的优先级顺序，但没有说明当某个文件不存在或已过时时的处理方式。

**建议**:
1. 在 Repository Alignment 小节增加说明：当高优先级文件缺失时，依次降级到下一优先级文件
2. 对每个参考文件标注其维护状态（active / legacy / deprecated）

### C3. Batch Manifest 缺少恢复语义

**问题**: manifest-template.md 有 `status: in_progress` 等状态值，但没有定义：
- 如何从一个已有的 `in_progress` manifest 恢复
- manifest 文件的存储位置约定
- 跨会话恢复时如何确认环境状态

**建议**:
1. 在 manifest-template.md 增加 `resume_rules` 字段：
   ```yaml
   resume_rules:
     storage_path: docs/reports/audits/{audit_run_id}/
     recovery_check:
       - verify frontend server reachable
       - verify backend API reachable
       - verify no new route changes since last run
   ```
2. 在 SKILL.md Workflow 开头增加恢复检测：检查是否有未完成的 manifest，如有则询问用户是恢复还是重新开始

### C4. Severity 模型缺少跨角色一致性保障

**问题**: 4 个审计角色独立判定 severity，但同一问题在不同角色视角下可能得到不同 severity。例如：
- functional-audit 可能把一个按钮不可用判定为 `Blocking`
- visual-artdeco-audit 可能把同一按钮的样式问题判定为 `Medium`

merge/dedup 阶段没有说明如何处理 severity 冲突。

**建议**:
1. 在 merge 步骤增加 severity 冲突解决规则：取各角色中的最高 severity
2. 在 closeout checklist 增加 severity 一致性检查项

### C5. 环境异常 Fallback 缺失（与 OpenSpec 提案对齐）

**问题**: OpenSpec proposal 明确提出需要为以下环境异常设计 fallback：
- Playwright 报告目录权限问题
- PM2 端口冲突
- dirty worktree + staged-scope 切换
- Agent 容量耗尽

当前 SKILL.md 的 Failure Handling 小节只覆盖了 route/page/API 层面的失败，没有覆盖这些执行环境层面的异常。

**建议**:
1. 在 SKILL.md 的 Failure Handling 小节后增加 `Environment Fallback` 小节：
   ```
   Environment Fallback:
   - Browser tool unavailable → downgrade to code-review-only audit, mark all findings as verification: partial
   - Port conflict → attempt alternate port from allowed range (3020-3029 / 8020-8029), record actual port in manifest
   - Agent capacity exhausted → fall back to sequential inline execution, skip parallel dispatch
   - Dirty worktree staging conflict → stage target files individually, avoid blanket git add
   ```

---

## D. OpenSpec 提案未解决问题

`openspec/changes/add-page-audit-orchestration-governance/` 提出了 3 个 Open Questions，建议在优化 Skill 时一并解决：

| 问题 | 建议答案 |
|------|---------|
| manifest 是否必须落盘？ | **会话内临时态即可**。Full batch audit > 5 页时建议落盘以支持跨会话恢复；Quick mode 不需要落盘 |
| structured findings 格式？ | **Markdown frontmatter + YAML**。与当前 findings-schema-example.md 一致，不需要 JSON Schema 双格式维护。在 references 中增加校验规则即可 |
| Chromium-only / external-frontend reuse 策略？ | **按批次覆盖**。在 manifest 中增加 `verification_strategy` 字段，默认 `full`，可选 `chromium-only` 或 `code-review-only` |

---

## E. 建议执行顺序

如果采纳以上建议，推荐的实施顺序：

1. **A3** — 修正响应式断点（简单，直接修改 references 即可）
2. **A1 + A2** — 补充环境前置条件与 Agent 工具声明（核心结构性修正）
3. **A4** — 增加修复前确认门禁（影响用户体验）
4. **B1** — 定义 Agent 调度模式（影响执行一致性）
5. **B4** — 增加轻量模式（提升 Skill 适用面）
6. **B5** — 统一 Agent Output Contract（改善 merge 效率）
7. **C5** — 补充环境异常 fallback（与 OpenSpec 提案对齐）
8. 其余项按需实施

---

## 附录：文件清单

| 文件 | 类型 | 审核状态 |
|------|------|---------|
| `.claude/skills/myweb-audit/SKILL.md` | Skill 主文件 | 审核完成 |
| `.claude/skills/myweb-audit/references/audit-checklist.md` | 检查清单 | 审核完成 |
| `.claude/skills/myweb-audit/references/artdeco-rubric.md` | ArtDeco 评分标准 | 审核完成 |
| `.claude/skills/myweb-audit/references/batching-rules.md` | 分批规则 | 审核完成 |
| `.claude/skills/myweb-audit/references/report-template.md` | 报告模板 | 审核完成 |
| `.claude/skills/myweb-audit/references/manifest-template.md` | 批次清单模板 | 审核完成 |
| `.claude/skills/myweb-audit/references/findings-schema-example.md` | Findings 结构示例 | 审核完成 |
| `.claude/skills/myweb-audit/references/closeout-checklist.md` | 收口检查清单 | 审核完成 |
| `.claude/agents/myweb-audit-route-inventory.md` | Agent: 路由清单 | 审核完成 |
| `.claude/agents/myweb-audit-functional-audit.md` | Agent: 功能审计 | 审核完成 |
| `.claude/agents/myweb-audit-data-state-audit.md` | Agent: 数据状态审计 | 审核完成 |
| `.claude/agents/myweb-audit-visual-artdeco-audit.md` | Agent: 视觉 ArtDeco 审计 | 审核完成 |
| `.claude/agents/myweb-audit-responsive-a11y-audit.md` | Agent: 响应式与可访问性审计 | 审核完成 |

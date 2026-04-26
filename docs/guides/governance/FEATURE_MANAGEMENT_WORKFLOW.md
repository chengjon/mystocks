# 功能管理流程指南

> **补充规范说明**:
> 本文件是项目补充标准、执行细则或专题规范，不是仓库共享规则的唯一事实来源。
> 仓库级共享规则总入口仍以 `architecture/STANDARDS.md` 为准；执行流程、命令与协作约束再参考根目录 `AGENTS.md`。本文件用于补充某一专题的执行细则、约束或参考模板。
>
> 若本文件与 `architecture/STANDARDS.md`、根目录 `AGENTS.md` 或当前已批准执行口径不一致，应优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md` 与当前实现；若无冲突，则按本文件的专题范围执行。


> **版本**: 1.0.2 | **创建日期**: 2026-03-12 | **更新日期**: 2026-04-26
> **适用范围**: 所有功能开发、维护、废弃流程

---

## 一、文档体系概览

本项目建立了以下功能管理文档：

| 文档 | 位置 | 用途 |
|------|------|------|
| **AI Quick Start** | `docs/guides/ai-tools/AI_QUICK_START.md` | 按任务类型路由到正确的治理入口和功能域 |
| **功能树** | `docs/FUNCTION_TREE.md` | 业务能力总线，也是开发方向与功能边界总览，维护功能状态和领域入口 |
| **Docs 首页** | `docs/INDEX.md` | 按任务类型和阅读顺序快速路由 |
| **更新日志** | `CHANGELOG.md` | 版本变更记录 |
| **本指南** | `docs/guides/governance/FEATURE_MANAGEMENT_WORKFLOW.md` | 功能管理流程、同步规则、PR 对齐要求 |

### 1.1 入口职责划分

- `docs/INDEX.md`：按任务类型找入口，适合 AI 和开发者快速定向。
- `docs/guides/ai-tools/AI_QUICK_START.md`：提供完整任务路由、最小读取路径和文档优先级。
- `docs/FUNCTION_TREE.md`：按功能域找规范、代码、测试和运行入口。
- `governance/mainline/task-cards/pr-<PR号>.yaml`：`function_tree` 的唯一机器事实源；PR 模板只是 reviewer 镜像。
- `CHANGELOG.md`：记录已经发生的变更事实。
- 本指南：规定什么时候必须同步更新功能树和 PR 描述。

---

## 二、功能生命周期

```
📝 计划中 → 🚧 开发中 → ✅ 完成 → (可选) ⚠️ 需修复 → ✅ 完成
                                    ↓
                              🔒 已废弃
```

### 状态定义

| 状态 | 图标 | 触发条件 | 操作 |
|------|------|----------|------|
| 计划中 | 📝 | 需求确认，尚未开发 | 在功能树添加条目 |
| 开发中 | 🚧 | 开始编码 | 更新功能树状态 |
| 完成 | ✅ | 测试通过，合并到main | 更新功能树+CHANGELOG |
| 需修复 | ⚠️ | 发现Bug或问题 | 在CHANGELOG记录问题 |
| 已废弃 | 🔒 | 功能不再使用 | 标记废弃原因 |
| 实验性 | 🧪 | 实验功能 | 说明可能变化 |

---

## 三、操作流程

### 3.1 新功能开发流程

```
1. 需求确认
   └─→ 在 docs/FUNCTION_TREE.md 添加功能条目，状态 📝
   └─→ 在所属一级领域补齐或更新“领域入口”表

2. 开始开发
   └─→ 更新状态为 🚧
   └─→ 在 CHANGELOG.md [Unreleased] → 新增 添加条目

3. 开发完成
   └─→ 运行测试确保通过
   └─→ 更新功能树状态为 ✅
   └─→ 更新功能树完成度百分比
   └─→ 确认该领域的规范/API/前端/核心代码/测试/运行入口仍有效

4. 合并到 main
   └─→ 在 CHANGELOG.md 记录变更
   └─→ 在 task card 中填写 `function_tree.domain_id` / `node_id` / `affected_entrypoints`
   └─→ 在 PR 中镜像 task card 的稳定 ID 和 reviewer 摘要
   └─→ 如需发布版本，创建版本号段落
```

### 3.2 Bug 修复流程

```
1. 发现问题
   └─→ 在功能树将状态改为 ⚠️
   └─→ 在 CHANGELOG.md [Unreleased] → 修复 记录
   └─→ 如排障入口变化，同步更新该领域“运行与排障入口”

2. 修复完成
   └─→ 更新状态回 ✅
   └─→ 在 CHANGELOG 记录修复
   └─→ 在 PR 中补充验证证据和受影响入口
```

### 3.3 功能废弃流程

```
1. 确认废弃
   └─→ 在功能树将状态改为 🔒
   └─→ 添加废弃原因和替代方案
   └─→ 在 CHANGELOG [Unreleased] → 弃用 记录
   └─→ 调整该领域入口，移除失效主入口或替换为继任入口

2. 代码移除
   └─→ 在 CHANGELOG [Unreleased] → 移除 记录
   └─→ 从功能树删除条目或移到归档区
```

### 3.4 文档入口同步流程

```
1. 判断变更是否影响功能入口
   └─→ 影响规范 / API / 前端 / 核心代码 / 测试 / 运行任一入口时，必须同步更新 FUNCTION_TREE
   └─→ 若新增主路由目录 / 主页面、主 API 包路由或 canonical 入口，必须补写 FUNCTION_TREE 中对应“主入口”描述
   └─→ 若退役兼容层、旧页面、旧 API 根入口、shim 或平行实现，必须同步更新 FUNCTION_TREE 中的边界状态和继任入口说明

2. 判断是否跨领域
   └─→ 主领域维护完整入口
   └─→ 其他领域只保留引用说明，避免双份维护

3. 检查 Docs 首页
   └─→ 如任务路由发生变化，同步更新 docs/INDEX.md

4. 检查 AI Quick Start
   └─→ 如任务类型、最小读取路径或高优先级入口变化，同步更新 docs/guides/ai-tools/AI_QUICK_START.md

5. 提交前复核
   └─→ 确认 task card.function_tree 与 PR 镜像字段、验证证据、FUNCTION_TREE 稳定 ID 一致

### 3.5 Transcript 证据治理

```
1. 新 transcript 采集
   └─→ `AUTO` / `MANUAL` transcript 必须落到 Mongo transcript ledger
   └─→ 每条 transcript 必须归属到具体 `work_item_id`

2. 导出边界
   └─→ `TASK-REPORT.md` 只保留 transcript 摘要，不作为正文真相源
   └─→ 完整正文只允许显式 session export，且仅限 90 天热存窗口

3. 历史迁移
   └─→ 历史 markdown transcript block 只建立 legacy audit index + archive reference
   └─→ 不回填正文，不伪造新的 append-only transcript body events
```
```

---

## 四、文档更新模板

### 4.1 功能树更新模板

```markdown
### 领域入口

| 入口类型 | 链接/路径 | 用途 |
|---------|----------|------|
| 规范入口 | `path/to/doc.md` | 该领域必须遵守的规则 |
| API/契约入口 | `path/to/api.py` | 后端路由、契约或接口文档 |
| 前端/交互入口 | `path/to/view.vue` | 主要页面、组件或路由入口 |
| 核心代码入口 | `path/to/module/` | 主要实现代码 |
| 测试与验证入口 | `path/to/test.py` | 单测、集成或 E2E 入口 |
| 运行与排障入口 | `path/to/runbook.md` | 部署、健康检查、排障手册 |

### X.X 子功能名称 ✅/🚧/📝

| 功能点 | 状态 | 代码位置 | 说明 |
|--------|------|----------|------|
| 具体功能 | ✅ | `path/to/file.py` | 功能描述 |
```

### 4.2 CHANGELOG 更新模板

```markdown
## [Unreleased]

### 新增 (Added)
- 新功能描述 [#issue号]

### 变更 (Changed)
- 变更描述 [#issue号]

### 修复 (Fixed)
- 修复描述 [#issue号]
```

### 4.3 版本发布模板

```markdown
## [X.Y.Z] - YYYY-MM-DD

### 新增 (Added)
- 功能1
- 功能2

### 变更 (Changed)
- 变更1

### 修复 (Fixed)
- 修复1
```

---

## 五、完成度计算规则

每个功能领域的完成度按以下公式计算：

```
完成度 = (✅功能数 / 总功能数) × 100%
```

示例：
- 领域有 10 个功能
- 8 个已完成 ✅
- 2 个开发中 🚧
- 完成度 = 8/10 = 80%

---

## 六、PR 与 Review 对齐要求

### 6.0 机器事实源

- `governance/mainline/task-cards/pr-<PR号>.yaml` 是 `function_tree` 的唯一机器事实源。
- PR 模板只负责 reviewer 镜像，不承担机器门禁真相源职责。
- `meta-governance` 仅存在于 machine-readable catalog / task card 中，不要求镜像到业务 `FUNCTION_TREE` 文档。

### 6.1 PR 描述必填字段

若本次改动影响功能、入口、流程或状态，PR 描述至少补充以下字段：

- `变更类型`：`feature` / `bugfix` / `docs` / `refactor`
- `function_tree.domain_id`：对应稳定业务域 ID 或 `meta-governance`
- `function_tree.node_id`：对应稳定节点 ID
- `function_tree.affected_entrypoints`：`governance` / `api` / `frontend` / `core` / `tests` / `operations`
- `function_tree.update_status`：`required` / `not-needed`
- `function_tree.secondary_domains`：跨业务域时显式列出
- `function_tree.exemption_reason`：豁免或自举原因
- `验证证据`：命令、结果、关键链路
- `风险与回滚`：是否跨域、是否影响主链路、如何回滚

### 6.2 Review 检查要点

- PR 中的功能域和节点是否能在 `FUNCTION_TREE` 中定位到。
- 变更是否影响领域入口但未同步更新。
- 跨领域功能是否只在主领域维护完整入口。
- 验证证据是否覆盖核心路径、错误路径或直接依赖。

---

## 七、定期维护

### 每周检查

- [ ] 更新功能树完成度
- [ ] 检查是否有长期 🚧 状态的功能
- [ ] 检查 ⚠️ 状态功能的修复进度

### 每月检查

- [ ] 审查 🔒 废弃功能是否可以移除
- [ ] 更新功能领域完成度
- [ ] 发布月度 CHANGELOG 总结

### 版本发布时

- [ ] 将 [Unreleased] 内容移到新版本
- [ ] 更新版本号和日期
- [ ] 更新功能树中的统计信息

---

## 八、关联文档

- Docs 首页: [INDEX.md](../INDEX.md)
- AI Quick Start: [../ai-tools/AI_QUICK_START.md](../ai-tools/AI_QUICK_START.md)
- 功能树: [FUNCTION_TREE.md](../FUNCTION_TREE.md)
- 更新日志: [../../CHANGELOG.md](../../CHANGELOG.md)
- 架构规范: [../../architecture/STANDARDS.md](../../architecture/STANDARDS.md)
- 开发流程: [CLAUDE.md](../../CLAUDE.md)

---

## 九、常见问题

### Q1: 功能应该归属哪个领域？

A: 参考功能树的 10 大领域分类：
1. 市场数据与行情
2. 技术分析与指标
3. 策略管理与回测
4. 风险管理与监控
5. 投资组合与交易
6. 监控与告警
7. 高级分析与AI
8. 系统管理与配置
9. 数据存储与管理
10. 公告与信息

### Q2: 如何处理跨领域功能？

A: 在主要领域记录完整功能，在其他相关领域添加引用链接。

### Q3: 小修复需要更新功能树吗？

A: 如果只是局部代码修复且不影响功能状态、领域入口或任务路由，只需更新 CHANGELOG。只要入口或状态发生变化，就必须同步更新功能树。

---

*最后更新: 2026-03-12*

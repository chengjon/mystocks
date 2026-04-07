# MyStocks 项目 - Agents & Skills 可用性报告

> **历史总结说明**:
> 本文件是 API 相关的阶段性总结、报告、状态或验收材料，不是当前 API 契约、当前实施基线或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`；若涉及 API 契约事实源，再以实际的 FastAPI 路由 + Pydantic Schema + `/openapi.json` 为准。
>
> 文内统计值、完成状态、修复结论和验收结果如未重新复核，应视为历史快照，不得直接当作当前事实。


**生成时间**: 2026-01-23
**项目**: MyStocks 量化交易数据管理系统
**分析范围**: .claude/agents/, .claude/skills/, 插件系统

---

## 📊 概述

### 当前配置状态
- **Skills**: 9个已配置技能
- **Agents**: 8个已配置代理
- **Commands**: 9个自定义命令
- **Hooks**: 7个事件钩子 (部分优化中)
- **插件系统**: 160+ Claude Code 插件可用

---

## 🛠️ Skills 系统 (9个)

### 📁 项目级 Skills (`.claude/skills/`)

| Skill名称 | 类型 | 优先级 | 状态 | 说明 |
|----------|------|--------|------|------|
| `backend-dev-guidelines` | 领域技能 | 高 | ✅ 活跃 | FastAPI后端开发规范 |
| `frontend-dev-guidelines` | 领域技能 | 高 | ✅ 活跃 | Vue前端开发规范 |
| `frontend-design` | 设计技能 | 中 | ✅ 活跃 | UI/UX设计生成 |
| `ui-ux-pro-max` | 设计技能 | 高 | ✅ 活跃 | 高级UI/UX设计系统 |
| `skill-developer` | 工具技能 | 中 | ✅ 活跃 | Skill开发工具 |
| `workflow-developer` | 工具技能 | 中 | ✅ 活跃 | 工作流开发 |
| `dev-docs-workflow` | 工具技能 | 中 | ✅ 活跃 | 文档工作流 |
| `notification-developer` | 工具技能 | 中 | ✅ 活跃 | 通知系统开发 |
| `progressive-disclosure-pattern` | 工具技能 | 低 | ✅ 活跃 | 渐进式披露模式 |

### 🎯 Skill 激活机制

**基于关键词自动激活** (`skill-rules.json`):
- **后端关键词**: backend, API, route, controller, service, database, FastAPI
- **前端关键词**: frontend, Vue, component, UI, UX, responsive, mobile
- **设计关键词**: design, UI/UX, layout, component, responsive, mobile

**触发条件**:
1. **关键词匹配**: 用户提示包含指定关键词
2. **文件路径匹配**: 编辑特定路径文件时自动激活
3. **意图模式匹配**: 识别开发意图自动激活

---

## 🤖 Agents 系统 (8个)

### 📁 项目级 Agents (`.claude/agents/`)

| Agent名称 | 专业领域 | 工具权限 | 状态 |
|----------|---------|----------|------|
| `frontend-developer` | 前端开发 | 完整 | ✅ 活跃 |
| `auth-route-tester` | 认证路由测试 | 受限 | ✅ 活跃 |
| `build-error-resolver` | 构建错误解决 | 完整 | ✅ 活跃 |
| `code-architecture-reviewer` | 代码架构审查 | 只读 | ✅ 活跃 |
| `database-verifier` | 数据库验证 | 数据库 | ✅ 活跃 |
| `documentation-architect` | 文档架构 | 文档 | ✅ 活跃 |
| `frontend-error-fixer` | 前端错误修复 | 前端 | ✅ 活跃 |
| `strategic-plan-architect` | 战略规划 | 规划 | ✅ 活跃 |

### 🎯 Agent 专业能力

#### 1. **frontend-developer** - 前端开发专家
```
专业领域: Vue 3 + TypeScript + Pinia + WebSocket
工具权限: 完整文件操作权限
使用场景: 组件开发、状态管理、API集成、性能优化
```

#### 2. **build-error-resolver** - 构建错误解决专家
```
专业领域: 构建工具、依赖管理、错误诊断
工具权限: 构建工具 + 文件操作
使用场景: npm/yarn错误、TypeScript编译错误、依赖冲突
```

#### 3. **code-architecture-reviewer** - 代码架构审查
```
专业领域: 架构模式、代码质量、设计原则
工具权限: 只读分析权限
使用场景: PR审查、架构评估、重构建议
```

#### 4. **database-verifier** - 数据库验证专家
```
专业领域: TDengine + PostgreSQL + 数据完整性
工具权限: 数据库查询权限
使用场景: 数据迁移验证、查询优化、约束检查
```

---

## ⚡ Commands 系统 (9个)

### 📁 自定义命令 (`.claude/commands/`)

| 命令 | 功能分类 | 状态 | 说明 |
|------|---------|------|------|
| `pm2-status` | 运维监控 | ✅ 活跃 | PM2进程状态查看 |
| `speckit.plan` | 项目规划 | ✅ 活跃 | Speckit规划生成 |
| `speckit.constitution` | 项目规划 | ✅ 活跃 | 项目宪章管理 |
| `speckit.checklist` | 项目规划 | ✅ 活跃 | 任务清单生成 |
| `speckit.analyze` | 项目规划 | ✅ 活跃 | 规范分析 |
| `openspec.proposal` | 规范管理 | ✅ 活跃 | OpenSpec提案创建 |
| `openspec.apply` | 规范管理 | ✅ 活跃 | OpenSpec实施 |
| `openspec.archive` | 规范管理 | ✅ 活跃 | OpenSpec归档 |
| `dev-docs` | 文档开发 | ✅ 活跃 | 开发文档生成 |

---

## 🔗 插件生态系统

### 📦 Claude Code 插件市场 (160+)

#### 1. **anthropic-agent-skills** - 官方技能 (17个)
- `frontend-design` - 前端设计
- `web-artifacts-builder` - Web工件构建
- `webapp-testing` - Web应用测试
- `create-agent-skill` - Agent/Skill创建
- `heal-skill` - Skill修复

#### 2. **Every Marketplace** - 综合插件 (50+)
- 开发工具、测试框架、部署工具
- AI辅助编程、代码分析、文档生成

#### 3. **Superpowers Marketplace** - 超级能力 (30+)
- 高级AI能力、自动化工具
- 复杂任务处理、多模态分析

#### 4. **ClaudeForge Marketplace** - 社区插件 (40+)
- 开源社区贡献的实用工具
- 特定领域解决方案

#### 5. **CC Marketplace** - 专业插件 (20+)
- 企业级工具、专业开发环境
- 高级集成和自动化

---

## 🎯 使用指南

### 选择合适的Agent/Skill

#### 开发任务类型匹配
```typescript
// 前端开发任务
if (task.includes('Vue') || task.includes('component')) {
  useAgent: 'frontend-developer'
  useSkill: 'frontend-dev-guidelines'
}

// 后端API开发
if (task.includes('FastAPI') || task.includes('endpoint')) {
  useSkill: 'backend-dev-guidelines'
}

// 架构设计审查
if (task.includes('review') || task.includes('architecture')) {
  useAgent: 'code-architecture-reviewer'
}

// 构建错误解决
if (task.includes('build') || task.includes('error')) {
  useAgent: 'build-error-resolver'
}
```

#### Skill自动激活
- **无需手动调用** - 系统根据关键词自动激活
- **智能上下文** - 相关文档自动加载到Claude上下文
- **无缝集成** - 不中断正常开发流程

### 最佳实践

#### 1. **任务分配策略**
```bash
# 自动分配 - 系统根据关键词智能选择
输入: "创建Vue组件处理股票数据"
自动激活: frontend-dev-guidelines + frontend-design

# 手动指定 - 复杂任务明确指定
输入: "/use-agent frontend-developer 优化交易组件性能"
```

#### 2. **协作模式**
```bash
# 多Agent协作
输入: "重构用户认证系统，需要架构审查"
/use-agent strategic-plan-architect 制定重构计划
/use-agent code-architecture-reviewer 审查现有代码
/use-agent frontend-developer 实施重构
```

#### 3. **质量保证**
```bash
# 自动质量检查
输入: "完成了API开发"
/use-agent build-error-resolver 验证构建无错误
/use-agent code-architecture-reviewer 审查代码质量
```

---

## 📈 系统优势

### 🚀 **开发效率提升**
- **智能激活**: 基于上下文自动选择最佳工具
- **无缝集成**: 不中断开发流程的辅助系统
- **专业分工**: 每个Agent/Skill专注于特定领域

### 🎯 **质量保障**
- **规范遵循**: Skill系统确保代码符合项目标准
- **自动化检查**: Agent系统提供持续的质量监控
- **最佳实践**: 内置的行业标准和最佳实践

### 🔧 **可扩展性**
- **插件生态**: 160+插件支持不断扩展能力
- **自定义开发**: 可以创建项目特定的Agent/Skill
- **标准化接口**: 统一的调用和集成方式

---

## 📚 相关文档

- **Agent管理**: `docs/guides/ai-tools/CLAUDE_AGENTS_SUMMARY.md`
- **Skill配置**: `.claude/skill-rules.json`
- **使用指南**: `docs/guides/ai-tools/CLAUDE_CODE_AGENTS_MANAGEMENT_GUIDE.md`
- **插件列表**: `docs/api/plugin_list.md`

---

## 🎊 总结

MyStocks项目的Agent/Skill系统提供了**完整的AI辅助开发生态**：

- **9个专业Skills**: 覆盖开发、设计、文档、通知等全领域
- **8个专用Agents**: 前端开发、错误解决、架构审查、数据库验证等
- **160+插件支持**: 从官方到社区的完整工具链
- **智能激活系统**: 基于关键词和上下文的自动工具选择
- **标准化工作流**: OpenSpec + Speckit + 自定义命令的完整开发流程

这个系统将**AI能力无缝集成到开发流程中**，显著提升开发效率和代码质量，是现代AI辅助开发的最佳实践体现。

**系统状态**: ✅ **完全可用** - 随时可以使用任何Agent/Skill开始开发工作

---

*报告生成*: Claude Code
*系统状态*: 生产就绪
*最后更新*: 2026-01-23</content>
<parameter name="filePath">AGENTS_SKILLS_AVAILABILITY_REPORT.md

# Claude Agents 快速参考卡片

## 📊 现状 (2025-12-10 清理后)

```
✅ 已清理完成

占位符代理删除: 7/7 ✅
用户级代理保留: 6/6 ✅
项目级代理目录: 已清空 ✅
显示混乱问题: 已解决 ✅
```

---

## 🎯 可用代理 (6 个)

### 快速选择表

| 需求场景 | 推荐代理 | 快速提示 |
|---------|---------|---------|
| 📝 代码审查 | **code-reviewer** | "我完成了代码实现" |
| 🐛 问题诊断 | **root-cause-debugger** | "出现了这个错误..." |
| 🏗️ 系统设计 | **web-fullstack-architect** | "设计一个Web应用" |
| 💾 数据库设计 | **database-architect-cn** | "设计数据库架构" |
| 💰 成本优化 | **first-principles-fullstack-architect** | "我们预算有限..." |
| 🔌 API开发 | **contract-driven-dev-expert** | "设置API-first开发" |

---

## 🔍 详细信息

### 1️⃣ code-reviewer (红色)
- **模型**: inherit
- **触发**: 代码完成后
- **功能**: 质量/安全/维护性审查

### 2️⃣ contract-driven-dev-expert (黄色)
- **模型**: sonnet
- **适用**: 小团队API开发
- **功能**: Mock服务、CI/CD配置

### 3️⃣ database-architect-cn (青色)
- **模型**: inherit
- **适用**: 数据库架构设计
- **功能**: 选型、优化、高可用

### 4️⃣ first-principles-fullstack-architect (蓝色)
- **模型**: inherit
- **适用**: 成本约束的架构
- **功能**: 需求分析、防止过度设计

### 5️⃣ root-cause-debugger (绿色)
- **模型**: inherit
- **触发**: 遇到bug/错误
- **功能**: 诊断、修复、预防

### 6️⃣ web-fullstack-architect (红色)
- **模型**: inherit
- **适用**: Web应用全栈设计
- **功能**: 前后端、性能、安全、部署

---

## ✅ 已删除的占位符

| 名称 | 状态 |
|------|------|
| auth-route-tester | ❌ 已删除 |
| build-error-resolver | ❌ 已删除 |
| code-architecture-reviewer | ❌ 已删除 |
| database-verifier | ❌ 已删除 |
| documentation-architect | ❌ 已删除 |
| frontend-error-fixer | ❌ 已删除 |
| strategic-plan-architect | ❌ 已删除 |

---

## 📖 更多信息

详细指南: `docs/guides/ai-tools/CLAUDE_AGENTS_SUMMARY.md`
完整审查: `docs/api/AGENTS_AUDIT_REPORT.md`
官方文档: `/opt/mydoc/Anthropic/Claude-code/sub-agents.md`

---

**状态**: ✅ 就绪
**日期**: 2025-12-10

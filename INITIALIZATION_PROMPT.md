# Frontend CLI 任务初始化

**Worker CLI**: Frontend CLI (前端开发工程师)
**初始化时间**: 2025-12-30
**预期完成**: 4周 (32小时)

---

## 📋 任务文档位置

你的完整任务说明位于: `TASK.md`

**立即行动**: 请仔细阅读 `TASK.md` 的全部内容，特别关注:
- ✅ 核心职责 (关键目标)
- ✅ 任务清单 (4个阶段)
- ✅ 验收标准 (每个任务的完成标准)
- ✅ 质量标准 (代码、测试、用户体验)
- ✅ 问题报告机制 (遇到阻塞时如何报告)

---

## 🎯 核心目标 (一句话总结)

修复TypeScript类型错误，创建数据适配层，并实现Web页面与真实API的集成，为用户提供完整的Web界面体验。

**关键指标**:
- 修复262个TypeScript错误，目标<50
- 创建统一数据适配层
- 开发API客户端和React Query Hooks
- 实现3个核心页面的真实API集成
- 前端测试覆盖率>80%

---

## ✅ 立即行动清单

### Step 1: 确认任务理解 (T+0h)
- [ ] 阅读 `TASK.md` 全文
- [ ] 确认验收标准清晰且可达成
- [ ] 确认质量标准可达成
- [ ] 规划工作方式（使用哪些工具、如何组织组件）

### Step 2: 创建进度报告文档 (T+0h)
创建 `TASK-REPORT.md`，记录以下内容:
```markdown
# Frontend CLI 进度报告

**Worker CLI**: Frontend CLI
**Worktree**: /opt/claude/mystocks_phase7_frontend
**Branch**: phase7-frontend-web-integration

---

## 当前状态
- 当前阶段: 阶段1 - TypeScript类型修复
- 当前任务: T1.1 - TypeScript类型错误修复
- 总体进度: 0/32 小时 (0%)
- 最后更新: 2025-12-30 [时间]

## 任务理解确认
- ✅ 已阅读TASK.md全文
- ✅ 理解核心职责和验收标准
- ✅ 规划工作方式

## 下一步行动
1. 分析TypeScript错误类型
2. 创建类型声明文件（如klinecharts.d.ts）

## 问题与阻塞
无

## 更新日志
- 2025-12-30: 任务初始化，开始执行
```

### Step 3: 开始执行第一阶段 (T+0h ~ T+8h)
按照 `TASK.md` 中的任务清单，开始执行**阶段1: TypeScript类型修复**。

---

## 📅 第一次检查点

**时间**: T+2h (2025-12-30 2小时后)
**检查内容**:
1. TASK-REPORT.md已创建且包含必要信息
2. 已开始执行T1.1任务（TypeScript错误分析）
3. 遇到的问题已记录在TASK-REPORT.md中

**请准备**: 在T+2h时，主CLI将查看你的TASK-REPORT.md，确认你已正确理解任务并开始执行。

---

## 🚀 开始执行

请开始独立执行任务。按照TASK.md中的指引，完成每个阶段的任务。

**重要原则**:
- ✅ **独立执行**: 按照TASK.md自主完成任务
- ✅ **主动报告**: 每2小时更新TASK-REPORT.md
- ✅ **用户体验优先**: 功能正确 + 体验流畅
- ✅ **及时沟通**: 遇到阻塞立即报告（使用问题报告机制）

**遇到阻塞问题时**:
- 🟡 警告级（类型错误、组件警告）: 尝试解决1小时，未解决报告
- 🔴 阻塞级（页面无法加载、API无法调用）: 15分钟内报告

报告格式参考 `TASK.md` 中的"问题报告机制"章节。

---

**工具提示**:
- Vue 3.4+: 前端框架
- TypeScript 5+: 类型系统
- Vite 5+: 构建工具
- Axios: HTTP客户端
- React Query: 数据管理

**权限范围**:
- ✅ `web/frontend/src/` - 完全控制
- ✅ `web/frontend/src/api/` - 完全控制（API客户端）
- ✅ `web/frontend/src/hooks/` - 完全控制（数据Hooks）
- ✅ `web/frontend/src/utils/` - 完全控制（适配器）
- ⚠️ `web/backend/` - 只读（了解API响应格式）
- ⚠️ `docs/api/` - 只读（参考API文档）

---

**祝执行顺利！** 🎯

**Main CLI (Manager)**
2025-12-30

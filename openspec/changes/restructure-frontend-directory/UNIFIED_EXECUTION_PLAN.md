# restructure-frontend-directory – 统一执行计划

**状态**: ✅ Phase 0 完成，Phase 1 准备就绪
**日期**: 2026-03-02
**负责人**: 当前团队（接管自前一个团队）
**变更ID**: `restructure-frontend-directory`

---

## 📋 执行摘要

### 已完成
- ✅ OpenSpec 变更包创建、验证、提交
- ✅ Phase 0 门禁实现（pre-commit 冻结）
- ✅ 进度追踪初始化
- ✅ 交接文档提交

### 当前状态
- 🔄 Phase 1（治理与审批）– 准备就绪，等待架构委员会签字
- ⏳ Phase 2-9（实现）– 等待 Phase 1 完成

### 关键提交
| 提交 | 消息 | 内容 |
|------|------|------|
| `5720f4d1` | spec(frontend): add restructure frontend directory proposal | OpenSpec 变更包 |
| `e827beff` | chore(frontend): enforce views migration gate for restructure phase0 | Phase 0 门禁 |
| `656f2b3d` | docs: add handoff document for restructure-frontend-directory | 交接文档 |

---

## 🎯 Phase 1 – 治理与审批（1-2 天）

### 目标
获得架构委员会的明确批准，为 Phase 2 实施做准备。

### 执行步骤

#### 步骤 1: 通知架构委员会
```
收件人: 架构主管、前端主管、安全审查员
主题: restructure-frontend-directory – 等待审批

内容:
- 变更ID: restructure-frontend-directory
- 文档位置: openspec/changes/restructure-frontend-directory/
- 关键文件:
  - proposal.md – 问题陈述与解决方案
  - design.md – 技术决策与风险评估
  - tasks.md – 19 个阶段的实施计划
  - specs/frontend-structure/spec.md – 需求规范

- 请求:
  1. 架构主管: 评论 "APPROVED" 确认设计
  2. 前端主管: 评论 "APPROVED" 确认可行性
  3. 安全审查: 评论 "APPROVED" 或 "NO SECURITY CONCERNS"

- 预期工作量: 26 人天（≈ 3.5 周）
- 风险等级: 中等（协调文件移动、导入重写、路由变更）
```

#### 步骤 2: 收集审批
- [ ] 架构主管签字
- [ ] 前端主管签字
- [ ] 安全审查完成

#### 步骤 3: 更新进度文档
```bash
# 编辑 tasks.md，标记 Phase 1 完成
# 编辑 MIGRATION_PROGRESS.md，记录审批结果

git add openspec/changes/restructure-frontend-directory/tasks.md
git add openspec/changes/restructure-frontend-directory/MIGRATION_PROGRESS.md
git commit -m "docs: record Phase 1 approvals from Architecture Board"
git push origin main
```

#### 步骤 4: 验证准备
```bash
# 确保 Phase 0 门禁仍然有效
python scripts/hooks/check-views-migration-table.py

# 验证 OpenSpec 变更包
openspec validate restructure-frontend-directory --strict
```

---

## 🚀 Phase 2 – 共享资产提取（3 天）

**前置条件**: Phase 1 审批已完成 ✅

### 目标
将分散的共享资产（components、composables）整理到统一的 `src/shared/` 位置。

### 执行步骤

#### 步骤 1: 创建隔离工作区
```bash
git worktree add .worktrees/phase2-shared-extraction -b phase2-shared-extraction-v2
cd .worktrees/phase2-shared-extraction-v2
```

#### 步骤 2: 盘点共享资产
```bash
# 列出所有 composables
find web/frontend/src -type f -name "*.ts" -path "*/composables/*" | sort > /tmp/composables.txt

# 列出所有 components
find web/frontend/src -type f -name "*.vue" -path "*/components/*" | sort > /tmp/components.txt

# 统计
echo "Composables: $(wc -l < /tmp/composables.txt)"
echo "Components: $(wc -l < /tmp/components.txt)"
```

#### 步骤 3: 创建目标目录
```bash
mkdir -p src/shared/components
mkdir -p src/shared/composables
mkdir -p src/shared/styles
```

#### 步骤 4: 移动全局 composables
```bash
# 移动 src/composables/* 到 src/shared/composables/
git mv src/composables/* src/shared/composables/ 2>/dev/null || true

# 验证
npm run lint
npm run type-check
```

#### 步骤 5: 移动共享组件
```bash
# 移动 src/components/shared/* 到 src/shared/components/
git mv src/components/shared/* src/shared/components/ 2>/dev/null || true

# 验证
npm run lint
npm run type-check
```

#### 步骤 6: 更新导入路径
```bash
# 从 @/composables/ 改为 @/shared/composables/
find web/frontend/src -type f \( -name "*.vue" -o -name "*.ts" \) \
  -exec sed -i 's|@/composables/|@/shared/composables/|g' {} \;

# 从 @/components/ 改为 @/shared/components/
find web/frontend/src -type f \( -name "*.vue" -o -name "*.ts" \) \
  -exec sed -i 's|@/components/|@/shared/components/|g' {} \;

# 验证
npm run lint
npm run type-check
```

#### 步骤 7: 运行完整验证
```bash
# 烟雾测试
npm run test:smoke

# E2E 测试
npm run test:e2e

# 开发服务器
npm run dev  # 验证应用启动
```

#### 步骤 8: 提交
```bash
git commit -m "refactor: extract shared assets to src/shared/

- Move src/composables/* to src/shared/composables/
- Move src/components/shared/* to src/shared/components/
- Update all import paths to use @/shared/ prefix
- Verify with lint, type-check, smoke tests, and E2E tests

Co-Authored-By: restructure-frontend-directory team"

git push origin phase2-shared-extraction-v2
```

---

## 📊 完整时间表

| 阶段 | 持续时间 | 状态 | 关键活动 |
|------|---------|------|---------|
| **Phase 0** – 冻结与规划 | 1 天 | ✅ 完成 | 门禁实现、进度追踪 |
| **Phase 1** – 治理与审批 | 1-2 天 | 🔄 进行中 | 收集签字、更新进度 |
| **Phase 2** – 共享资产提取 | 3 天 | ⏳ 待命 | 移动资产、更新导入 |
| **Phase 3** – 页面迁移（7 域） | 7 天 | ⏳ 待命 | 按域迁移页面 |
| **Phase 4** – 路由与布局 | 2 天 | ⏳ 待命 | 更新路由配置 |
| **Phase 5** – 测试 | 2 天 | ⏳ 待命 | 烟雾测试、E2E 测试 |
| **Phase 6** – 代码审查 | 1 天 | ⏳ 待命 | 架构审查、安全审查 |
| **Phase 7** – 合并与部署 | 1 天 | ⏳ 待命 | 合并到 main、部署 |
| **Phase 8** – 部署后验证 | 1 天 | ⏳ 待命 | 验证 staging、归档变更 |
| **Phase 9** – 清理与验证 | 1 天 | ⏳ 待命 | 最终检查、文档更新 |
| **总计** | **≈ 3.5 周** | | |

---

## ✅ 安全恢复清单

在开始任何工作前，请确认：

- [ ] 运行 `git status` 确认工作区干净
- [ ] 运行 `openspec validate restructure-frontend-directory --strict` 验证变更包
- [ ] 确认 Phase 1 审批已明确记录
- [ ] 确认 Phase 0 门禁仍然有效
- [ ] 不在 Phase 1 完成前开始 Phase 2

---

## 📚 关键文档

| 文档 | 位置 | 用途 |
|------|------|------|
| **提案** | `openspec/changes/restructure-frontend-directory/proposal.md` | 问题陈述、解决方案、影响 |
| **任务** | `openspec/changes/restructure-frontend-directory/tasks.md` | 19 个阶段的实施清单 |
| **设计** | `openspec/changes/restructure-frontend-directory/design.md` | 技术决策、风险评估 |
| **规范** | `openspec/changes/restructure-frontend-directory/specs/frontend-structure/spec.md` | 需求规范 |
| **交接** | `openspec/changes/restructure-frontend-directory/HANDOFF_2026-03-02.md` | 前一个团队的交接 |
| **进度** | `openspec/changes/restructure-frontend-directory/MIGRATION_PROGRESS.md` | 实时进度追踪 |
| **治理** | `docs/reports/reviews/PHASE1_GOVERNANCE_APPROVAL.md` | 审批清单 |

---

## 🎯 成功标准

### Phase 1 完成标志
- ✅ 架构主管评论 "APPROVED"
- ✅ 前端主管评论 "APPROVED"
- ✅ 安全审查完成
- ✅ `tasks.md` 中 Phase 1 项目标记为完成
- ✅ `MIGRATION_PROGRESS.md` 更新

### Phase 2 完成标志
- ✅ 所有共享资产移动到 `src/shared/`
- ✅ 所有导入路径更新为 `@/shared/...`
- ✅ `npm run lint` 通过
- ✅ `npm run type-check` 通过
- ✅ `npm run test:smoke` 通过
- ✅ `npm run test:e2e` 通过
- ✅ `npm run dev` 应用正常启动

---

## 🚨 风险与缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| 导入路径过时 | 构建失败 | 中 | 每次移动后运行 lint & type-check |
| 路由表不同步 | 导航 404 | 中 | 验证每个文件都在路由配置中 |
| 重复合并错误 | 功能丢失 | 低 | 为每个重复创建检查清单 |
| 烟雾测试不完整 | 回归漏过 | 低 | 扩展覆盖范围、运行 E2E 测试 |
| Staging 部署失败 | 需要回滚 | 低 | 本地测试、运行完整 CI 后再合并 |

---

## 📞 联系与支持

- **架构问题**: 参考 `design.md`
- **实施问题**: 参考 `tasks.md`
- **规范问题**: 参考 `specs/frontend-structure/spec.md`
- **进度追踪**: 更新 `MIGRATION_PROGRESS.md`

---

**准备好开始 Phase 1 了吗？** 🚀

下一步: 通知架构委员会并收集审批。

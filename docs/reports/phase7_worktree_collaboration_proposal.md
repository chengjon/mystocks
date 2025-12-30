# Phase 7: 209 API契约与Web集成 - Worktree协作方案

**文档版本**: v2.0 (基于MULTI_CLI methodology v2.0)
**创建者**: Main CLI (Manager)
**创建时间**: 2025-12-30
**更新时间**: 2025-12-30
**基于**: Phase 6实战经验 + Worktree管理指南 v2.0
**目标**: 完成 `web/backend/IMPLEMENTATION_GUIDE.md` 中的12周实施计划

**核心更新** (v2.0):
- ✅ 采用TASK.md + TASK-REPORT.md分离策略（避免README.md冲突）
- ✅ 集成10个Prompt策略模板（高效沟通）
- ✅ 使用结构化Worker CLI报告模板
- ✅ 多阶段任务管理（TASK-X.md格式）

---

## 📊 执行摘要

### 项目背景

MyStocks项目需要完成**209个API端点**的契约标准化、测试覆盖和Web集成：

| 模块 | API数量 | 优先级 | 当前状态 |
|------|--------|--------|----------|
| 行情数据 | 40+ | P0 | Hybrid数据源 |
| 策略管理 | 50+ | P0 | Hybrid数据源 |
| 交易委托 | 30+ | P0 | Mock数据 |
| 用户账户 | 25+ | P1 | Real数据 |
| 技术指标 | 35+ | P1 | Real数据 |
| 系统配置 | 29+ | P2 | Mock数据 |

**当前挑战**:
- 🔴 262个TypeScript错误（类型安全不足）
- 🔴 仅5% API契约覆盖率
- 🟡 仅4个契约注册（market-data, trading, technical-analysis, strategy-management）
- 🟡 前端使用Mock数据，未对接真实API

### 协作方案概览

**核心团队**: 3个Worker CLI + 1个Main CLI（我）

**目标**: 12周实施计划，通过多CLI并行开发节省**~50%时间**

**关键成功因素**（基于Phase 6经验）:
- ✅ **"指导但不代替"** - Main CLI提供指导，Worker CLIs独立执行
- ✅ **Git Worktree隔离** - 真正的并行开发，零上下文切换开销
- ✅ **定期进度监控** - 每小时检查，及时发现阻塞问题
- ✅ **质量不妥协** - 速度和质量兼得（E2E测试100%通过）

---

## 🎯 角色定义与职责分配

### 角色架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Main CLI (Coordinator)                   │
│  - 项目规划与进度监控                                          │
│  - Worktree创建与管理                                         │
│  - 问题协调与解决支持                                         │
│  - 集成与最终验证                                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │  Backend CLI    │  │   Test CLI      │  │ Frontend CLI │ │
│  │  (后端开发工程师) │  │  (测试工程师)    │  │(前端开发工程师)│ │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────┤ │
│  │ • API契约开发    │  │ • Playwright测试│  │ • Web集成     │ │
│  │ • PM2服务管理   │  │ • tmux环境搭建   │  │ • 数据适配层   │ │
│  │ • 路由扫描      │  │ • lnav日志分析   │  │ • Vue组件开发  │ │
│  │ • FastAPI实现   │  │ • 契约验证       │  │ • TypeScript  │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 角色详细说明

#### 1. Backend CLI (后端开发工程师)

**Worktree命名**: `phase7-backend-contracts`
**分配分支**: `phase7-backend-api-contracts`
**预计工作量**: 48小时（6周 × 8小时/周）

**核心职责**:

1. **API契约标准化** (Phase 1-2, 4-5周)
   - 扫描209个API端点，生成OpenAPI规范
   - 创建契约注册模板（YAML格式）
   - 定义核心字段：api_id, module, path, method, request_params, response_code, response_data
   - 注册所有API到契约管理系统

2. **PM2服务管理** (贯穿全程)
   - 编写PM2 ecosystem配置
   - 启动/重启API服务：`pm2 restart mystocks-api`
   - 监控服务状态：`pm2 monit`
   - 收集服务日志：`pm2 logs`

3. **路由扫描与文档生成**
   - 批量扫描FastAPI路由
   - 生成API目录（catalog.yaml + catalog.md）
   - 验证API文档完整性

4. **API实现与修复** (按优先级)
   - P0: market, strategy, trading (30 APIs)
   - P1: backtest, risk (25 APIs)
   - P2: indicators, announcement (40 APIs)

**工具链**:
- PM2 (进程管理)
- FastAPI (API框架)
- Pydantic (数据验证)
- Python 3.12+

**验收标准**:
- [ ] 209个API全部扫描并生成契约模板
- [ ] 115个API完成注册（P0+P1优先级）
- [ ] API文档100%覆盖（catalog.yaml + catalog.md）
- [ ] PM2服务稳定运行（无崩溃）

**权限范围**:
- ✅ `web/backend/` - 完全控制
- ✅ `config/data_sources.json` - 修改数据源配置
- ⚠️ `web/frontend/` - 只读（了解接口定义）
- ⚠️ `docs/api/` - 协调修改（需要Main CLI批准）

---

#### 2. Test CLI (测试工程师)

**Worktree命名**: `phase7-test-automation`
**分配分支**: `phase7-test-contracts-automation`
**预计工作量**: 40小时（5周 × 8小时/周）

**核心职责**:

1. **tmux测试环境搭建** (Week 1)
   - 创建4窗口tmux会话：API监控 / Web服务 / 日志 / 测试
   - 配置窗口布局：`even-horizontal`
   - 自动化启动脚本：`scripts/start-system.sh --tmux`

2. **Playwright契约测试** (Phase 2-3, Week 3-5)
   - API契约一致性测试（209个端点）
   - 响应结构验证
   - 错误码测试（200, 20101等）
   - 目标：60% API测试覆盖率

3. **lnav日志分析** (贯穿全程)
   - 实时日志筛选：`:filter-in ERROR`
   - 按模块分析：`:filter-in path=/api/market/`
   - 导出分析结果：`:write-to /tmp/api_analysis.txt`
   - 错误追踪和性能瓶颈识别

4. **E2E测试框架** (Phase 4, Week 6-12)
   - 用户流程测试（20-30个用例）
   - 关键业务场景验证
   - 性能测试（响应时间、吞吐量）

**工具链**:
- Playwright (测试框架)
- tmux (多窗口管理)
- lnav (日志分析)
- pytest (测试运行器)

**验收标准**:
- [ ] tmux测试环境自动化（一键启动）
- [ ] 209个API契约测试套件创建
- [ ] 115个已注册API测试覆盖（60%覆盖率）
- [ ] E2E测试20-30个用例，100%通过
- [ ] lnav日志分析报告生成

**权限范围**:
- ✅ `tests/api/` - 完全控制（契约测试）
- ✅ `tests/e2e/` - 完全控制（E2E测试）
- ✅ `scripts/start-system.sh` - 修改启动脚本
- ⚠️ `web/backend/` - 只读（了解API端点）
- ⚠️ `web/frontend/` - 只读（了解页面流程）

---

#### 3. Frontend CLI (前端开发工程师)

**Worktree命名**: `phase7-frontend-integration`
**分配分支**: `phase7-frontend-web-integration`
**预计工作量**: 32小时（4周 × 8小时/周）

**核心职责**:

1. **TypeScript类型修复** (Phase 4, Week 1-2)
   - 修复262个TypeScript错误 → 目标 <50
   - ECharts类型标准化
   - Element Plus兼容性
   - 创建类型声明文件（如klinecharts.d.ts）

2. **数据适配层开发** (Phase 4, Week 3)
   - 创建 `src/utils/dataAdapter.ts`
   - 定义标准数据格式（StandardKLine等）
   - API响应数据转换
   - 优雅降级机制（API失败 → Mock数据）

3. **API客户端与Hooks** (Phase 5, Week 4-6)
   - Axios客户端配置：`src/api/client.ts`
   - 请求/响应拦截器
   - React Query Hooks：`src/hooks/useMarketData.ts`
   - 错误处理和重试逻辑

4. **Web页面集成** (Phase 5, Week 7-12)
   - 替换Mock数据为真实API调用
   - 分3批渐进式切换：
     - Week 7: 核心页面（Market, Trading）
     - Week 8-10: 功能页面（Strategy, Backtest）
     - Week 11-12: 配置页面（Settings, Admin）

**工具链**:
- Vue 3.4+ (前端框架)
- TypeScript 5+ (类型系统)
- Vite 5+ (构建工具)
- Axios (HTTP客户端)
- React Query (数据管理)

**验收标准**:
- [ ] TypeScript错误：262 → <50
- [ ] 数据适配层创建（5+个适配函数）
- [ ] 3个核心页面集成真实API（Market, Trading, Strategy）
- [ ] 前端测试覆盖率 >80%

**权限范围**:
- ✅ `web/frontend/src/` - 完全控制
- ✅ `web/frontend/src/api/` - 完全控制（API客户端）
- ✅ `web/frontend/src/hooks/` - 完全控制（数据Hooks）
- ✅ `web/frontend/src/utils/` - 完全控制（适配器）
- ⚠️ `web/backend/` - 只读（了解API响应格式）
- ⚠️ `docs/api/` - 只读（参考API文档）

---

#### 4. Main CLI (我 - Project Coordinator)

**工作位置**: 主仓库 `/opt/claude/mystocks_spec`
**角色**: Manager & Coordinator
**工作时间**: 贯穿12周（平均2小时/天）

**核心职责**:

1. **项目规划与Worktree创建** (Week 1前)
   - 任务拆分与工作量估算
   - 创建3个worktree
   - 编写README任务文档
   - 建立自动化监控脚本

2. **进度监控** (贯穿全程)
   - 每小时检查所有worktree状态
   - 每2小时生成结构化报告
   - 里程碑检查：T+2h, T+6h, T+8h（每周）
   - 动态优先级调整

3. **问题协调** (响应式)
   - 🟢 信息级：4h内处理
   - 🟡 警告级：1h内处理
   - 🔴 阻塞级：15min内处理
   - 提供解决方案文档，不直接修改代码

4. **集成与验证** (每周里程碑)
   - 验证所有交付物完整性
   - 按依赖顺序合并分支
   - 运行E2E测试验证
   - 生成完成报告

5. **文档与知识管理**
   - 更新项目文档
   - 归档工作产物
   - 总结经验教训

**工具链**:
- Git (版本控制)
- tmux (监控会话管理)
- Markdown (文档编写)
- Bash (自动化脚本)

**关键原则**（基于Phase 6经验）:
- ✅ **"指导但不代替"** - 提供3次迭代指导文档，让Worker CLIs自己执行
- ✅ **最小化沟通开销** - 不主动干预，仅在阻塞时介入
- ✅ **优先级优化** - 识别瓶颈，动态调整任务顺序
- ✅ **质量保证** - E2E测试100%通过，Pylint 9.0+/10

**权限范围**:
- ✅ 全部worktree：读+写权限（但仅监控，不主动修改）
- ✅ 主仓库：读+写+合并权限
- ✅ Git操作：全部权限（create, merge, push, delete）

---

## 📝 任务文档管理策略 (v2.0核心改进)

### 核心原则：任务与进度报告分离

**问题** (Phase 6经验教训):
- ❌ 多个CLI同时修改README.md → Git合并冲突
- ❌ 任务说明和进度混在一起 → 难以追踪
- ❌ 主CLI需要手动从README提取进度 → 效率低

**解决方案** (v2.0方法):
- ✅ **TASK.md**: 主CLI创建，任务说明（只读，Worker CLI不修改）
- ✅ **TASK-REPORT.md**: Worker CLI创建，进度报告（定期更新）
- ✅ **TASK-*-REPORT.md**: Worker CLI创建，阶段完成报告
- ✅ **README.md**: 项目概览（不变，避免冲突）

### 文件组织架构

```
/opt/claude/mystocks_phase7_backend/
├── README.md              # 项目概览（Main CLI创建，只读）
├── TASK.md                # 任务说明（Main CLI创建，只读）
├── TASK-REPORT.md         # 进度报告（Worker CLI维护）
├── TASK-1-REPORT.md       # 第1阶段完成报告
├── TASK-2-REPORT.md       # 第2阶段完成报告
└── ...
```

### Main CLI工作流程

**阶段1: 任务分配** (T+0h)
```bash
# 为每个CLI创建TASK.md
cd /opt/claude/mystocks_phase7_backend
cat > TASK.md << 'EOF'
# Backend CLI 任务文档

**Worker CLI**: Backend CLI (API契约开发)
**Branch**: phase7-backend-api-contracts
**Worktree**: /opt/claude/mystocks_phase7_backend
**预计工作量**: 48小时（6周）
**完成标准**: 209个API契约标准化完成

## 🎯 核心职责
...
EOF
```

**阶段2: 进度监控** (T+2h, T+4h, ...)
```bash
# 检查Worker CLI的进度报告
cd /opt/claude/mystocks_phase7_backend
cat TASK-REPORT.md

# 检查Git状态
git log --oneline -5
git status --short | wc -l
```

**阶段3: 阶段验收** (T+2周, T+3周, ...)
```bash
# 验证TASK-X-REPORT.md
cd /opt/claude/mystocks_phase7_backend
cat TASK-1-REPORT.md

# 运行验收测试
pytest tests/api/ -v

# 合并分支
git checkout main
git merge phase7-backend-api-contracts --no-ff --no-edit
```

### Worker CLI工作流程

**阶段1: 理解任务** (T+0h ~ T+0.5h)
```bash
# 1. 阅读TASK.md
cd /opt/claude/mystocks_phase7_backend
cat TASK.md

# 2. 确认验收标准清晰
# 3. 规划工作方式
# 4. 开始执行
```

**阶段2: 进度报告** (每2小时)
```bash
# 更新TASK-REPORT.md
cat > TASK-REPORT.md << 'EOF'
# Backend CLI 任务进度报告

**当前阶段**: T+4h
**报告时间**: 2025-12-30 14:00

## ✅ 已完成
- [x] T1.1: API目录扫描 - 完成时间: 2025-12-30 12:00
- [x] T1.2: catalog.yaml生成

## 🔄 进行中
- [ ] T1.3: 契约模板创建 - 当前进度: 60%

## 📈 进度统计
- 已完成任务: 2/3 (67%)
- 实际用时: 4小时（预计3小时，延迟1小时）
EOF

git add TASK-REPORT.md
git commit -m "docs: 更新进度到T+4h (67%完成)"
```

**阶段3: 阶段完成** (每个阶段结束时)
```bash
# 生成完成报告
cat > TASK-1-REPORT.md << 'EOF'
# 任务完成报告 - 第1阶段：API契约模板

**完成时间**: 2025-12-30 18:00

## ✅ 验收标准
- [x] 209个API契约模板创建完成
- [x] catalog.yaml生成完成

## 📦 交付物
- `docs/api/catalog.yaml` - API目录
- `contracts/` - 209个契约模板

## 🧪 测试结果
- 契约验证测试: 209/209 PASSED (100%)
EOF

git add TASK-1-REPORT.md
git commit -m "docs: 第1阶段完成报告"
```

### 多阶段任务管理

**阶段切换流程**:

```bash
# ============================================
# Main CLI: 阶段1完成，下发阶段2任务
# ============================================
cd /opt/claude/mystocks_phase7_backend

# 1. 标记阶段1完成
mv TASK.md TASK-1.md

# 2. 下发阶段2任务
cat > TASK-2.md << 'EOF'
# Backend CLI 第2阶段任务：API实现

**阶段**: Phase 2
**本阶段预计工作量**: 16小时（2周）
**总体预计工作量**: 48小时（6周）

## 🎯 本阶段核心职责
实现30个P0优先级API端点
EOF

# 3. 通知Worker CLI开始阶段2
# (Worker CLI会读取TASK-2.md)
```

### 相关文档

- **[TASK_TEMPLATE.md](../docs/guides/multi-cli-tasks/TASK_TEMPLATE.md)** - 完整模板参考
- **[MULTI_CLI_PROMPT_STRATEGIES.md](../docs/guides/MULTI_CLI_PROMPT_STRATEGIES.md)** - Prompt策略

---

## 🎤 Prompt策略模板 (v2.0新增)

### 核心原则

1. **Documentation > Dialogue** - 结构化文档 > 冗长对话
2. **Guidance > Instructions** - 提供目标 > 指定方法
3. **Active Reporting > Passive Checking** - 主动报告 > 被动检查
4. **Structured Feedback > Vague Evaluation** - 结构化反馈 > 模糊评价

### 10个Prompt模板

#### 模板1: 初始化任务Prompt（T+0h）

```markdown
# Worker CLI-X 任务初始化

## 📋 任务文档
位置: TASK.md

## 🎯 核心目标
[一句话描述核心目标]

## ✅ 立即行动
1. 阅读 TASK.md
2. 确认验收标准清晰
3. 规划工作方式
4. 记录任务理解确认

## 📅 第一次检查点
时间: T+2h
内容: 准备T+2h进度汇报

## 🚀 开始执行
请开始独立执行任务，遇到阻塞问题及时报告。
```

#### 模板2: 进度检查Prompt（T+2h, T+4h, ...）

```markdown
# Worker CLI-X 进度检查

## 📊 当前进度
时间: T+Xh
预计完成: T+Yh

## ✅ 请汇报
1. 已完成任务清单
2. 进行中任务及进度百分比
3. 阻塞问题（如有）

## 📈 请生成
更新 TASK-REPORT.md 并提交

## 🚧 有阻塞问题吗？
🟢 信息级: 下次检查处理
🟡 警告级: 1h内处理
🔴 阻塞级: 15min内处理
```

#### 模板3: 阶段完成Prompt（T+2周, T+3周, ...）

```markdown
# Worker CLI-X 阶段验收

## ✅ 验收标准
[列出本阶段所有验收标准]

## 📦 请提交
1. TASK-X-REPORT.md（完成报告）
2. 代码提交记录
3. 测试结果

## 🧪 验证测试
[列出需要运行的测试命令]

## ✅ 下一步
等待主CLI验收和下一阶段任务
```

#### 模板4: 阻塞问题解决Prompt

```markdown
# Worker CLI-X 阻塞问题解决方案

## 问题
[清晰的标题]

## 级别
🔴 阻塞级 / 🟡 警告级 / 🟢 信息级

## 分析
[根因分析]

## 解决方案
[具体解决方案，不直接修改代码]

## 执行步骤
1. 步骤1: [具体操作]
   产出物: [期望结果]
2. 步骤2: [具体操作]
   产出物: [期望结果]

## 验证方法
[如何验证问题已解决]

---
*请按照此指导独立完成修复，主CLI提供指导但不代替执行。*
```

#### 模板5: 优先级调整Prompt

```markdown
# Worker CLI-X 优先级调整通知

## 📊 当前状态
- 已完成: X个任务
- 进行中: Y个任务
- 剩余: Z个任务

## 🔄 优先级调整
**原顺序**: [旧顺序]
**新顺序**: [新顺序]
**原因**: [调整原因]

## ⏭️ 请立即关注
[新的高优先级任务]

## 📝 已暂停任务
[被暂停的任务列表，后续继续]
```

#### 模板6: 里程碑验收Prompt

```markdown
# Phase X 里程碑验收

## ✅ 验收清单
- [ ] Backend CLI: [验收项]
- [ ] Test CLI: [验收项]
- [ ] Frontend CLI: [验收项]

## 🧪 集成测试
[测试命令]

## 📊 质量指标
- Pylint评级: X/10
- TypeScript错误: Y个
- E2E测试通过率: Z%

## 🚀 下一阶段
[Phase X+1概要]
```

#### 模板7: 代码审查反馈Prompt

```markdown
# Worker CLI-X 代码审查反馈

## ✅ 做得好的地方
1. [具体优点]
2. [具体优点]

## ⚠️ 需要改进的地方
1. [问题1]: [具体建议]
2. [问题2]: [具体建议]

## 📝 改进优先级
- 🔴 P0: [必须修复]
- 🟡 P1: [建议修复]
- 🟢 P2: [可选优化]

## ⏰ 预期修复时间
T+Xh内完成并提交

## ✅ 修复后验证
[验证方法]
```

#### 模板8: Git合并指导Prompt

```markdown
# Phase X 分支合并指导

## 📋 合并清单
- [ ] 所有验收标准通过
- [ ] 测试套件100%通过
- [ ] 代码已提交到远程分支

## 🔀 合并顺序
1. [Branch-1] (依赖最少)
2. [Branch-2] (依赖Branch-1)
3. [Branch-3] (依赖Branch-2)

## 🧪 合并后验证
[验证命令]

## 📦 合并后清理
- [ ] 删除worktree
- [ ] 删除本地分支
- [ ] 删除远程分支
```

#### 模板9: 阶段总结Prompt

```markdown
# Phase X 阶段总结报告

## 📊 总体成果
- 时间跨度: X周
- 实际用时: Y小时
- 效率提升: Z%

## ✅ 完成情况
- Backend CLI: [完成率]
- Test CLI: [完成率]
- Frontend CLI: [完成率]

## 📈 质量指标
| 指标 | Phase X前 | Phase X后 | 改进 |
|------|----------|-----------|------|
| [指标1] | X | Y | Z% |
| [指标2] | X | Y | Z% |

## 💡 经验教训
1. [经验1]
2. [经验2]

## 🚀 下一步
[Phase X+1概要]
```

#### 模板10: 项目完成Prompt

```markdown
# Phase 7 项目完成报告

## 🎉 项目成功完成！

**开始时间**: YYYY-MM-DD
**完成时间**: YYYY-MM-DD
**总用时**: X周 / Y小时

## ✅ 最终成果
- API契约覆盖率: 5% → 60% (+1100%)
- TypeScript错误: 262 → <50 (-80%)
- E2E测试通过率: 100%
- 代码质量: Pylint 9.0+/10

## 📦 交付物清单
- [ ] 209个API契约
- [ ] 115个已注册API
- [ ] 60% API测试覆盖率
- [ ] 3个核心页面Web集成
- [ ] E2E测试套件
- [ ] 完整文档

## 💡 核心经验
1. "指导但不代替" - [量化结果]
2. Git Worktree - [量化结果]
3. 进度监控 - [量化结果]
4. 质量保证 - [量化结果]

## 🙏 致谢
感谢所有Worker CLIs的辛勤工作！

---
*项目文档已归档，准备进入下一阶段。*
```

### Prompt使用指南

**何时使用哪个模板**:

| 场景 | 使用模板 | 频率 |
|------|---------|------|
| 任务开始 | 模板1 | 1次/阶段 |
| 进度检查 | 模板2 | 每2小时 |
| 阶段完成 | 模板3 | 1次/阶段 |
| 阻塞问题 | 模板4 | 按需 |
| 优先级调整 | 模板5 | 按需 |
| 里程碑验收 | 模板6 | 每周 |
| 代码审查 | 模板7 | 按需 |
| Git合并 | 模板8 | 每周 |
| 阶段总结 | 模板9 | 每周 |
| 项目完成 | 模板10 | 1次 |

---

## 📅 实施路线图

### 12周时间线概览

```
Week 1-2: Phase 4 - TypeScript类型整理
├── Frontend CLI: TypeScript错误修复 (262 → ~150)
├── Backend CLI: API目录扫描与契约模板生成
└── Test CLI: tmux环境搭建

Week 3: Phase 4.3-4.5 - 契约对齐
├── Backend CLI: 209个API契约标准化
├── Frontend CLI: 契约类型对齐、适配层创建
└── Test CLI: Playwright测试框架配置

Week 4-5: Phase 5 - 契约测试
├── Test CLI: 4个已注册API契约测试
├── Backend CLI: P0 API实现（30个）
└── Frontend CLI: 数据适配层开发

Week 6: Phase 6 - 开发者体验
├── Backend CLI: Pre-commit hooks配置
├── Frontend CLI: 代码生成器开发
└── Test CLI: 一键契约测试脚本

Week 7-12: Phase 7 - 完整API注册与Web集成
├── Backend CLI: 115个API注册（P0+P1）
├── Frontend CLI: Web页面分批集成
└── Test CLI: E2E测试与CI/CD集成
```

### 每周里程碑与验收标准

#### Week 1-2: TypeScript类型修复

| CLI | 任务 | 交付物 | 验收标准 |
|-----|------|--------|----------|
| Frontend | 修复262个TS错误 | 错误日志、类型声明文件 | 错误 → <150 |
| Backend | API目录扫描 | catalog.yaml, catalog.md | 209个API清单 |
| Test | tmux环境搭建 | start-system.sh --tmux | 一键启动成功 |

**Main CLI检查点**（T+2周）:
- [ ] Frontend CLI完成类型修复目标
- [ ] Backend CLI生成完整API目录
- [ ] Test CLI演示tmux环境启动
- [ ] 生成第2周进度报告

#### Week 3: 契约对齐

| CLI | 任务 | 交付物 | 验收标准 |
|-----|------|--------|----------|
| Backend | 209个API契约模板 | YAML契约文件 | 模板100%覆盖 |
| Frontend | 契约类型对齐 | TypeScript类型 | 前后端类型一致 |
| Test | Playwright配置 | playwright.config.ts | 测试框架就绪 |

**Main CLI检查点**（T+3周）:
- [ ] 契约模板创建完成
- [ ] 前后端类型对齐验证
- [ ] Playwright测试框架配置完成
- [ ] 生成第3周进度报告

#### Week 4-5: 契约测试与P0实现

| CLI | 任务 | 交付物 | 验收标准 |
|-----|------|--------|----------|
| Test | 4个已注册API测试 | 测试套件 | 100%通过 |
| Backend | P0 API实现（30个） | FastAPI端点 | 功能测试通过 |
| Frontend | 数据适配层 | dataAdapter.ts | 5+个适配函数 |

**Main CLI检查点**（T+5周）:
- [ ] 4个已注册API测试覆盖
- [ ] P0 API实现完成
- [ ] 数据适配层创建
- [ ] 生成第5周进度报告

#### Week 7-12: 完整集成

**批次切换计划**（渐进式）:

| 周次 | 切换页面 | API数量 | 验收方式 |
|------|---------|---------|----------|
| Week 7 | Market, Trading | 20 | E2E测试 |
| Week 8-10 | Strategy, Backtest | 40 | 功能测试 |
| Week 11-12 | Settings, Admin | 20 | 回归测试 |

**Main CLI检查点**（每周）:
- [ ] 该批次页面集成完成
- [ ] E2E测试通过
- [ ] 性能指标达标
- [ ] 生成周进度报告

---

## 🛠️ 工具链整合

### PM2 + tmux + lnav + Playwright 自动化测试环境

#### 1. PM2生态系统配置

**文件位置**: `web/backend/ecosystem.config.js`

```javascript
module.exports = {
  apps: [
    {
      name: 'mystocks-api',
      script: 'uvicorn',
      args: 'app.main:app --host 0.0.0.0 --port 8000',
      cwd: '/opt/claude/mystocks_spec/web/backend',
      interpreter: 'python',
      instances: 2,
      exec_mode: 'cluster',
      env: {
        PYTHONPATH: '/opt/claude/mystocks_spec/web/backend'
      },
      watch: false,
      max_memory_restart: '500M',
      log_file: '/opt/claude/mystocks_spec/logs/api.log',
      error_file: '/opt/claude/mystocks_spec/logs/api_error.log',
      merge_logs: true,
      autorestart: true
    }
  ]
};
```

**Backend CLI使用PM2**:
```bash
# 启动API服务
pm2 start ecosystem.config.js

# 监控服务状态
pm2 monit

# 查看日志
pm2 logs mystocks-api

# 重启服务（代码更新后）
pm2 restart mystocks-api

# 停止服务
pm2 stop mystocks-api
```

#### 2. tmux测试会话配置

**文件位置**: `scripts/start-system.sh`（Test CLI创建）

```bash
#!/bin/bash
# 创建测试会话

tmux new-session -d -s "mystocks-test"

# 窗口 0: API服务监控（PM2）
tmux rename-window -t "mystocks-test:0" 'API'
tmux send-keys -t "mystocks-test:0" "cd /opt/claude/mystocks_spec/web/backend" Enter
tmux send-keys -t "mystocks-test:0" "pm2 monit" Enter

# 窗口 1: Web服务（Vite Dev Server）
tmux new-window -t "mystocks-test" -n 'Web'
tmux send-keys -t "mystocks-test:1" "cd /opt/claude/mystocks_spec/web/frontend" Enter
tmux send-keys -t "mystocks-test:1" "npm run dev" Enter

# 窗口 2: 日志监控（lnav）
tmux new-window -t "mystocks-test" -n 'Logs'
tmux send-keys -t "mystocks-test:2" "lnav -q /opt/claude/mystocks_spec/logs/" Enter

# 窗口 3: 测试执行
tmux new-window -t "mystocks-test" -n 'Test'
tmux send-keys -t "mystocks-test:3" "cd /opt/claude/mystocks_spec" Enter

# 布局
tmux select-layout -t "mystocks-test" even-horizontal

# 附加会话
tmux attach-session -t "mystocks-test"
```

**使用方法**:
```bash
# 一键启动测试环境
bash scripts/start-system.sh --tmux

# 快捷键（tmux内）
# Ctrl+b c: 创建新窗口
# Ctrl+b n: 下一个窗口
# Ctrl+b p: 上一个窗口
# Ctrl+b 0-3: 切换到窗口0-3
```

#### 3. lnav日志分析

**Test CLI使用lnav**:
```bash
# 启动lnav日志分析
lnav -q /opt/claude/mystocks_spec/logs/

# 筛选错误日志
:filter-in ERROR

# 按API路径筛选
:filter-in path=/api/market/

# 导出分析结果
:write-to /tmp/api_analysis.txt

# 实时统计
:show-stats

# 退出
:quit
```

**日志监控脚本**（Test CLI创建）:
```bash
#!/bin/bash
# scripts/monitor_api_logs.sh

# 实时监控API错误
tail -f /opt/claude/mystocks_spec/logs/api.log | \
  grep --line-buffered -E "ERROR|WARN" | \
  while read line; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $line"
  done
```

#### 4. Playwright测试配置

**文件位置**: `web/backend/tests/playwright.config.ts`

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/api',
  fullyParallel: true,
  retries: 2,
  reporter: 'html',

  use: {
    baseURL: 'http://localhost:8000',
    trace: 'on-first-retry',
  },

  projects: [
    {
      name: 'API',
      use: { ...devices['Desktop Chrome'], api: true },
      testMatch: /tests\/api\/.*\.ts/,
    },
    {
      name: 'E2E',
      use: devices['Desktop Chrome'],
      testMatch: /tests\/e2e\/.*\.ts/,
    },
  ],
});
```

**Test CLI运行测试**:
```bash
# API契约测试
pytest tests/api/test_contract_consistency.py -v

# 全量API测试
pytest tests/api/ --api-base-url=http://localhost:8000 -v

# E2E测试
pytest tests/e2e/ -v

# 生成报告
pytest tests/api/ --html=playwright-report/api/test_report.html
```

---

## 📋 Worktree创建与任务分配

### 步骤1: 主CLI创建3个Worktree（T+0h）

```bash
# ============================================
# 确保主分支最新
# ============================================
cd /opt/claude/mystocks_spec
git checkout main
git pull origin main

# ============================================
# 创建Backend CLI Worktree
# ============================================
git worktree add /opt/claude/mystocks_phase7_backend phase7-backend-api-contracts

# ============================================
# 创建Test CLI Worktree
# ============================================
git worktree add /opt/claude/mystocks_phase7_test phase7-test-contracts-automation

# ============================================
# 创建Frontend CLI Worktree
# ============================================
git worktree add /opt/claude/mystocks_phase7_frontend phase7-frontend-web-integration

# ============================================
# 验证Worktree创建成功
# ============================================
git worktree list

# 期望输出:
# /opt/claude/mystocks_spec                    abcd1234 [main]
# /opt/claude/mystocks_phase7_backend           5678abcd [phase7-backend-api-contracts]
# /opt/claude/mystocks_phase7_test              1234ef56 [phase7-test-contracts-automation]
# /opt/claude/mystocks_phase7_frontend          9f0e1a2b [phase7-frontend-web-integration]
```

### 步骤2: 为每个Worker CLI创建README

#### Backend CLI README模板

**文件**: `/opt/claude/mystocks_phase7_backend/README.md`

```markdown
# Phase 7: Backend API契约与实现

**分配给**: Backend CLI (后端开发工程师)
**分配时间**: 2025-12-30
**主CLI**: Claude Code (Manager)
**分支**: phase7-backend-api-contracts
**预计工作量**: 48小时（6周 × 8小时/周）

---

## 任务目标

完成209个API端点的契约标准化、文档生成和P0/P1优先级实现，确保API契约与Web前端无缝对接。

## 背景

MyStocks项目当前有209个API端点，但仅4个完成契约注册。需要系统性地扫描、文档化和注册所有API，为前端集成和自动化测试奠定基础。

## 验收标准

### Week 1-2: API目录扫描
- [ ] 扫描所有209个API端点
- [ ] 生成API目录：docs/api/catalog.yaml
- [ ] 生成API文档：docs/api/catalog.md
- [ ] 验证API文档完整性（100%覆盖）

### Week 3: API契约标准化
- [ ] 创建209个API契约模板（YAML格式）
- [ ] 定义核心字段：api_id, module, path, method, request_params, response_code, response_data
- [ ] 契约模板100%覆盖所有端点

### Week 4-5: P0 API实现（30个）
- [ ] 实现market模块API（10个）
- [ ] 实现strategy模块API（10个）
- [ ] 实现trading模块API（10个）
- [ ] 功能测试通过率 = 100%

### Week 6-12: P1/P2 API实现（85个）
- [ ] 注册115个API到契约管理系统
- [ ] PM2服务稳定运行（无崩溃）
- [ ] API文档100%覆盖

## 工作范围

### 本worktree范围内
- ✅ `web/backend/app/api/` - API路由和端点
- ✅ `web/backend/app/services/` - 业务逻辑服务
- ✅ `docs/api/` - API文档和契约
- ✅ `config/data_sources.json` - 数据源配置
- ✅ `ecosystem.config.js` - PM2配置

### 超出本worktree范围（需要请示主CLI）
- ⚠️ `web/frontend/` - 前端代码（仅可读取接口定义）
- ⚠️ `tests/` - 测试代码（Test CLI负责）
- ⚠️ 修改数据库schema（需要主CLI协调）

## 优先级
- 🔴 高（最高优先级，API契约是整个Phase 7的基础）

## 预计工作量
- 总计: 48小时
- Week 1-2: API扫描与文档（8小时）
- Week 3: 契约标准化（8小时）
- Week 4-5: P0实现（16小时）
- Week 6-12: P1/P2实现（16小时）

## 预计完成时间
T+6周（从现在开始计算）

## 工具链
- **PM2**: 进程管理（启动/重启/监控API服务）
- **FastAPI**: API框架
- **Pydantic**: 数据验证
- **Python**: 3.12+

## PM2使用指南

### 启动API服务
```bash
cd /opt/claude/mystocks_spec/web/backend
pm2 start ecosystem.config.js
```

### 监控服务状态
```bash
pm2 monit
```

### 查看日志
```bash
pm2 logs mystocks-api
```

### 重启服务（代码更新后）
```bash
pm2 restart mystocks-api
```

## 问题请示流程
如果遇到以下情况，请向主CLI请示：
1. 需要修改前端代码以适配API接口
2. 需要调整数据库schema
3. PM2服务无法启动或持续崩溃
4. API契约格式不统一，需要协调标准

## 进度更新

### T+0h（任务开始）
- 状态: 任务理解中
- 进度: 0%

---

**任务分配信息**
- 分配给: Backend CLI
- 分配时间: 2025-12-30
- 主CLI: Claude Code (Manager)
- 项目: MyStocks Phase 7
```

#### Test CLI README模板

**文件**: `/opt/claude/mystocks_phase7_test/README.md`

```markdown
# Phase 7: API契约测试与自动化

**分配给**: Test CLI (测试工程师)
**分配时间**: 2025-12-30
**主CLI**: Claude Code (Manager)
**分支**: phase7-test-contracts-automation
**预计工作量**: 40小时（5周 × 8小时/周）

---

## 任务目标

搭建完整的自动化测试环境，实现API契约测试（60%覆盖率）和E2E测试（20-30个用例），确保前后端集成质量。

## 背景

当前项目测试覆盖率仅5%，缺乏自动化测试框架。需要搭建tmux+lnav+Playwright环境，实现契约驱动测试。

## 验收标准

### Week 1: tmux环境搭建
- [ ] 创建tmux测试会话脚本（`scripts/start-system.sh --tmux`）
- [ ] 配置4个窗口：API监控 / Web服务 / 日志 / 测试
- [ ] 验证一键启动成功

### Week 2-3: Playwright配置
- [ ] 安装Playwright和浏览器驱动
- [ ] 配置playwright.config.ts
- [ ] 创建测试框架结构（tests/api/, tests/e2e/）

### Week 4-5: API契约测试
- [ ] 创建209个API契约测试用例
- [ ] 4个已注册API测试覆盖（100%通过）
- [ ] 目标：60% API契约测试覆盖率

### Week 6-12: E2E测试
- [ ] 创建20-30个E2E测试用例
- [ ] 覆盖关键业务流程
- [ ] 测试通过率 = 100%

## 工作范围

### 本worktree范围内
- ✅ `tests/api/` - API契约测试
- ✅ `tests/e2e/` - E2E测试
- ✅ `scripts/start-system.sh` - 测试环境启动脚本
- ✅ `web/backend/tests/playwright.config.ts` - Playwright配置

### 超出本worktree范围（需要请示主CLI）
- ⚠️ `web/backend/app/api/` - 后端代码（仅可读取API定义）
- ⚠️ `web/frontend/src/` - 前端代码（仅可了解页面流程）
- ⚠️ 修改API契约（需要Backend CLI协调）

## 优先级
- 🔴 高（测试质量保障）

## 预计工作量
- 总计: 40小时
- Week 1: tmux环境搭建（8小时）
- Week 2-3: Playwright配置（8小时）
- Week 4-5: API契约测试（16小时）
- Week 6-12: E2E测试（8小时）

## 预计完成时间
T+5周（从现在开始计算）

## 工具链

### tmux（多窗口管理）
```bash
# 创建测试会话
tmux new-session -d -s "mystocks-test"

# 窗口0: API服务监控
tmux rename-window -t "mystocks-test:0" 'API'
tmux send-keys -t "mystocks-test:0" "pm2 monit" Enter

# 窗口1: Web服务
tmux new-window -t "mystocks-test" -n 'Web'
tmux send-keys -t "mystocks-test:1" "npm run dev" Enter

# 窗口2: 日志监控
tmux new-window -t "mystocks-test" -n 'Logs'
tmux send-keys -t "mystocks-test:2" "lnav -q /opt/claude/mystocks_spec/logs/" Enter

# 窗口3: 测试执行
tmux new-window -t "mystocks-test" -n 'Test'

# 布局
tmux select-layout -t "mystocks-test" even-horizontal
```

### lnav（日志分析）
```bash
# 启动lnav
lnav -q /opt/claude/mystocks_spec/logs/

# 筛选错误
:filter-in ERROR

# 按API路径筛选
:filter-in path=/api/market/

# 导出分析结果
:write-to /tmp/api_analysis.txt
```

### Playwright（测试框架）
```bash
# API契约测试
pytest tests/api/test_contract_consistency.py -v

# 全量API测试
pytest tests/api/ --api-base-url=http://localhost:8000 -v

# E2E测试
pytest tests/e2e/ -v

# 生成报告
pytest tests/api/ --html=playwright-report/api/test_report.html
```

## 问题请示流程
如果遇到以下情况，请向主CLI请示：
1. API契约定义不清晰，无法编写测试
2. 测试环境无法启动（PM2/tmux/lnav问题）
3. 发现API接口bug，需要Backend CLI修复
4. 需要调整测试优先级

## 进度更新

### T+0h（任务开始）
- 状态: 任务理解中
- 进度: 0%

---

**任务分配信息**
- 分配给: Test CLI
- 分配时间: 2025-12-30
- 主CLI: Claude Code (Manager)
- 项目: MyStocks Phase 7
```

#### Frontend CLI README模板

**文件**: `/opt/claude/mystocks_phase7_frontend/README.md`

```markdown
# Phase 7: Web前端集成

**分配给**: Frontend CLI (前端开发工程师)
**分配时间**: 2025-12-30
**主CLI**: Claude Code (Manager)
**分支**: phase7-frontend-web-integration
**预计工作量**: 32小时（4周 × 8小时/周）

---

## 任务目标

修复TypeScript类型错误，创建数据适配层，分批将Web页面从Mock数据切换到真实API，实现前后端完整集成。

## 背景

当前前端使用Mock数据，存在262个TypeScript错误。需要系统性地修复类型问题、创建适配层、对接真实API。

## 验收标准

### Week 1-2: TypeScript类型修复
- [ ] 修复TypeScript错误：262 → <50
- [ ] ECharts类型标准化
- [ ] Element Plus兼容性
- [ ] 创建类型声明文件（如klinecharts.d.ts）

### Week 3: 数据适配层
- [ ] 创建 `src/utils/dataAdapter.ts`
- [ ] 创建5+个适配函数（adaptKlineData等）
- [ ] 实现优雅降级机制（API失败 → Mock数据）
- [ ] 单元测试覆盖率 >80%

### Week 4: API客户端与Hooks
- [ ] 创建Axios客户端：`src/api/client.ts`
- [ ] 配置请求/响应拦截器
- [ ] 创建React Query Hooks：`src/hooks/useMarketData.ts`
- [ ] 错误处理和重试逻辑

### Week 5-12: Web页面集成
- [ ] Week 7: 核心页面集成（Market, Trading）- 20个API
- [ ] Week 8-10: 功能页面集成（Strategy, Backtest）- 40个API
- [ ] Week 11-12: 配置页面集成（Settings, Admin）- 20个API
- [ ] E2E测试通过率 = 100%

## 工作范围

### 本worktree范围内
- ✅ `web/frontend/src/` - 完全控制
- ✅ `web/frontend/src/api/` - API客户端
- ✅ `web/frontend/src/hooks/` - 数据Hooks
- ✅ `web/frontend/src/utils/` - 数据适配器

### 超出本worktree范围（需要请示主CLI）
- ⚠️ `web/backend/app/api/` - 后端代码（仅可读取API响应格式）
- ⚠️ `docs/api/` - API文档（仅可参考）
- ⚠️ 修改API契约（需要Backend CLI协调）

## 优先级
- 🔴 高（前端集成是用户体验的关键）

## 预计工作量
- 总计: 32小时
- Week 1-2: TypeScript修复（8小时）
- Week 3: 数据适配层（8小时）
- Week 4: API客户端（8小时）
- Week 5-12: Web页面集成（8小时）

## 预计完成时间
T+4周（从现在开始计算）

## 工具链
- **Vue 3.4+**: 前端框架
- **TypeScript 5+**: 类型系统
- **Vite 5+**: 构建工具
- **Axios**: HTTP客户端
- **React Query**: 数据管理

## 技术方案

### 数据适配层示例

```typescript
// src/utils/dataAdapter.ts
export interface StandardKLine {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export function adaptKlineData(apiData: any): StandardKLine[] {
  if (!apiData?.kline) return [];

  return apiData.kline.map((item: any) => ({
    timestamp: item.timestamp,
    open: Number(item.open),
    high: Number(item.high),
    low: Number(item.low),
    close: Number(item.close),
    volume: Number(item.volume)
  }));
}

// 优雅降级
export async function getKlineWithFallback(symbol: string, period: string) {
  try {
    const response = await apiClient.get('/api/market/kline', {
      params: { symbol, period }
    });
    return adaptKlineData(response.data);
  } catch (error) {
    console.warn('API 失败，降级到 Mock 数据');
    return getMockKlineData(symbol, period);
  }
}
```

### API客户端示例

```typescript
// src/api/client.ts
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
```

## 问题请示流程
如果遇到以下情况，请向主CLI请示：
1. API契约定义与前端需求不匹配
2. API响应格式无法适配
3. 需要Backend CLI调整API接口
4. TypeScript类型定义需要后端配合

## 进度更新

### T+0h（任务开始）
- 状态: 任务理解中
- 进度: 0%

---

**任务分配信息**
- 分配给: Frontend CLI
- 分配时间: 2025-12-30
- 主CLI: Claude Code (Manager)
- 项目: MyStocks Phase 7
```

---

## 🔄 协作流程与沟通机制

### 定期进度监控

**Main CLI监控频率**:
- **每小时**: 检查所有worktree状态（最新提交、未提交修改、分支状态）
- **每2小时**: 生成结构化进度报告
- **每周**: 里程碑验证（T+2周, T+3周, T+5周, T+6周, T+12周）

**监控命令**:
```bash
# 检查所有worktree
git worktree list

# 检查Backend CLI进度
cd /opt/claude/mystocks_phase7_backend
git log --oneline -5
git status --short | wc -l

# 检查Test CLI进度
cd /opt/claude/mystocks_phase7_test
git log --oneline -5
git status --short | wc -l

# 检查Frontend CLI进度
cd /opt/claude/mystocks_phase7_frontend
git log --oneline -5
git status --short | wc -l
```

### 进度报告模板

**Main CLI每2小时生成一次**:

```markdown
# Phase 7 多CLI协作进度报告（第N小时）

**生成时间**: YYYY-MM-DD HH:MM
**报告人**: Main CLI
**当前阶段**: T+Xh状态检查

---

## 📊 总体进度概览

### 完成率
- **已完成**: X/N 个Worker CLI（X%）
- **进行中**: Y/N 个Worker CLI（Y%）
- **总体进度**: ~W%（加权平均）

---

## 🔄 Worker CLI 当前状态

### ✅ Backend CLI: API契约开发
**状态**: 进行中 (~X% 进度)
**预计完成**: T+6周
**最新提交**: `<commit-sha> - <commit-message>`

**当前工作证据** (X个文件已修改):
```
web/backend/docs/api/catalog.yaml - 已创建
web/backend/docs/api/catalog.md - 已生成
```

**进度评估**: [按计划进行 / 提前 / 延迟]

---

### ✅ Test CLI: 自动化测试
**状态**: 进行中 (~X% 进度)
**预计完成**: T+5周

[同上格式]

---

### ✅ Frontend CLI: Web集成
**状态**: 进行中 (~X% 进度)
**预计完成**: T+4周

[同上格式]

---

## ⚠️ 风险和问题

### 当前风险
（列出阻塞问题和风险）

---

## 🚀 下一阶段行动计划

### 立即行动 (T+Xh → T+Yh)
**Main CLI任务**:
1. ✅ 生成当前进度报告
2. 🔍 持续监控Worker CLI进度
3. 🚨 支持阻塞的Worker CLI

---

**下次更新**: T+Yh（约X小时后）
```

### 问题级别与响应时间

| 级别 | 定义 | 示例 | Main CLI响应时间 |
|------|------|------|--------------|
| 🟢 信息级 | 不影响工作的小问题 | 代码风格建议、文档不完整 | 下次定期检查（4h内） |
| 🟡 警告级 | 可能影响进度 | 依赖版本冲突、测试偶尔失败 | 4小时内 |
| 🔴 阻塞级 | 完全无法继续工作 | PM2服务启动失败、API契约冲突 | 立即（15min内） |

### 请示流程

**Worker CLI → Main CLI**:
```markdown
## 请示主CLI协助

**时间**: YYYY-MM-DD HH:MM
**级别**: 🔴 阻塞级 / 🟡 警告级 / 🟢 信息级

### 问题描述
[清晰描述问题]

### 影响范围
- 本worktree: [影响描述]
- 其他worktree: [如果影响其他worktree]
- 整体进度: [对整体进度的影响]

### 已尝试的解决方案
1. [尝试1]: [结果]
2. [尝试2]: [结果]

### 请求协助
- [需要主CLI做什么]
- [期望的响应时间]

### 附件
- [相关文件路径]
- [错误日志路径]
```

**Main CLI → Worker CLI** (提供解决方案文档):
```markdown
# Worker CLI-X 问题解决方案

## 问题
[清晰的标题]

## 级别
🔴 阻塞级 / 🟡 警告级 / 🟢 信息级

## 解决方案
[具体的解决方案]

## 执行步骤
1. **步骤1**: [具体操作]
   ```bash
   [命令或操作]
   ```
   产出物: [期望的结果]

2. **步骤2**: [具体操作]
   产出物: [期望的结果]

## 验证方法
[如何验证问题已解决]

## 下一步
Worker CLI: [具体需要执行的操作]
Main CLI: [是否需要持续跟踪]

---

*请按照此指导独立完成修复，不要请求主CLI执行这些步骤。*
*主CLI的角色是提供指导，Worker CLI负责执行。*
```

### Git协作规范

**提交信息格式**（HEREDOC标准化）:
```bash
git commit -m "$(cat <<'EOF'
type(scope): description

Detailed explanation...

🤖 Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

**分支合并策略**（Main CLI在里程碑时执行）:
```bash
# 切换到main分支
git checkout main
git pull origin main

# 按依赖顺序合并
git merge phase7-frontend-web-integration --no-ff --no-edit
git merge phase7-test-contracts-automation --no-ff --no-edit
git merge phase7-backend-api-contracts --no-ff --no-edit

# 推送到远程
git push origin main
```

---

## 📈 成功指标与验收标准

### 总体成功指标

| 指标 | 当前（Phase 7前） | Phase 7后目标 | 改进 |
|------|-----------------|---------------|------|
| **TypeScript错误** | 262个 | <50个 | -80% |
| **API契约覆盖率** | 5% | 60% | +1100% |
| **已注册API** | 4个 | 115个 | +2775% |
| **API测试覆盖率** | 0% | 60% | +60% |
| **E2E测试通过率** | - | 100% | 完美 |
| **类型安全** | ~40% | >95% | +137% |

### 分阶段验收标准

#### Week 1-2验收
- [ ] Frontend CLI: TypeScript错误 262 → <150
- [ ] Backend CLI: 209个API扫描完成，catalog.yaml生成
- [ ] Test CLI: tmux环境一键启动成功

#### Week 3验收
- [ ] Backend CLI: 209个API契约模板创建
- [ ] Frontend CLI: 前后端类型对齐验证通过
- [ ] Test CLI: Playwright测试框架配置完成

#### Week 4-5验收
- [ ] Test CLI: 4个已注册API测试覆盖（100%通过）
- [ ] Backend CLI: P0 API实现完成（30个）
- [ ] Frontend CLI: 数据适配层创建

#### Week 6-12验收（每周）
- [ ] 该批次页面集成完成
- [ ] E2E测试通过
- [ ] 性能指标达标

---

## 💡 基于Phase 6经验的关键策略

### 成功经验1: "指导但不代替"的力量

**深度体验**（Phase 6 CLI-2案例）:
- CLI-2遇到13个语法错误，阻塞了3小时
- Main CLI提供3次迭代指导文档（T+1h, T+3h, T+5h）
- CLI-2独立修复所有错误，提前3.1小时完成

**本次应用**:
- ✅ Main CLI不直接修改Worker CLI的代码
- ✅ 提供详细的问题解决方案文档
- ✅ 让Worker CLIs自己执行修复
- ✅ 培养Worker CLIs的独立能力

### 成功经验2: Git Worktree是并行开发的完美基础设施

**深度体验**（Phase 6数据）:
- 4个CLI同时工作在4个独立领域
- 0个Git冲突或文件覆盖问题
- 真正的并行开发，无需stash或频繁切换分支

**本次应用**:
- ✅ 3个worktree完全隔离
- ✅ Backend CLI: `web/backend/app/api/`
- ✅ Test CLI: `tests/`
- ✅ Frontend CLI: `web/frontend/src/`
- ✅ 文件所有权清晰，最小化沟通开销

### 成功经验3: 进度监控 = 项目成功

**深度体验**（Phase 6监控数据）:
- CLI-2阻塞3小时未被发现 → 问题发现延迟
- 建立自动化监控后 → 问题发现时间-66.7%
- 响应时间从3小时降至1小时

**本次应用**:
- ✅ Main CLI每小时检查进度
- ✅ 每2小时生成结构化报告
- ✅ 设置里程碑：每周（T+2周, T+3周等）
- ✅ 优先级优化（动态调整任务顺序）

### 成功经验4: 质量保证不能妥协

**深度体验**（Phase 6质量指标）:
- E2E测试: 18/18 PASSED (100%)
- Pylint评级: 9.32/10（提升+0.42）
- 并行开发 + 质量保证 = 更快 + 更好

**本次应用**:
- ✅ Playwright契约测试（60%覆盖率）
- ✅ E2E测试（20-30个用例，100%通过）
- ✅ TypeScript类型检查（错误 <50）
- ✅ lnav日志分析（自动化错误检测）

### 成功经验5: 优先级优化的杠杆效应

**深度体验**（Phase 6 CLI-2案例）:
- 投入: 1.5小时（分析+指导文档）
- 产出: 节省3.1小时
- 杠杆率: 206.7%

**本次应用**:
- ✅ 识别关键路径：Backend API契约 → Frontend集成 → E2E测试
- ✅ 优先级调整：API契约标准化优先于完整实现
- ✅ 渐进式切换：核心页面优先于配置页面

---

## 🚀 立即行动计划

### Main CLI立即执行（T+0h）

1. **创建3个worktree**
   ```bash
   git worktree add /opt/claude/mystocks_phase7_backend phase7-backend-api-contracts
   git worktree add /opt/claude/mystocks_phase7_test phase7-test-contracts-automation
   git worktree add /opt/claude/mystocks_phase7_frontend phase7-frontend-web-integration
   ```

2. **为每个CLI创建TASK.md** (使用新v2.0模板)
   ```bash
   # Backend CLI
   cd /opt/claude/mystocks_phase7_backend
   cat > TASK.md << 'EOF'
   # Backend CLI 任务文档

   **Worker CLI**: Backend CLI (API契约开发)
   **Branch**: phase7-backend-api-contracts
   **Worktree**: /opt/claude/mystocks_phase7_backend
   **预计工作量**: 48小时（6周）
   **完成标准**: 209个API契约标准化完成

   ## 🎯 核心职责
   ...

   ## 📋 任务清单
   ...

   ## 📊 进度跟踪
   **当前状态**: 🔄 待开始
   EOF

   # Test CLI
   cd /opt/claude/mystocks_phase7_test
   cat > TASK.md << 'EOF'
   # Test CLI 任务文档
   ...
   EOF

   # Frontend CLI
   cd /opt/claude/mystocks_phase7_frontend
   cat > TASK.md << 'EOF'
   # Frontend CLI 任务文档
   ...
   EOF
   ```

3. **建立自动化监控脚本**
   ```bash
   # scripts/monitor_phase7_progress.sh
   # 每小时检查所有worktree的TASK-REPORT.md
   # 每2小时生成结构化进度报告
   ```

4. **使用模板1向Worker CLIs发送任务初始化Prompt**
   ```bash
   # 参考上面的"模板1: 初始化任务Prompt"
   ```

5. **约定首次检查时间**（T+2h）

### Worker CLIs立即执行（T+0h ~ T+0.5h）

1. **阅读并理解TASK.md**
2. **确认验收标准清晰**
3. **规划工作方式**
4. **记录任务理解确认** (可选: 创建TASK-REPORT.md初始版本)
5. **开始独立执行任务**

### T+2h第一次进度检查

**Main CLI**:
```bash
# 使用"模板2: 进度检查Prompt"
# 检查每个CLI的TASK-REPORT.md
cd /opt/claude/mystocks_phase7_backend && cat TASK-REPORT.md
cd /opt/claude/mystocks_phase7_test && cat TASK-REPORT.md
cd /opt/claude/mystocks_phase7_frontend && cat TASK-REPORT.md
```

**Worker CLIs**:
```bash
# 更新TASK-REPORT.md
cd /opt/claude/mystocks_phase7_backend
cat > TASK-REPORT.md << 'EOF'
# Backend CLI 任务进度报告

**当前阶段**: T+2h
**报告时间**: 2025-12-30 XX:00

## ✅ 已完成
- [x] 任务理解确认

## 🔄 进行中
- [ ] [第一个任务]

## 📈 进度统计
- 已完成任务: 0/X (0%)
EOF

git add TASK-REPORT.md
git commit -m "docs: T+2h进度报告"
```

---

## 📝 附录

### 相关文档 (v2.0方法论)

**核心指导文档**:
- **[MULTI_CLI_WORKTREE_MANAGEMENT.md](../docs/guides/MULTI_CLI_WORKTREE_MANAGEMENT.md)** ⭐ - Version 2.0 完整工作指南 (2735行)
- **[MULTI_CLI_PROMPT_STRATEGIES.md](../docs/guides/MULTI_CLI_PROMPT_STRATEGIES.md)** - Prompt策略与10个模板 (1328行)
- **[MULTI_CLI_MAIN_CLI_LESSONS_LEARNED.md](../docs/guides/MULTI_CLI_MAIN_CLI_LESSONS_LEARNED.md)** - Phase 6经验总结 (861行)
- **[TASK_TEMPLATE.md](../docs/guides/multi-cli-tasks/TASK_TEMPLATE.md)** - 任务文档模板 (692行)

**Phase 7实施文档**:
- **[IMPLEMENTATION_GUIDE.md](../web/backend/IMPLEMENTATION_GUIDE.md)** - 209 API完整实施指南
- **[PHASE6_FINAL_COMPLETION_REPORT.md](../reports/PHASE6_FINAL_COMPLETION_REPORT.md)** - Phase 6完成报告

**质量保证文档**:
- **[PYTHON_QUALITY_ASSURANCE_WORKFLOW.md](../docs/guides/PYTHON_QUALITY_ASSURANCE_WORKFLOW.md)** - Python质量保证流程
- **[FILE_ORGANIZATION_RULES.md](../docs/standards/FILE_ORGANIZATION_RULES.md)** - 文件组织规范

### Git命令速查

**创建worktree**:
```bash
git worktree add <路径> <分支名>
```

**检查worktree状态**:
```bash
git worktree list
cd <worktree_path>
git log --oneline -5
git status --short | wc -l
```

**删除worktree**:
```bash
git worktree remove <路径>
git branch -d <分支名>
```

**合并分支**:
```bash
git checkout main
git merge <branch_name> --no-ff -m "Merge message"
```

### PM2命令速查

```bash
pm2 start ecosystem.config.js    # 启动服务
pm2 monit                          # 监控状态
pm2 logs <app_name>                # 查看日志
pm2 restart <app_name>             # 重启服务
pm2 stop <app_name>                # 停止服务
```

### tmux命令速查

```bash
tmux new-session -d -s "name"     # 创建会话
tmux rename-window -t "name:0" 'API' # 重命名窗口
tmux send-keys -t "name:0" "cmd" Enter # 发送命令
tmux select-layout -t "name" even-horizontal # 布局
tmux attach-session -t "name"      # 附加会话
```

### Playwright命令速查

```bash
pytest tests/api/ -v               # API测试
pytest tests/e2e/ -v               # E2E测试
pytest tests/ --html=report.html   # 生成报告
```

---

**文档版本**: v2.0 (基于MULTI_CLI methodology v2.0)
**创建时间**: 2025-12-30
**更新时间**: 2025-12-30
**创建者**: Main CLI (Manager)
**基于**:
- Phase 6实战经验 (65.5%时间节省)
- MULTI_CLI_WORKTREE_MANAGEMENT.md v2.0 (2735行完整指南)
- MULTI_CLI_PROMPT_STRATEGIES.md (10个Prompt模板)
- TASK_TEMPLATE.md (结构化任务文档)

**v2.0核心改进**:
- ✅ TASK.md + TASK-REPORT.md分离策略（避免README.md冲突）
- ✅ 10个Prompt策略模板（高效沟通）
- ✅ 结构化Worker CLI报告（TASK-REPORT.md, TASK-*-REPORT.md）
- ✅ 多阶段任务管理（TASK-X.md格式）
- ✅ "指导但不代替"原则（Phase 6验证）

---

*🚀 准备就绪，等待执行！*
*3个核心角色，12周实施计划，209个API端点，让我们一起完成这个挑战！*
*基于Phase 6验证的方法论，预期节省50%+开发时间！*

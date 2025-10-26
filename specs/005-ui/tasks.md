# Tasks: UI系统改进 - 字体系统、问财查询、自选股重构

**Feature**: 005-ui
**Input**: Design documents from `/specs/005-ui/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Note**: Tests are optional for this feature (UI improvements focus on manual testing)

---

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 ✅ 前端开发服务器已运行 (http://localhost:3000)
- [x] T002 ✅ Vue 3 + Element Plus 项目已初始化
- [x] T003 ✅ ESLint + Prettier 已配置

**Status**: Setup完成 ✅

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### 数据库修复 (阻塞US3)

- [ ] T004 🔴 [BLOCKING] 添加watchlist_groups.category字段到数据库
  - 文件: `database/migrations/add_category_to_watchlist_groups.sql`
  - SQL: `ALTER TABLE watchlist_groups ADD COLUMN category VARCHAR(20) DEFAULT 'user' NOT NULL;`
  - 验证: 执行后检查schema
  - **阻塞原因**: US3自选股需要category字段区分4个选项卡

### API服务层基础

- [ ] T005 [P] [Foundation] 创建问财API服务层封装
  - 文件: `web/frontend/src/api/wencai.js`
  - 功能: executeQuery, getResults, executeCustomQuery等方法
  - 依赖: axios, API_ENDPOINTS配置

- [ ] T006 [P] [Foundation] 创建自选股API服务层封装
  - 文件: `web/frontend/src/api/watchlist.js`
  - 功能: getAllWithGroups, getByGroup, addStock, removeStock等方法
  - 依赖: axios, API_ENDPOINTS配置

### 后端API增强

- [ ] T007 [P] [Foundation] 实现自选股按category查询端点
  - 文件: `web/backend/app/api/watchlist.py`
  - 新增: `GET /api/watchlist?category={user|system|strategy|monitor}`
  - 依赖: T004 (数据库迁移)

- [ ] T008 [P] [Foundation] 添加问财API限流和缓存机制
  - 文件: `web/backend/app/api/wencai.py`
  - 功能: fastapi_limiter (10次/分钟), lru_cache (5分钟)
  - 性能: 缓存命中率 >80%

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - 全局字体系统生效 (Priority: P1) 🎯 MVP

**Goal**: 用户可以在系统设置中调整字体大小，整个应用立即响应变化，设置持久化

**Independent Test**: 访问系统设置 → 选择字体大小 → 导航到其他页面验证字体变化 → 刷新页面验证持久化

### 实施任务

- [ ] T009 [P] [US1] 创建全局Typography样式文件
  - 文件: `web/frontend/src/assets/styles/typography.css`
  - 内容: CSS Variables定义 (--font-size-base, --font-size-helper等6个变量)
  - 规范: FR-001, FR-003, FR-004, FR-005

- [ ] T010 [US1] 在main.js中导入typography.css
  - 文件: `web/frontend/src/main.js`
  - 代码: `import './assets/styles/typography.css'`
  - 依赖: T009

- [ ] T011 [P] [US1] 增强FontSizeSetting组件的功能
  - 文件: `web/frontend/src/components/settings/FontSizeSetting.vue`
  - 修改:
    - handleFontSizeChange: 更新CSS Variables + LocalStorage
    - onMounted: 从LocalStorage恢复字体设置
  - 规范: FR-006, FR-007, FR-008

- [ ] T012 [P] [US1] 增强Pinia preferences store
  - 文件: `web/frontend/src/stores/preferences.js`
  - 新增: updatePreference, loadPreferences方法
  - 存储键: `preferences.fontSize`

### 验证任务

- [ ] T013 [P] [US1] 验证CSS Variables在Element Plus组件中生效
  - 方法: 浏览器DevTools检查el-button, el-table的computed styles
  - 预期: font-family和font-size继承CSS Variables
  - 规范: FR-001

- [ ] T014 [P] [US1] 跨浏览器兼容性测试
  - 浏览器: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
  - 验证: CSS Variables渲染一致性
  - 工具: BrowserStack或手动测试

- [ ] T015 [P] [US1] 验证LocalStorage持久化功能
  - 测试步骤:
    1. 设置字体为18px
    2. 检查LocalStorage['preferences.fontSize'] === '18px'
    3. 刷新页面
    4. 验证字体仍为18px
  - 规范: FR-007, FR-008

- [ ] T016 [US1] 验证字体切换的即时响应（无需刷新）
  - 测试: 切换字体大小 → 观察页面立即更新
  - 性能: 响应时间 <100ms
  - 规范: FR-006, SC-001

- [ ] T017 [US1] 检查所有页面组件正确使用CSS Variables
  - 文件范围: `web/frontend/src/components/**/*.vue`
  - 检查: 搜索hardcoded font-size，替换为CSS Variables
  - 工具: 全局搜索 "font-size: \\d+px"

- [ ] T018 [P] [US1] 响应式设计测试
  - 屏幕尺寸: 移动端(375px), 平板(768px), 桌面(1920px)
  - 验证: 字体在不同屏幕下可读性
  - 工具: 浏览器响应式模式

**Checkpoint**: User Story 1 完成 - 全局字体系统可独立验证 ✅

---

## Phase 4: User Story 2 - 问财筛选默认查询恢复 (Priority: P2)

**Goal**: 用户可以在问财筛选页面看到9个预设查询，点击查询快速获取结果并联动显示

**Independent Test**: 访问问财筛选页面 → 验证显示9个查询 → 点击任意查询 → 验证结果正确显示

### 实施任务

- [ ] T019 [US2] 替换WencaiPanel中的模拟数据为真实API调用
  - 文件: `web/frontend/src/components/market/WencaiPanelV2.vue`
  - 修改: executePresetQuery方法调用wencaiApi.executeQuery
  - 依赖: T005 (API服务层)
  - 规范: FR-011

- [ ] T020 [US2] 实现预设查询点击后的完整数据流
  - 文件: `web/frontend/src/components/market/WencaiPanelV2.vue`
  - 流程:
    1. 调用wencaiApi.executeQuery (触发后端抓取)
    2. 调用wencaiApi.getResults (获取结果)
    3. 处理结果并显示
  - 依赖: T019

- [ ] T021 [US2] 实现查询结果分页加载功能
  - 文件: `web/frontend/src/components/market/WencaiPanelV2.vue`
  - 功能: currentPage, pageSize, handlePageChange
  - 依赖: T020

- [ ] T022 [US2] 添加问财API错误处理和降级策略
  - 文件: `web/frontend/src/api/wencai.js`
  - 错误类型:
    - 400 → "查询参数无效"
    - 429 → "查询频率过高"
    - 500 → "服务器错误"
    - 网络错误 → "网络连接失败"
  - 降级: 显示Toast + 保留上次数据

- [ ] T023 [P] [US2] 验证9个预设查询的配置正确性
  - 文件: `web/frontend/src/config/wencaiQueries.js`
  - 检查: 9个查询对象 (qs_1 to qs_9)
  - 字段: id, name, description, query, category
  - 参考: `specs/005-ui/contracts/wencai-queries.json`

### 验证任务

- [ ] T024 [US2] 测试问财查询API契约
  - 端点: POST /api/market/wencai/query
  - 请求: { query_name: "qs_1", pages: 1 }
  - 响应验证:
    - ✓ success: boolean
    - ✓ total_records: number
    - ✓ timestamp: string (ISO 8601)
  - 依赖: T005, T008

- [ ] T025 [US2] 验证字段名称映射
  - 映射表:
    - 股票代码 → symbol
    - 股票简称 → name
    - 涨跌幅 → change_percent (去掉"%", 转number)
  - 测试: 执行查询后检查前端tableData格式

- [ ] T026 [US2] 测试自定义查询功能
  - 功能: 用户输入任意查询条件
  - 测试: 输入"市值大于100亿" → 执行 → 验证结果
  - 依赖: T020

- [ ] T027 [US2] 验证查询结果导出CSV功能
  - 按钮: "导出CSV"
  - 测试: 点击后下载CSV文件，检查数据完整性
  - 依赖: T020

- [ ] T028 [US2] 测试网络失败、超时等异常场景
  - 场景:
    1. 断网状态下执行查询
    2. API超时 (>5s)
    3. 后端返回500错误
  - 验证: 显示友好错误提示 + 界面保持可用
  - 依赖: T022

- [ ] T029 [US2] 性能测试
  - 指标: 查询响应时间 <1s (SC-004)
  - 测试: 执行10次查询，计算平均响应时间
  - 工具: console.time / Chrome DevTools Network

**Checkpoint**: User Story 2 完成 - 问财筛选功能可独立验证 ✅

---

## Phase 5: User Story 3 - 自选股页面重构为选项卡式布局 (Priority: P3)

**Goal**: 用户可以在自选股页面看到4个选项卡，切换查看不同分类，表格分组高亮显示

**Independent Test**: 访问自选股页面 → 验证4个选项卡 → 切换标签 → 验证表格固定表头 → 验证分组高亮 → 刷新页面验证状态持久化

### 前置条件验证

- [ ] T030 🔴 [US3] 验证数据库category字段已添加
  - 依赖: T004 (阻塞任务)
  - 验证: `SELECT category FROM watchlist_groups LIMIT 1;`
  - 预期: 返回 'user', 'system', 'strategy', 或 'monitor'

- [ ] T031 🔴 [US3] 验证后端category查询端点可用
  - 依赖: T007
  - 测试: `GET /api/watchlist?category=user`
  - 预期: 返回该分类的自选股列表

### 实施任务

- [ ] T032 [US3] 替换WatchlistTable中的模拟数据为真实API调用
  - 文件: `web/frontend/src/components/stock/WatchlistTable.vue`
  - 修改: loadData方法调用watchlistApi.getByGroup
  - 映射: tab名称 → 后端groupId (user→1, system→2, strategy→3, monitor→4)
  - 依赖: T006, T031

- [ ] T033 [US3] 实现分组高亮样式
  - 文件: `web/frontend/src/components/stock/WatchlistTable.vue`
  - 功能: getRowClassName方法根据group_name返回CSS类名
  - 样式: 6种颜色 (blue, green, orange, purple, cyan, red)
  - 规范: FR-016

- [ ] T034 [US3] 添加自选股增删改查错误处理
  - 文件: `web/frontend/src/api/watchlist.js`
  - 错误类型:
    - 400 → "股票已在自选股中"
    - 404 → "自选股不存在" / "分组不存在"
    - 500 → "服务器错误"
  - 降级: 显示Toast + 回滚UI

- [ ] T035 [P] [US3] 实现选项卡状态持久化
  - 文件: `web/frontend/src/components/stock/WatchlistTabs.vue`
  - 存储: LocalStorage['watchlist.activeTab']
  - 功能: onMounted恢复, handleTabChange保存
  - 规范: FR-019

- [ ] T036 [P] [US3] 优化后端分组查询性能
  - 文件: `web/backend/app/api/watchlist.py`
  - 优化: 使用joinedload减少N+1查询
  - 目标: 查询时间 <500ms (SC-005)
  - 依赖: T007

### 验证任务

- [ ] T037 [US3] 测试自选股API契约
  - 端点: GET /api/watchlist?category=user
  - 响应验证:
    - ✓ stocks: Array<{ symbol, name, group_name, ... }>
    - ✓ 字段完整性
  - 依赖: T031

- [ ] T038 [US3] 验证4个选项卡切换功能
  - 选项卡: 用户自选, 系统自选, 策略自选, 监控列表
  - 测试: 点击每个标签 → 验证加载对应数据
  - 依赖: T032

- [ ] T039 [US3] 测试选项卡状态持久化
  - 测试步骤:
    1. 切换到"策略自选"
    2. 刷新页面
    3. 验证仍停留在"策略自选"
  - 依赖: T035

- [ ] T040 [US3] 验证分组高亮样式显示效果
  - 测试: 查看表格，确认不同group_name有不同背景色
  - 验证: 6种颜色清晰区分
  - 依赖: T033

- [ ] T041 [US3] 测试添加股票到自选股功能
  - 操作: 点击"添加股票" → 输入symbol → 选择分组 → 确认
  - 验证: 表格刷新，新股票出现
  - 依赖: T032

- [ ] T042 [US3] 测试移除股票功能及确认对话框
  - 操作: 点击"移除" → 确认对话框 → 确认
  - 验证: 表格刷新，股票消失
  - 依赖: T032

- [ ] T043 [US3] 测试空列表状态
  - 场景: 某个分类无自选股
  - 验证: 显示el-empty组件 + 友好提示
  - 依赖: T032

- [ ] T044 [US3] 性能测试 (1000条数据)
  - 测试: 添加1000条自选股
  - 指标: 标签页切换 <200ms, 表格滚动流畅
  - 工具: Chrome DevTools Performance
  - 依赖: T036

**Checkpoint**: User Story 3 完成 - 自选股重构可独立验证 ✅

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### 文档和代码质量

- [ ] T045 [P] 更新README.md说明3个新功能
  - 文件: `web/frontend/README.md`
  - 内容: 字体系统、问财查询、自选股使用说明

- [ ] T046 [P] 代码格式化和清理
  - 工具: `npm run lint --fix`
  - 范围: 所有修改的Vue组件和JS文件

- [ ] T047 [P] 删除未使用的代码和注释
  - 检查: TODO注释, console.log, 废弃组件
  - 工具: 全局搜索

### 全局验证

- [ ] T048 运行quickstart.md中的完整测试清单
  - 文件: `specs/005-ui/quickstart.md`
  - 验证: 所有功能按文档描述正常工作

- [ ] T049 执行手动回归测试
  - 测试范围: Dashboard、市场数据、系统设置等其他页面
  - 验证: 字体系统未破坏现有功能

- [ ] T050 检查浏览器控制台错误和警告
  - 工具: Chrome DevTools Console
  - 验证: 无JavaScript错误, 无CSS警告

### 性能优化

- [ ] T051 检查页面加载性能
  - 指标: 首屏加载时间 <2s (SC-003)
  - 工具: Lighthouse, Chrome DevTools
  - 优化: 延迟加载非关键组件

- [ ] T052 优化API请求数量
  - 检查: Network tab中的请求数
  - 优化: 合并请求, 添加缓存

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ✅
    ↓
Phase 2 (Foundational) ← 当前焦点
    ↓
Phase 3 (US1) ← 可以开始
    ↓
Phase 4 (US2) ← 依赖T005
    ↓
Phase 5 (US3) ← 🔴 阻塞于T004, T007
    ↓
Phase 6 (Polish)
```

### Critical Path (阻塞链)

```
T004 (数据库迁移) 🔴
    ↓
T007 (category查询端点)
    ↓
T031 (端点验证)
    ↓
T032 (前端集成)
    ↓
US3所有任务
```

### Parallel Opportunities

**Phase 2 Foundation** (可并行):
```bash
[P] T005, T006, T008  # API服务层
[P] T007, T036        # 后端优化 (需等待T004)
```

**Phase 3 US1** (大部分可并行):
```bash
[P] T009, T011, T012  # 实施任务
[P] T013, T014, T015, T018  # 验证任务
```

**Phase 4 US2** (API封装完成后可并行):
```bash
T005完成后:
  [P] T019, T023  # 前端开发
  [P] T024, T029  # 测试验证
```

**Phase 5 US3** (阻塞解除后可并行):
```bash
T031验证通过后:
  [P] T032, T035  # 前端开发
  [P] T037, T043  # 测试验证
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) - 建议优先路径

**Week 1**:
1. ✅ Phase 1: Setup (已完成)
2. Phase 2: Foundation (T005-T008, **跳过T004等待数据库维护窗口**)
3. **Phase 3: US1 完整实施** (T009-T018)
4. 部署US1 → 用户验证字体系统

**Week 2**:
1. Phase 4: US2 实施 (T019-T029)
2. 部署US2 → 用户验证问财查询
3. **数据库维护窗口**: 执行T004迁移

**Week 3**:
1. 完成T007 (category端点)
2. Phase 5: US3 实施 (T030-T044)
3. 部署US3 → 用户验证自选股重构

**Week 4**:
1. Phase 6: Polish (T045-T052)
2. 全面回归测试
3. 生产环境部署

### Incremental Delivery

```
Milestone 1: 字体系统 (US1)
├─ T009-T018 完成
├─ 用户可调整字体
└─ 设置持久化 ✅

Milestone 2: 问财查询 (US2)
├─ T019-T029 完成
├─ 9个预设查询可用
└─ 结果正确显示 ✅

Milestone 3: 自选股重构 (US3)
├─ T030-T044 完成
├─ 4个选项卡布局
├─ 分组高亮显示
└─ 状态持久化 ✅

Milestone 4: 生产就绪
├─ T045-T052 完成
├─ 全面测试通过
└─ 部署上线 ✅
```

### Parallel Team Strategy

如果有2个开发者：

**Developer A** (前端专家):
- Week 1: US1 (T009-T018)
- Week 2: US2前端 (T019-T023)
- Week 3: US3前端 (T032-T035)

**Developer B** (全栈):
- Week 1: Foundation (T005-T008)
- Week 2: US2后端+测试 (T024-T029)
- Week 3: US3后端+测试 (T030-T031, T036-T044)

**Week 4**: 两人合作完成Polish和部署

---

## 关键数据流验证点

### 1. 问财查询数据流 (US2)

```
前端 WencaiPanelV2.vue
    ↓ wencaiApi.executeQuery({ query_name: "qs_1", pages: 1 })
后端 POST /api/market/wencai/query
    ↓ 响应: { success: true, total_records: 50, ... }
前端 wencaiApi.getResults("qs_1", limit=20, offset=0)
    ↓
后端 GET /api/market/wencai/results/qs_1?limit=20&offset=0
    ↓ 响应: { results: [...], total: 50 }
前端 tableData.value 更新
    ↓
UI 表格渲染
```

**验证点**:
- ✓ query_name字段名称一致
- ✓ 响应中的字段名映射 (股票代码 → symbol)
- ✓ 数值类型转换 (涨跌幅"5.23%" → 5.23)

### 2. 自选股数据流 (US3)

```
前端 WatchlistTable.vue (tab="user")
    ↓ watchlistApi.getByGroup(groupId=1)
后端 GET /api/watchlist?category=user
    ↓ 响应: { stocks: [{ symbol, name, group_name, ... }] }
前端 tableData.value 映射
    ↓ getRowClassName(row) 返回CSS类名
UI 表格渲染 + 分组高亮
```

**验证点**:
- ✓ category参数映射 (user → groupId=1)
- ✓ group_name字段存在且正确
- ✓ 分组颜色映射关系

### 3. 字段名称映射表

| 后端字段 | 前端字段 | 类型转换 | 示例 |
|---------|---------|---------|------|
| 股票代码 | symbol | 直接映射 | "000001" |
| 股票简称 | name | 直接映射 | "平安银行" |
| 最新价 | latest_price | parseFloat | "12.50" → 12.50 |
| 涨跌幅 | change_percent | 去%转数字 | "5.23%" → 5.23 |
| trade_date | add_date | YYYY-MM-DD | "2025-10-26T10:00:00" → "2025-10-26" |

---

## Notes

- ✅ = 已完成
- 🔴 = 阻塞任务
- [P] = 可并行执行
- [US1/US2/US3] = 所属用户故事
- Commit after each logical task group
- Stop at any checkpoint to validate story independently
- **T004是US3的关键阻塞点**，需协调数据库维护窗口

---

## 总结

**总任务数**: 52个任务
**US1任务**: 10个 (T009-T018)
**US2任务**: 11个 (T019-T029)
**US3任务**: 15个 (T030-T044)
**Foundation**: 8个 (T001-T008)
**Polish**: 8个 (T045-T052)

**关键路径**: T004 → T007 → T031 → US3所有任务 (约2周)
**并行机会**: US1和US2可同时进行（17个可并行任务）

**建议MVP**: 先完成US1 (1周)，快速交付价值 ✅

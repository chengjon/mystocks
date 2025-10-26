# Implementation Plan: UI系统改进 - 字体系统、问财查询、自选股重构

**Branch**: `005-ui` | **Date**: 2025-10-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-ui/spec.md`

## Summary

实现三个独立的UI改进：
1. **全局字体系统** (P1): 建立Typography规范，实现实时字体大小调整和持久化
2. **问财筛选恢复** (P2): 恢复9个预设查询(qs_1到qs_9)并实现查询结果联动
3. **自选股重构** (P3): 重构为选项卡式布局，支持4个分类和分组高亮显示

技术方案基于现有Vue 3 + Element Plus架构，通过CSS Variables实现全局字体控制，通过组件重构实现功能增强。

## Technical Context

**Language/Version**: JavaScript (ES6+), Vue 3.4.0
**Primary Dependencies**:
- Element Plus ^2.8.0 (UI组件库)
- Pinia ^2.2.0 (状态管理)
- Vue Router ^4.3.0 (路由管理)
- Vite ^5.4.0 (构建工具)

**Storage**: LocalStorage (字体偏好设置持久化)
**Testing**: 手动测试 + E2E测试（可选）
**Target Platform**: 现代浏览器（Chrome 90+, Firefox 88+, Safari 14+），不支持IE11
**Project Type**: Web应用 - 前端单页应用(SPA)
**Performance Goals**:
- 字体切换响应时间 <500ms
- 页面加载时间 <2s
- 标签页切换 <200ms (1000条数据)

**Constraints**:
- 无需后端API修改（问财API和自选股API已存在）
- 必须向后兼容现有页面
- 必须支持LocalStorage降级（禁用时使用默认值）

**Scale/Scope**:
- 影响约20+个页面/组件
- 新增/修改约10个Vue组件
- 9个问财预设查询配置

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ 通过的检查项

1. **配置驱动原则**: ✅ 字体配置通过CSS Variables管理，问财查询通过配置对象管理
2. **分层架构原则**: ✅ 遵循Vue组件化架构（表现层/业务层/数据层分离）
3. **代码质量标准**: ✅ 使用ESLint + Prettier确保代码规范
4. **最小变更原则**: ✅ 只修改字体系统、问财查询、自选股相关组件
5. **安全容错原则**: ✅ LocalStorage降级、API错误处理、空状态处理

### ⚠️ 需要注意的事项

1. **测试覆盖**: 当前前端测试覆盖率较低，本次改动将依赖手动测试
   - **理由**: 前端UI改动的自动化测试成本较高，且功能相对独立
   - **风险缓解**: 通过详细的手动测试检查清单确保质量

2. **性能监控**: 字体系统需要验证对现有页面的性能影响
   - **理由**: CSS Variables的大量使用可能影响渲染性能
   - **风险缓解**: 在Phase 1设计阶段明确性能基准，实施后验证

### 🚫 本feature不涉及的宪法要求

- **数据分类存储原则**: N/A (仅前端UI改动，不涉及后端数据存储)
- **智能路由原则**: N/A (不涉及数据路由)
- **完整可观测性原则**: N/A (前端UI改动暂不增加监控，可在后续迭代添加)

## Project Structure

### Documentation (this feature)

```
specs/005-ui/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit.plan output)
├── research.md          # Phase 0 output (technology decisions)
├── data-model.md        # Phase 1 output (data structures)
├── quickstart.md        # Phase 1 output (development guide)
├── contracts/           # Phase 1 output (API contracts)
│   └── wencai-queries.json
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/speckit.tasks - not yet created)
```

### Source Code (repository root)

```
web/frontend/
├── src/
│   ├── App.vue                        # [MODIFY] 添加全局字体变量应用
│   ├── main.js                        # [MODIFY] 添加字体初始化逻辑
│   ├── assets/
│   │   └── styles/
│   │       └── typography.css         # [NEW] Typography全局样式
│   ├── components/
│   │   ├── settings/
│   │   │   └── FontSizeSetting.vue    # [MODIFY] 完善字体设置功能
│   │   ├── market/
│   │   │   ├── WencaiPanel.vue        # [MODIFY] 添加9个预设查询
│   │   │   └── WencaiQueryList.vue    # [NEW] 预设查询列表组件
│   │   └── stock/
│   │       ├── WatchlistTabs.vue      # [MODIFY] 重构为选项卡布局
│   │       └── WatchlistTable.vue     # [MODIFY] 添加分组高亮
│   ├── stores/
│   │   └── preferences.js             # [MODIFY] 添加字体偏好管理
│   ├── config/
│   │   └── wencaiQueries.js           # [NEW] 问财预设查询配置
│   └── views/
│       └── Watchlist.vue              # [MODIFY] 自选股页面重构
│
└── tests/
    └── manual/
        └── ui-improvements-checklist.md  # [NEW] 手动测试清单
```

**Structure Decision**: 采用现有的Vue 3 SPA结构，在`web/frontend/`目录下进行所有前端修改。遵循Vue组件化开发模式，将功能拆分为独立组件。新增typography.css全局样式文件统一管理字体系统。

## Complexity Tracking

*本feature无宪法违规项，无需填写此部分*

---

## Phase 0: Research & Technology Decisions

**Status**: ✅ Completed

详见 [research.md](./research.md) - 包含以下研究结果：
- CSS Variables vs Sass Variables for dynamic font sizing
- LocalStorage vs SessionStorage for preference persistence
- Element Plus Tabs组件最佳实践
- 问财API集成方案

## Phase 1: Design & Contracts

**Status**: ⏳ In Progress

将生成以下artifacts：
- [data-model.md](./data-model.md) - 数据结构设计
- [contracts/wencai-queries.json](./contracts/wencai-queries.json) - 问财查询配置
- [quickstart.md](./quickstart.md) - 开发快速开始指南

## Phase 2: Task Breakdown

**Status**: ⏸️ Not Started

将通过 `/speckit.tasks` 命令生成 [tasks.md](./tasks.md)

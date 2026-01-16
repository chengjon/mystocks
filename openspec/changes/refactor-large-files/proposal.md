# 重构：拆分超长文件为可维护模块

## 为什么

当前项目中存在多个超过1200行的大型文件，这些文件难以维护、测试和协作开发：

1. **Python后端文件**：
   - `quant_strategy_validation.py` (4,046行) - 混合CI验证、安全扫描、性能测试
   - `mystocks_complete.py` (1,250行) - 上帝文件，包含Phase 1-5所有功能
   - `risk_management.py` (2,070行) - API层与服务层混合
   - `akshare_market.py` (1,588行) - 功能重叠，类结构损坏

2. **Vue组件文件**：
   - `ArtDecoTradingManagement.vue` (7,766行) - 超大组件，难以定位错误
   - 多个ArtDeco页面组件超过1500行
   - 高级分析组件职责不清晰

3. **其他文件**：
   - `generated-types.ts` (3,709行) - 单文件包含所有类型定义
   - 多个测试文件超过1200行

**问题影响**：
- ❌ 难以维护：修改一处可能影响多处
- ❌ 难以测试：无法进行细粒度单元测试
- ❌ 难以协作：多人同时修改同一文件导致冲突
- ❌ 难以理解：单文件承载过多职责

## 改变什么

### 1. Python后端文件拆分

| 文件 | 行数 | 拆分后 | 目标行数 |
|------|------|--------|----------|
| quant_strategy_validation.py | 4,046 | validators/ (5个子文件) | 每文件≤500行 |
| mystocks_complete.py | 1,250 | api/v1/{system,strategy,trading,admin,analysis}/ | 每文件≤300行 |
| risk_management.py | 2,070 | api/ + services/ + models/ | 每文件≤400行 |
| akshare_market.py | 1,588 | adapters/akshare/{base,market_overview,stock_info,fund_flow}/ | 每文件≤400行 |
| unified_mock_data.py | 1,294 | mock/{data_factory,generators/}/ | 每文件≤400行 |

### 2. Vue组件文件拆分

| 文件 | 行数 | 拆分后 |
|------|------|--------|
| ArtDecoTradingManagement.vue | 7,766 | components/ (5个子组件) + composables/ + api/ |
| ArtDecoMarketData.vue | 2,990 | components/ (4个子组件) + composables/ |
| ArtDecoStockManagement.vue | 2,974 | components/ (4个子组件) + composables/ |
| ArtDeco高级组件 (9个) | 1,500-2,500 | 每个拆分为3-5个专注子组件 |

### 3. TypeScript类型文件拆分

| 文件 | 行数 | 拆分后 |
|------|------|--------|
| generated-types.ts | 3,709 | types/{models/,api/,common}/ + index.ts |

### 4. 测试文件拆分

| 文件 | 行数 | 拆分后 |
|------|------|--------|
| test_ai_assisted_testing.py | 2,119 | ai/ (3个子测试文件) + fixtures/ |
| test_akshare_adapter.py | 1,904 | adapters/akshare/ (4个子测试文件) |
| 其他测试文件 (7个) | 1,200-1,800 | 按测试功能拆分 |

## 关键设计决策

### 1. API按领域(Domain)拆分，而非按阶段(Phase)拆分

**错误方式**：`api/v1/phase1/`, `phase2/`, `phase3/`  
**正确方式**：`api/v1/system/`, `strategy/`, `trading/`, `admin/`, `analysis/`

**理由**：代码结构应反映业务领域，而非开发时间线。

### 2. 遵循单向依赖规则

```
层级依赖规则（从上到下单向依赖）：
┌─────────────────────────────────────┐
│  API (路由层) - 只调用 Services       │  ← 最上层，只能向下调用
├─────────────────────────────────────┤
│  Services (业务逻辑) - 调用其他 Services │ ← 中间层
├─────────────────────────────────────┤
│  Models/Pydantic (数据模型)           │  ← 底层，被Services引用
├─────────────────────────────────────┤
│  Utils/Common (工具函数)              │  ← 底层，被所有层引用
└─────────────────────────────────────┘
```

### 3. Vue组件状态管理策略

- **层级 ≤ 2层**：使用 Props + Emit
- **层级 > 2层**：使用 Provide/Inject 或 Pinia Store

## 影响

### 受影响的规格

- `specs/code-quality/` - 代码质量标准
- `specs/backend-api/` - 后端API规范
- `specs/frontend-component/` - 前端组件规范
- `specs/test-suite/` - 测试套件规范

### 受影响的代码

**Python后端**：
- `scripts/ci/quant_strategy_validation.py`
- `web/backend/app/api/mystocks_complete.py`
- `web/backend/app/api/risk_management.py`
- `src/adapters/akshare/market_data.py`
- `web/backend/app/mock/unified_mock_data.py`

**Vue前端**：
- `web/frontend/src/views/artdeco-pages/*.vue`
- `web/frontend/src/components/artdeco/advanced/*.vue`

**TypeScript**：
- `web/frontend/src/api/types/generated-types.ts`

**测试**：
- `tests/ai/test_ai_assisted_testing.py`
- `tests/adapters/test_akshare_adapter.py`
- `tests/security/test_security_compliance.py`

### 验收标准

1. **行数控制**：每个新文件≤500行
2. **单一职责**：每个文件只有一种主要职责
3. **清晰命名**：文件名明确反映职责
4. **独立测试**：每个文件可独立单元测试
5. **无循环依赖**：文件之间没有循环引用
6. **Lint通过**：拆分后ESLint/Pylint无错误
7. **减少超长文件数**：>1200行的文件数降至10个以内

### 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| 循环依赖 | 遵循单向依赖规则，使用局部导入作为最后手段 |
| Props钻取 | 超过2层使用Provide/Inject或Pinia Store |
| 类型文件被覆盖 | 先修改生成脚本，而非手动拆分 |
| 迁移期间功能中断 | 按阶段实施，每个阶段完成后测试验证 |

## 实施时间表

### 阶段1：立即行动（本周）
1. 修复akshare_market.py类结构 - 1天
2. 拆分mystocks_complete.py - 3天
3. 拆分generated-types.ts生成脚本 - 2天

### 阶段2：短期目标（2周内）
4. 拆分ArtDecoTradingManagement.vue - 5天
5. 拆分risk_management.py - 3天
6. 拆分ArtDeco高级组件 - 5天

### 阶段3：中期目标（1个月内）
7. 拆分quant_strategy_validation.py - 7天
8. 拆分其他ArtDeco页面组件 - 10天
9. 拆分测试文件 - 7天

### 阶段4：长期目标（2个月内）
10. 拆分核心业务逻辑文件 - 14天
11. 拆分工具脚本 - 7天

## 相关文档

- 参考文档：`docs/03-API与功能文档/超长文档拆分办法.md`
- 完整方案：`docs/code_refactoring_plan.md`

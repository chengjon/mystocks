# TypeScript 类型扩展系统设计方案

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、任务方案或执行矩阵，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值和时间线如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


**文档版本**: v1.0
**创建时间**: 2026-01-19
**状态**: 待审核
**作者**: Claude Code
**审核**: 待定

---

## 📋 目录

1. [问题背景](#问题背景)
2. [问题分析](#问题分析)
3. [解决方案对比](#解决方案对比)
4. [推荐方案：类型扩展系统](#推荐方案类型扩展系统)
5. [详细实施步骤](#详细实施步骤)
6. [代码示例](#代码示例)
7. [测试验证](#测试验证)
8. [维护指南](#维护指南)
9. [风险评估](#风险评估)
10. [FAQ](#faq)

---

## 📖 问题背景

### 现状

MyStocks 项目使用自动化脚本从后端 Pydantic schemas 生成 TypeScript 类型定义：

- **生成脚本**: `scripts/generate_frontend_types.py`
- **触发方式**: `npm run dev` 和 `npm run build` 时自动运行
- **输出目录**: `web/frontend/src/api/types/`
- **生成文件**: 7个类型文件 (strategy, market, common, trading, analysis, system, admin)

### 问题发现

**时间**: 2026-01-19 10:41
**事件**: Pre-commit hook 的 TypeScript Quality Gate 检查失败，发现 **36 个类型错误**

**根本原因**:

1. 自动生成脚本只从后端 Pydantic schemas 提取类型
2. **前端专用的 ViewModel 类型**不在后端 schemas 中
3. 每次运行 `npm run dev` 时，类型文件被重新生成，**覆盖了手动添加的类型定义**

### 缺失的核心类型

**strategy.ts 缺少** (6个):
- `Strategy` - 策略基础接口
- `StrategyPerformance` - 策略绩效指标
- `BacktestTask` - 回测任务
- `BacktestResultVM` - 回测结果视图模型
- `CreateStrategyRequest` - 创建策略请求
- `UpdateStrategyRequest` - 更新策略请求

**market.ts 缺少** (3个):
- `MarketOverviewVM` - 市场总览视图模型
- `FundFlowChartPoint` - 资金流向图表数据点
- `KLineChartData` - K线图表数据

**common.ts 和 strategy.ts 类型定义错误** (多处):
- `BacktestResultSummary` - 未定义
- `BacktestTrade` - 未定义
- `PositionItem` - 应为 `Position`
- `list` - 被误用作类型

---

## 🔍 问题分析

### 生成脚本的工作原理

```python
# scripts/generate_frontend_types.py

# 1. 扫描后端 schemas 目录
schemas_dir = Path("web/backend/app/schemas/")

# 2. 提取 Pydantic 模型定义
for schema_file in schemas_dir.glob("*.py"):
    models = extract_pydantic_models(schema_file)

# 3. 转换为 TypeScript 接口
for model in models:
    typescript_interface = convert_to_ts(model)

# 4. 写入类型文件
output_file.write_text(typescript_interface)
```

### 为什么会覆盖

**package.json 配置**:
```json
{
  "scripts": {
    "dev": "npm run generate-types && vite",
    "build": "npm run generate-types && vue-tsc --noEmit && vite build"
  }
}
```

**执行流程**:
1. 用户运行 `npm run dev`
2. 自动执行 `npm run generate-types`
3. 运行 `python ../../scripts/generate_frontend_types.py`
4. **覆盖所有手动修改** ❌

### 核心矛盾

| 自动生成系统 | 手动维护需求 |
|-------------|-------------|
| 从后端 schemas 提取 | 前端 ViewModel 类型 |
| 每次启动时重新生成 | 需要持久化的类型定义 |
| 适合 CRUD API 类型 | 不适合视图层类型 |

---

## ⚖️ 解决方案对比

### 方案1: 修改生成脚本

**描述**: 在 `generate_frontend_types.py` 中硬编码缺失的类型

**实施**:
```python
# 在生成脚本中添加
MANUAL_TYPES = {
    "strategy": """
    export interface Strategy {
      id: string;
      name: string;
      // ...
    }
    """,
    "market": """
    export interface MarketOverviewVM {
      // ...
    }
    """
}

def generate_types(domain, models):
    # 自动生成
    output = generate_from_pydantic(models)

    # 追加手动类型
    output += MANUAL_TYPES.get(domain, "")

    return output
```

**优点**:
- ✅ 一次性解决，不需要手动维护扩展文件
- ✅ 类型定义集中管理

**缺点**:
- ❌ **每次新增类型都要修改脚本**
- ❌ 脚本变成"硬编码类型列表"，失去自动化意义
- ❌ 代码审查困难（脚本逻辑与类型定义混在一起）
- ❌ Git 冲突概率高（脚本频繁修改）

**维护成本**: ⭐⭐⭐⭐⭐ (非常高)

---

### 方案2: 禁用自动生成

**描述**: 移除 `package.json` 中的 `generate-types` 步骤，完全手动维护类型文件

**实施**:
```json
{
  "scripts": {
    "dev": "vite",  // 移除 generate-types
    "build": "vue-tsc --noEmit && vite build"
  }
}
```

**优点**:
- ✅ 完全手动控制
- ✅ 不会被覆盖

**缺点**:
- ❌ **失去自动同步能力**
- ❌ 后端 API 变更时需要手动更新类型
- ❌ 容易出现前后端类型不一致
- ❌ 维护工作量巨大

**维护成本**: ⭐⭐⭐⭐ (高)

---

### 方案3: 创建扩展文件 ❌

**描述**: 创建独立的扩展文件，手动维护额外类型

**实施**:
```typescript
// src/api/types/manual_extensions.ts
export interface Strategy {
  // ...
}

export interface MarketOverviewVM {
  // ...
}

// src/api/types/index.ts
export * from './strategy';
export * from './market';
export * from './manual_extensions';  // 追加导出
```

**优点**:
- ✅ 不会被覆盖
- ✅ 手动类型独立管理

**缺点**:
- ❌ **类型定义分散在多个文件**
- ❌ 导入路径混乱（`import from '../api/types'` vs `import from '../api/types/manual_extensions'`）
- ❌ 缺乏组织结构

**维护成本**: ⭐⭐⭐ (中等)

---

### ✅ 方案3改进版: 类型扩展系统 (推荐)

**描述**: 创建结构化的扩展目录，清晰分离自动生成和手动维护的类型

**核心设计**:
- 📁 创建独立的 `extensions/` 目录
- 🔄 自动生成类型保持不变
- ✋ 手动扩展类型独立维护
- 📦 统一导出接口

**目录结构**:
```
src/api/types/
├── strategy.ts          # 自动生成（不要手动编辑）
├── market.ts            # 自动生成（不要手动编辑）
├── common.ts            # 自动生成（不要手动编辑）
├── trading.ts           # 自动生成
├── analysis.ts          # 自动生成
├── system.ts            # 自动生成
├── admin.ts             # 自动生成
├── extensions/          # 🆕 手动扩展目录
│   ├── README.md        # 说明文档
│   ├── strategy.ts      # 策略类型扩展
│   ├── market.ts        # 市场类型扩展
│   ├── common.ts        # 通用类型扩展
│   └── index.ts         # 扩展类型统一导出
└── index.ts             # 总导出（合并自动+手动）
```

**优点**:
- ✅ **职责分离清晰**：自动生成 vs 手动维护
- ✅ **易于维护**：新增类型只需编辑扩展文件
- ✅ **不会被覆盖**：扩展目录独立于生成脚本
- ✅ **组织结构清晰**：按领域分类
- ✅ **向后兼容**：不影响现有代码
- ✅ **Git 友好**：冲突概率低

**缺点**:
- ⚠️ 需要新建目录结构（一次性工作）
- ⚠️ 需要更新导入路径（一次性工作）

**维护成本**: ⭐ (非常低)

---

## 🎯 推荐方案：类型扩展系统

### 核心原则

1. **单一职责原则**
   - 自动生成系统：负责后端 Pydantic schema 类型
   - 手动扩展系统：负责前端 ViewModel 类型

2. **开闭原则**
   - 对扩展开放：新增类型只需添加扩展文件
   - 对修改封闭：不需要修改生成脚本

3. **清晰分离**
   - 自动生成类型：`src/api/types/*.ts`
   - 手动扩展类型：`src/api/types/extensions/*.ts`

### 设计决策

| 决策点 | 选择 | 理由 |
|-------|------|------|
| **扩展目录位置** | `src/api/types/extensions/` | 与自动生成的类型在同一父目录，便于导入 |
| **文件组织方式** | 按领域分类 (strategy, market, common) | 与自动生成文件的命名保持一致 |
| **导出方式** | 在 `index.ts` 中统一导出 | 提供统一的导入接口 |
| **命名规范** | 与自动生成类型保持一致 | 避免 TypeScript 重复导出错误 |

---

## 📝 详细实施步骤

### 第一步：创建扩展目录结构

```bash
cd /opt/claude/mystocks_spec/web/frontend/src/api/types

# 创建扩展目录
mkdir -p extensions

# 创建 README
touch extensions/README.md
```

### 第二步：创建扩展类型文件

#### 2.1 创建 `extensions/strategy.ts`

```typescript
/**
 * 策略类型扩展
 *
 * 这些类型是前端专用的 ViewModel 类型，不存在于后端 Pydantic schemas 中
 * 每次运行 npm run dev 时不会被覆盖
 */

// ========== 核心策略类型定义 ==========

export type StrategyType = 'trend_following' | 'mean_reversion' | 'momentum' | 'breakout' | 'arbitrage';
export type StrategyStatus = 'active' | 'inactive' | 'archived' | 'testing';
export type BacktestStatus = 'pending' | 'running' | 'completed' | 'failed';

/**
 * 策略参数类型
 */
export interface StrategyParameters {
  [key: string]: any;
}

/**
 * 策略基础接口
 */
export interface Strategy {
  id: string;
  name: string;
  description: string;
  type: StrategyType;
  status: StrategyStatus;
  created_at: string;
  updated_at: string;
  parameters: StrategyParameters;
  performance: StrategyPerformance;
}

/**
 * 策略绩效指标
 */
export interface StrategyPerformance {
  strategy_id: string;
  total_return: number;
  annual_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  profit_factor: number;
  calmar_ratio?: number;
  sortino_ratio?: number;
}

/**
 * 回测任务
 */
export interface BacktestTask {
  id: string;
  strategy_id: string;
  symbol: string;
  created_at: string;
  status: BacktestStatus;
  start_date?: string;
  end_date?: string;
  initial_capital?: number;
  parameters?: StrategyParameters;
}

/**
 * 回测交易记录
 */
export interface BacktestTrade {
  trade_id: string;
  symbol: string;
  entry_time: string;
  exit_time?: string;
  entry_price: number;
  exit_price?: number;
  quantity: number;
  side: 'buy' | 'sell';
  profit_loss?: number;
  profit_loss_pct?: number;
}

/**
 * 回测结果摘要
 */
export interface BacktestResultSummary {
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  total_profit_loss: number;
  avg_profit_loss: number;
  largest_win: number;
  largest_loss: number;
  profit_factor: number;
  avg_holding_period_days: number;
}

/**
 * 回测结果视图模型
 */
export interface BacktestResultVM {
  task_id: string;
  total_return: number;
  annualized_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  profit_factor: number;
  total_trades?: number;
  equity_curve?: Array<{date: string; value: number}>;
  trades?: BacktestTrade[];
}

/**
 * 创建策略请求
 */
export interface CreateStrategyRequest {
  name: string;
  description: string;
  type: StrategyType;
  parameters: StrategyParameters;
}

/**
 * 更新策略请求
 */
export interface UpdateStrategyRequest {
  id: string;
  name?: string;
  description?: string;
  parameters?: StrategyParameters;
  status?: StrategyStatus;
}

/**
 * 策略列表响应
 */
export interface StrategyListResponse {
  strategies: Strategy[];
  total: number;
  page: number;
  page_size: number;
}
```

#### 2.2 创建 `extensions/market.ts`

```typescript
/**
 * 市场数据类型扩展
 *
 * 这些类型是前端专用的 ViewModel 类型，用于市场数据展示
 */

/**
 * 市场总览视图模型
 */
export interface MarketOverviewVM {
  market_status: 'bull' | 'bear' | 'neutral';
  index_change: number;
  index_change_pct: number;
  advance_decline_ratio: number;
  turnover_rate: number;
  timestamp: string;
}

/**
 * 资金流向图表数据点
 */
export interface FundFlowChartPoint {
  date: string;
  main_flow_in: number;
  main_flow_out: number;
  retail_flow_in: number;
  retail_flow_out: number;
  net_flow: number;
}

/**
 * K线图表数据
 */
export interface KLineChartData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  amount?: number;
}
```

#### 2.3 创建 `extensions/common.ts`

```typescript
/**
 * 通用类型扩展
 *
 * 补充自动生成类型中缺失的通用类型定义
 */

/**
 * 仓位项（统一命名）
 */
export type PositionItem = Position;

/**
 * 日期类型（用于类型约束）
 */
export type date_type = string;

/**
 * 列表类型工具
 */
export type list<T> = Array<T>;

// 重新导出 Position 类型以避免循环依赖
export interface Position {
  symbol: string;
  quantity: number;
  avg_cost: number;
  current_price: number;
  market_value: number;
  profit_loss: number;
  profit_loss_pct: number;
}
```

### 第三步：创建扩展索引文件

```typescript
/**
 * 手动维护的类型扩展
 *
 * 这些类型不会自动生成，因为它们是前端专用的 ViewModel 类型
 * 每次运行 npm run dev 时不会被覆盖
 *
 * 使用方法：
 *   import { Strategy, MarketOverviewVM } from '@/api/types'
 */

// 策略类型扩展
export * from './strategy';

// 市场类型扩展
export * from './market';

// 通用类型扩展
export * from './common';
```

### 第四步：修改主索引文件

**当前**: `src/api/types/index.ts`

```typescript
/**
 * API 类型定义
 *
 * 包含自动生成和手动扩展的类型
 */

// ========== 自动生成的类型 ==========
// 注意：这些文件每次运行 npm run dev 时会重新生成
// 请勿手动编辑

export * from './strategy';
export * from './market';
export * from './common';
export * from './trading';
export * from './analysis';
export * from './system';
export * from './admin';

// ========== 手动扩展的类型 ==========
// 这些类型不会被覆盖，可以安全编辑

export * from './extensions';
```

### 第五步：验证导入

测试类型是否正确导出：

```typescript
// 在任意 .ts 或 .vue 文件中测试

import {
  // 自动生成的类型
  BacktestRequest,
  BacktestResponse,

  // 手动扩展的类型
  Strategy,
  StrategyPerformance,
  BacktestTask,
  MarketOverviewVM,
  FundFlowChartPoint,
  KLineChartData
} from '@/api/types'

// 应该没有 TypeScript 错误
```

---

## 🧪 测试验证

### 测试1: 类型检查

```bash
cd web/frontend

# 运行类型检查
npm run type-check

# 预期结果：无错误
```

### 测试2: 自动生成验证

```bash
# 运行开发服务器（会触发类型重新生成）
npm run dev

# 检查扩展文件是否被保留
ls -la src/api/types/extensions/

# 预期结果：extensions/ 目录和文件仍然存在
```

### 测试3: 导入验证

创建测试文件 `test-types.ts`:

```typescript
// test-types.ts
import {
  Strategy,
  StrategyPerformance,
  BacktestTask,
  MarketOverviewVM,
  FundFlowChartPoint
} from '@/api/types'

const testStrategy: Strategy = {
  id: '1',
  name: '测试策略',
  description: '测试',
  type: 'trend_following',
  status: 'active',
  created_at: '2026-01-19',
  updated_at: '2026-01-19',
  parameters: {},
  performance: {
    strategy_id: '1',
    total_return: 0.15,
    annual_return: 0.18,
    sharpe_ratio: 1.5,
    max_drawdown: -0.1,
    win_rate: 0.6,
    profit_factor: 1.8
  }
}

console.log(testStrategy)
```

运行测试：
```bash
npx ts-node test-types.ts
```

### 测试4: Pre-commit Hook 验证

```bash
# 创建一个测试提交
git add src/api/types/
git commit -m "test: verify type extensions"

# 预期结果：TypeScript Quality Gate 检查通过
```

---

## 📚 维护指南

### 添加新的扩展类型

**场景**: 需要添加新的前端 ViewModel 类型

**步骤**:

1. **确定类型所属领域**
   - 策略相关 → `extensions/strategy.ts`
   - 市场相关 → `extensions/market.ts`
   - 通用类型 → `extensions/common.ts`

2. **在对应文件中添加类型定义**
   ```typescript
   // extensions/strategy.ts
   export interface NewStrategyType {
     id: string;
     name: string;
     // ...
   }
   ```

3. **更新扩展索引** (如果创建了新文件)
   ```typescript
   // extensions/index.ts
   export * from './new-domain';
   ```

4. **验证导入**
   ```typescript
   import { NewStrategyType } from '@/api/types'
   ```

### 迁移现有手动类型

**场景**: 发现某个手动维护的类型应该移到扩展系统

**步骤**:

1. **识别类型位置**
   - 如果在 `src/api/types/*.ts` 中 → 迁移到 `extensions/`
   - 如果已经在 `extensions/` 中 → 无需迁移

2. **迁移类型定义**
   ```bash
   # 从原文件中移除
   # 添加到 extensions/domain.ts
   ```

3. **更新导入路径**
   ```typescript
   // 之前
   import { MyType } from '@/api/types/market'

   // 之后（无需改变，因为 index.ts 统一导出）
   import { MyType } from '@/api/types'
   ```

### 排查类型冲突

**场景**: TypeScript 报错 "Duplicate identifier"

**原因**: 自动生成和手动扩展中存在同名类型

**解决方案**:

1. **重命名扩展类型**
   ```typescript
   // 之前
   export interface BacktestResponse { ... }

   // 之后
   export interface BacktestResponseVM { ... }
   ```

2. **使用类型别名**
   ```typescript
   import { BacktestResponse as AutoBacktestResponse } from '@/api/types'

   export type BacktestResponseVM = AutoBacktestResponse & {
     extraField: string;
   }
   ```

3. **模块化导出**
   ```typescript
   // extensions/strategy.ts
   export { Strategy as StrategyVM } from './internal'
   ```

---

## ⚠️ 风险评估

### 技术风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| **类型命名冲突** | 中 | 中 | 使用 `VM` 后缀区分 ViewModel 类型 |
| **导入路径混乱** | 低 | 低 | 统一从 `@/api/types` 导入 |
| **扩展文件被覆盖** | 极低 | 高 | 扩展目录在生成脚本之外 |
| **团队成员不理解** | 中 | 中 | 详细文档和培训 |

### 实施风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| **现有代码需要更新导入** | 高 | 中 | 使用全局搜索替换工具 |
| **过渡期类型混乱** | 中 | 中 | 分阶段迁移，先旧后新 |
| **Git 合并冲突** | 低 | 低 | 扩展文件独立，冲突概率低 |

### 维护风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| **扩展类型无人维护** | 低 | 中 | 代码审查和文档明确职责 |
| **类型定义重复** | 中 | 低 | 定期审查和重构 |
| **扩展文件过度增长** | 中 | 低 | 按领域分类，保持文件小而专一 |

---

## ❓ FAQ

### Q1: 为什么不直接修改生成脚本？

**A**: 修改生成脚本会导致：
1. 每次添加新类型都要修改脚本
2. 脚本变成"硬编码类型列表"
3. 失去自动化的意义
4. 维护成本高

### Q2: 扩展类型会不会被覆盖？

**A**: **不会**。扩展目录 `src/api/types/extensions/` 不在生成脚本的处理范围内。

### Q3: 如何区分哪些类型应该放扩展？

**A**: 简单判断：
- ✅ **后端 API 直接返回的类型** → 自动生成
- ✅ **前端 ViewModel/DTO 类型** → 手动扩展
- ✅ **UI 组件专用类型** → 手动扩展

### Q4: 是否需要更新所有导入语句？

**A**: **不需要**。因为 `index.ts` 统一导出了所有类型：
```typescript
// 仍然有效
import { Strategy } from '@/api/types'

// 无需改为
import { Strategy } from '@/api/types/extensions/strategy'
```

### Q5: 如果团队有人不知道这个系统怎么办？

**A**: 文档和培训：
1. 本文档提供完整说明
2. `extensions/README.md` 提供快速参考
3. 在 `CLAUDE.md` 中添加引用
4. 代码审查时检查违规

### Q6: 能否部分采用（只迁移部分类型）？

**A**: **可以**。这是一个渐进式方案：
1. 先创建扩展目录结构
2. 迁移最常用的类型
3. 其他类型按需迁移
4. 不影响现有代码

### Q7: 生成脚本会不会改变？

**A**: 如果后端团队修改了生成脚本：
1. 确认脚本不会处理 `extensions/` 目录
2. 更新本文档的"实施步骤"
3. 通知团队变更

### Q8: TypeScript 编译会变慢吗？

**A**: **影响极小**。添加扩展类型只是增加了类型定义文件，不会显著增加编译时间。

---

## 📊 成功标准

### 技术指标

- ✅ TypeScript 编译无错误
- ✅ Pre-commit hook 通过
- ✅ 运行 `npm run dev` 后扩展文件不被覆盖
- ✅ 所有类型正确导入

### 团队指标

- ✅ 团队成员理解扩展系统
- ✅ 代码审查时检查合规性
- ✅ 新增类型时遵循规范

### 维护指标

- ✅ 扩展类型有明确的归属
- ✅ 文档保持更新
- ✅ 定期审查和重构

---

## 📝 实施清单

### 阶段1: 准备 (1小时)

- [ ] 团队审核本方案
- [ ] 确定实施时间窗口
- [ ] 准备回滚计划

### 阶段2: 实施 (2小时)

- [ ] 创建扩展目录结构
- [ ] 添加扩展类型文件
- [ ] 修改主索引文件
- [ ] 添加 README 文档

### 阶段3: 验证 (1小时)

- [ ] 运行类型检查
- [ ] 运行开发服务器
- [ ] 测试导入和导出
- [ ] 验证 pre-commit hook

### 阶段4: 发布 (30分钟)

- [ ] 提交代码
- [ ] 更新项目文档
- [ ] 通知团队成员
- [ ] 进行培训说明

---

## 📚 相关文档

- [TypeScript 官方文档 - 模块解析](https://www.typescriptlang.org/docs/handbook/module-resolution.html)
- [Vue 3 TypeScript 支持](https://vuejs.org/guide/typescript/composition-api.html)
- [项目 CLAUDE.md - TypeScript 修复规范](../../../CLAUDE.md)
- [Pydantic 文档](https://docs.pydantic.dev/)

---

## 🔄 版本历史

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|---------|
| v1.0 | 2026-01-19 | Claude Code | 初始版本 |

---

## 👥 审核记录

| 角色 | 姓名 | 审核状态 | 日期 | 意见 |
|------|------|---------|------|------|
| 方案作者 | Claude Code | 待审核 | - | - |
| 技术审核 | _ | 待审核 | - | - |
| 架构审核 | _ | 待审核 | - | - |
| 项目负责人 | _ | 待审核 | - | - |

---

## 📞 联系方式

如有问题或建议，请联系：
- **技术讨论**: 项目 GitHub Issues
- **紧急问题**: 项目负责人直接联系

---

**文档结束**

*最后更新: 2026-01-19*
*下次审核: 实施后1个月*

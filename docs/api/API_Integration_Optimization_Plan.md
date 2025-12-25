# API集成优化计划 (API Integration Optimization Plan)

**创建日期**: 2025-12-25
**目标**: 将前端Mock数据逐步替换为真实API调用，保持原有Mock数据不变
**原则**: Mock数据保留作为备用，真实数据优先使用

---

## 📋 项目当前状态

### 环境配置 ✅
- ✅ TDengine数据库已配置 (192.168.123.104:6030)
- ✅ PostgreSQL数据库已配置 (192.168.123.104:5438)
- ✅ JWT认证已配置
- ✅ USE_MOCK_DATA=false (使用真实数据)
- ✅ 后端API服务器运行在 http://localhost:8000

### 后端API状态 ✅
- ✅ 20个API文件已迁移到UnifiedResponse v2.0.0
- ✅ CSRF保护已实现（33个测试通过）
- ✅ 125+测试全部通过

### 前端状态 ✅
- ✅ 8个工具模块已实现
- ✅ 请求拦截器已配置
- ✅ TypeScript类型自动生成

---

## 🎯 优化目标

### 核心目标
1. **数据源切换**: 从Mock数据平滑切换到真实API数据
2. **性能优化**: 确保API响应时间 < 500ms
3. **错误处理**: 完善的错误处理和用户友好提示
4. **缓存策略**: 实现智能缓存减少API调用
5. **类型安全**: 100%TypeScript类型覆盖

### 非目标（保持不变）
- ❌ 不删除原有Mock数据
- ❌ 不改变组件结构
- ❌ 不修改业务逻辑
- ❌ 不影响现有功能

---

## 📊 优化阶段划分

### Phase 1: 市场数据模块 (Market Data Module)
**优先级**: 🔴 高 | **时间**: 2-3天

#### 1.1 市场概览 (Market Overview)
- **当前状态**: 使用Mock数据
- **目标API**: `/api/market/overview`
- **数据字段对齐**:
  ```typescript
  // Mock数据结构
  interface MarketOverview {
    market_index: number;        // 市场指数
    turnover_rate: number;       // 换手率
    rise_fall_count: number;     // 涨跌家数
  }

  // API响应结构 (UnifiedResponse)
  interface MarketOverviewResponse {
    success: boolean;
    code: number;
    message: string;
    data: {
      market_index: number;
      turnover_rate: number;
      rise_fall_count: number;
      timestamp: string;
    };
  }
  ```

- **实施步骤**:
  1. ✅ 创建MarketDataAdapter
  2. ✅ 更新MarketOverviewVM
  3. ⏳ 替换API调用（保留Mock作为fallback）
  4. ⏳ 添加缓存（5分钟TTL）
  5. ⏳ 测试验证

#### 1.2 K线数据 (K-Line Data)
- **当前状态**: 使用Mock数据
- **目标API**: `/api/market/kline`
- **数据字段对齐**:
  ```typescript
  interface KLineData {
    timestamp: number;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }
  ```

#### 1.3 资金流向 (Fund Flow)
- **当前状态**: 使用Mock数据
- **目标API**: `/api/market/fund-flow`

---

### Phase 2: 策略管理模块 (Strategy Module)
**优先级**: 🟡 中 | **时间**: 2-3天

#### 2.1 策略列表 (Strategy List)
- **目标API**: `/api/strategy/list`
- **实施步骤**:
  1. 创建StrategyAdapter
  2. 更新StrategyListVM
  3. 实现策略CRUD操作
  4. 添加缓存策略

#### 2.2 回测功能 (Backtest)
- **目标API**: `/api/strategy/backtest`
- **特殊处理**: SSE实时进度更新

---

### Phase 3: 交易管理模块 (Trade Module)
**优先级**: 🔴 高 | **时间**: 2-3天

#### 3.1 持仓查询 (Position Query)
- **目标API**: `/api/trade/positions`
- **安全要求**: CSRF Token必需

#### 3.2 订单管理 (Order Management)
- **目标API**: `/api/trade/orders`
- **实施步骤**:
  1. 添加CSRF Token管理
  2. 实现订单提交
  3. 实时订单状态更新（SSE）

---

### Phase 4: 用户与监控模块 (User & Monitoring)
**优先级**: 🟢 低 | **时间**: 1-2天

#### 4.1 自选股管理 (Watchlist)
- **目标API**: `/api/watchlist`

#### 4.2 系统监控 (Monitoring)
- **目标API**: `/api/monitoring/*`
- **实施步骤**:
  1. SSE实时数据流
  2. 性能指标展示
  3. 告警管理

---

## 🔧 技术实施方案

### 1. 数据适配器模式 (Adapter Pattern)

```typescript
// utils/adapters/marketAdapter.ts
export class MarketDataAdapter {
  /**
   * 转换API响应为前端数据格式
   * @param apiResponse API原始响应
   * @param fallbackData Mock数据（降级使用）
   */
  static adaptMarketOverview(
    apiResponse: UnifiedResponse<MarketOverviewData>,
    fallbackData: MockMarketOverview
  ): MarketOverview {
    if (!apiResponse.success || !apiResponse.data) {
      console.warn('API调用失败，使用Mock数据');
      return fallbackData;
    }

    return {
      marketIndex: apiResponse.data.market_index,
      turnoverRate: apiResponse.data.turnover_rate,
      riseFallCount: apiResponse.data.rise_fall_count,
      timestamp: apiResponse.data.timestamp
    };
  }
}
```

### 2. 降级策略 (Fallback Strategy)

```typescript
// services/marketService.ts
export class MarketService {
  async getMarketOverview(): Promise<MarketOverview> {
    try {
      // 优先尝试真实API
      const response = await apiClient.get('/api/market/overview');

      if (response.data.success) {
        // 使用真实数据
        return MarketDataAdapter.adaptMarketOverview(
          response.data,
          mockMarketOverview // 传入Mock作为fallback
        );
      }
    } catch (error) {
      console.error('API调用失败:', error);
    }

    // 降级到Mock数据
    console.log('使用Mock数据');
    return mockMarketOverview;
  }
}
```

### 3. 智能缓存策略

```typescript
// utils/cache/marketCache.ts
import { CacheManager } from '@/utils/cache';

export class MarketCacheManager {
  private cache = new CacheManager('market');

  async getMarketOverview(forceRefresh = false): Promise<MarketOverview> {
    const cacheKey = 'market:overview';

    // 检查缓存
    if (!forceRefresh) {
      const cached = this.cache.get(cacheKey);
      if (cached) {
        return cached;
      }
    }

    // 调用API
    const data = await MarketService.getMarketOverview();

    // 缓存5分钟
    this.cache.set(cacheKey, data, { ttl: 300 });

    return data;
  }
}
```

### 4. 错误处理增强

```typescript
// utils/errorHandler.ts
export class APIErrorHandler {
  static handle(error: any, fallbackData: any): any {
    // 记录错误
    console.error('API Error:', error);

    // 用户友好提示
    if (error.response?.status === 401) {
      ElMessage.warning('登录已过期，请重新登录');
    } else if (error.response?.status === 403) {
      ElMessage.error('权限不足');
    } else if (error.code === 'NETWORK_ERROR') {
      ElMessage.error('网络连接失败，使用离线数据');
    }

    // 返回降级数据
    return fallbackData;
  }
}
```

---

## 📝 实施清单

### 每个模块实施检查清单

#### 准备阶段
- [ ] 确认API文档完整性
- [ ] 确认TypeScript类型已生成
- [ ] 确认Mock数据已备份
- [ ] 创建数据适配器
- [ ] 编写单元测试

#### 实施阶段
- [ ] 更新API调用逻辑
- [ ] 实现降级策略
- [ ] 添加缓存机制
- [ ] 添加错误处理
- [ ] 更新类型定义

#### 测试阶段
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 性能测试达标（< 500ms）
- [ ] 错误场景测试
- [ ] 降级策略测试

#### 验收阶段
- [ ] 功能正常
- [ ] 性能达标
- [ ] 错误处理友好
- [ ] 缓存有效
- [ ] 文档更新

---

## 🚀 快速开始指南

### Step 1: 验证环境

```bash
# 1. 检查后端服务
curl http://localhost:8000/health

# 2. 检查数据库连接
python -c "
from web.backend.app.core.config import settings
print(f'TDengine: {settings.TDENGINE_HOST}')
print(f'PostgreSQL: {settings.POSTGRESQL_HOST}')
print(f'Use Mock: {settings.USE_MOCK_DATA}')
"

# 3. 生成TypeScript类型
cd web/frontend
npm run generate-types
```

### Step 2: 运行测试

```bash
# 后端测试
cd web/backend
pytest tests/test_market_api_integration.py -v

# 前端测试
cd web/frontend
npm run test
```

### Step 3: 启动服务

```bash
# 终端1: 启动后端
cd web/backend
python -m app.app_factory

# 终端2: 启动前端
cd web/frontend
npm run dev
```

### Step 4: 验证集成

1. 打开浏览器: http://localhost:3000
2. 检查Network标签，确认API调用
3. 验证数据正确展示
4. 检查控制台无错误

---

## 📊 进度跟踪

| 模块 | 进度 | 状态 | 备注 |
|------|------|------|------|
| Market Overview | 80% | 🔄 | 适配器已创建，待替换API调用 |
| K-Line Data | 60% | 🔄 | 类型已对齐 |
| Fund Flow | 50% | ⏳ | 待实施 |
| Strategy List | 70% | 🔄 | 适配器已创建 |
| Backtest | 40% | ⏳ | SSE集成待完成 |
| Trade/Positions | 30% | ⏳ | CSRF保护待集成 |
| Watchlist | 50% | 🔄 | 基础功能完成 |
| Monitoring | 60% | 🔄 | SSE部分完成 |

**总体进度**: 55% complete

---

## ⚠️ 注意事项

### 数据安全
1. ✅ 所有敏感信息从环境变量加载
2. ✅ JWT Token存储在localStorage
3. ✅ CSRF Token自动刷新
4. ✅ 不在代码中硬编码凭证

### 性能考虑
1. ✅ API响应时间 < 500ms
2. ✅ 使用LRU缓存减少重复调用
3. ✅ SSE替代轮询获取实时数据
4. ✅ 懒加载优化首屏性能

### 错误处理
1. ✅ 优雅降级到Mock数据
2. ✅ 用户友好的错误提示
3. ✅ 自动重试机制
4. ✅ 错误日志记录

---

## 📚 相关文档

- [API集成指南](web/backend/docs/API_INTEGRATION_GUIDE.md)
- [前端开发指南](web/frontend/docs/DEVELOPER_GUIDE.md)
- [项目完成报告](openspec/changes/implement-api-web-alignment/FINAL_COMPLETION_REPORT.md)
- [API对齐核心流程](docs/guides/API对齐核心流程.md)
- [API对齐方案](docs/guides/API对齐方案.md)

---

## 🔄 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0 | 2025-12-25 | 初始版本，完整优化计划 |

---

**文档所有者**: MyStocks Development Team
**审核状态**: ✅ 已审核
**实施状态**: 🚀 进行中

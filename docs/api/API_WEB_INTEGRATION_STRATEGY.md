# API与Web集成开发策略指南

**版本**: 1.0.0
**创建日期**: 2025-12-29
**状态**: 战略规划

---

## 📋 目录

1. [整体战略](#整体战略)
2. [阶段一：现有API对接](#阶段一现有api对接)
3. [阶段二：新增API流程](#阶段二新增api流程)
4. [最佳实践](#最佳实践)
5. [工具链使用](#工具链使用)

---

## 整体战略

### 核心理念：契约驱动开发 (Contract-First Development)

```
前端需求 → OpenAPI契约 → 后端实现 → 自动化测试 → 部署
   ↓         ↓           ↓          ↓          ↓
TS类型    版本管理    Pydantic    CI/CD     契约同步
```

### 三大支柱

1. **API契约管理平台** - CLI-2已完成
   - 契约版本管理
   - 差异检测
   - OpenAPI验证
   - TypeScript类型生成

2. **统一响应格式** - UnifiedResponse v2.0.0
   - 标准化响应结构
   - 错误处理一致
   - request_id追踪

3. **适配器模式** - 前端数据转换层
   - API → Mock数据降级
   - 数据格式适配
   - 智能缓存策略

---

## 阶段一：现有API对接

### Step 1: API契约注册与分类

#### 1.1 按功能模块分类现有API

```bash
# 使用API契约管理平台CLI工具
cd /opt/claude/mystocks_phase6_api_contract

# 为每个功能模块创建契约
api-contract-sync create market-data 1.0.0 \
  -s /path/to/openapi.yaml \
  -d "市场数据API" \
  -t stable

api-contract-sync create strategy-management 1.0.0 \
  -s /path/to/openapi.yaml \
  -d "策略管理API" \
  -t stable

api-contract-sync create trade-management 1.0.0 \
  -s /path/to/openapi.yaml \
  -d "交易管理API" \
  -t stable

api-contract-sync create monitoring 1.0.0 \
  -s /path/to/openapi.yaml \
  -d "监控与告警API" \
  -t stable
```

#### 1.2 导出现有API为OpenAPI规范

**方法1: 从FastAPI自动生成**
```python
# web/backend/scripts/generate_openapi_spec.py
import json
from app.main import app

# 导出OpenAPI规范
openapi_schema = app.openapi()

# 保存为文件
with open('docs/api/openapi_market_data.json', 'w', encoding='utf-8') as f:
    json.dump(openapi_schema, f, ensure_ascii=False, indent=2)

print(f"✅ OpenAPI规范已导出")
print(f"   - Title: {openapi_schema['info']['title']}")
print(f"   - Version: {openapi_schema['info']['version']}")
print(f"   - 端点数量: {len(openapi_schema['paths'])}")
```

**方法2: 手动组织OpenAPI文档**
```yaml
# docs/api/openapi/market-data-api.yaml
openapi: 3.0.3
info:
  title: Market Data API
  version: 1.0.0
  description: 市场数据查询接口
paths:
  /api/market/overview:
    get:
      summary: 获取市场概览
      tags:
        - Market Data
      responses:
        '200':
          description: 成功响应
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UnifiedResponse_MarketOverview'
  /api/market/kline:
    get:
      summary: 获取K线数据
      parameters:
        - name: symbol
          in: query
          required: true
          schema:
            type: string
        - name: interval
          in: query
          schema:
            type: string
            enum: [1m, 5m, 15m, 30m, 1h, 1d]
      responses:
        '200':
          description: 成功响应
components:
  schemas:
    UnifiedResponse_MarketOverview:
      type: object
      properties:
        success:
          type: boolean
        code:
          type: integer
        message:
          type: string
        data:
          $ref: '#/components/schemas/MarketOverviewData'
    MarketOverviewData:
      type: object
      properties:
        market_index:
          type: object
        turnover_rate:
          type: number
```

#### 1.3 注册到契约管理平台

```bash
# 为市场数据API创建契约版本
api-contract-sync create market-data 1.0.0 \
  -s docs/api/openapi/market-data-api.yaml \
  -a "backend-team" \
  -d "市场数据模块API v1.0.0" \
  -t stable,production

# 验证契约有效性
api-contract-sync validate docs/api/openapi/market-data-api.yaml

# 激活版本（如果不是首个版本）
api-contract-sync activate $(api-contract-sync list --name market-data --json | jq '.[0].id')
```

---

### Step 2: 生成TypeScript类型定义

#### 2.1 使用openapi-typescript生成类型

```bash
# 安装工具
npm install -g openapi-typescript

# 生成TypeScript类型定义
cd web/frontend

# 从API契约平台导出OpenAPI规范
curl http://localhost:8020/openapi.json -o openapi.json

# 生成类型文件
npx openapi-typescript openapi.json -o src/types/api-generated.ts

# 或使用生成脚本
bash scripts/generate-types/generate_ts_types.sh
```

#### 2.2 类型文件结构

```typescript
// web/frontend/src/types/api-generated.ts
export interface paths {
  "/api/market/overview": {
    get: operations["getMarketOverview"];
  };
  "/api/market/kline": {
    get: operations["getKlineData"];
  };
}

export interface operations {
  getMarketOverview: {
    responses: {
      200: {
        content: {
          "application/json": UnifiedResponse<MarketOverviewData>;
        };
      };
    };
  };
  getKlineData: {
    parameters: {
      query: {
        symbol: string;
        interval?: "1m" | "5m" | "15m" | "30m" | "1h" | "1d";
      };
    };
    responses: {
      200: {
        content: {
          "application/json": UnifiedResponse<KlineData>;
        };
      };
    };
  };
}

export interface UnifiedResponse<T> {
  success: boolean;
  code: number;
  message: string;
  data: T;
  timestamp: string;
  request_id: string;
  errors: ErrorDetail[] | null;
}

export interface MarketOverviewData {
  market_index: Record<string, number>;
  turnover_rate: number;
  rise_fall_count: {
    rise: number;
    fall: number;
    flat: number;
  };
  top_etfs: Array<{
    symbol: string;
    name: string;
    change_percent: number;
  }>;
  timestamp: string;
}
```

---

### Step 3: 创建前端API服务层

#### 3.1 基础API客户端

```typescript
// web/frontend/src/api/apiClient.ts
import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosError } from 'axios';
import type { UnifiedResponse } from '@/types/api-generated';

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8020',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器：添加CSRF token
apiClient.interceptors.request.use(
  (config) => {
    // 从localStorage获取CSRF token
    const csrfToken = localStorage.getItem('csrf_token');
    if (csrfToken && ['post', 'put', 'patch', 'delete'].includes(config.method?.toLowerCase() || '')) {
      config.headers['x-csrf-token'] = csrfToken;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器：统一处理UnifiedResponse格式
apiClient.interceptors.response.use(
  (response) => {
    // 后端已返回UnifiedResponse格式，直接返回
    return response.data;
  },
  (error: AxiosError) => {
    // 网络错误或HTTP状态码错误
    console.error('API request failed:', error.message);

    // 返回标准错误响应
    const errorResponse: UnifiedResponse<null> = {
      success: false,
      code: error.response?.status || 500,
      message: error.message || '网络请求失败',
      data: null,
      timestamp: new Date().toISOString(),
      request_id: '',
      errors: [{
        code: 'NETWORK_ERROR',
        message: error.message,
        details: error
      }]
    };

    return Promise.reject(errorResponse);
  }
);

// 通用API方法
export const apiGet = <T>(url: string, params?: any): Promise<UnifiedResponse<T>> => {
  return apiClient.get(url, { params });
};

export const apiPost = <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<UnifiedResponse<T>> => {
  return apiClient.post(url, data, config);
};

export const apiPut = <T>(url: string, data?: any): Promise<UnifiedResponse<T>> => {
  return apiClient.put(url, data);
};

export const apiDelete = <T>(url: string): Promise<UnifiedResponse<T>> => {
  return apiClient.delete(url);
};

export default apiClient;
```

#### 3.2 市场数据API服务

```typescript
// web/frontend/src/api/services/marketService.ts
import { apiGet, apiPost } from '../apiClient';
import type { UnifiedResponse, operations } from '@/types/api-generated';

// 类型别名
export type MarketOverviewResponse = UnifiedResponse<operations['getMarketOverview']['responses']['200']['content']['application/json']['data']>;
export type KlineDataResponse = UnifiedResponse<operations['getKlineData']['responses']['200']['content']['application/json']['data']>;

export class MarketApiService {
  private baseUrl = '/api/market';

  /**
   * 获取市场概览
   */
  async getMarketOverview(): Promise<MarketOverviewResponse> {
    return apiGet(`${this.baseUrl}/overview`);
  }

  /**
   * 获取K线数据
   */
  async getKlineData(params: {
    symbol: string;
    interval?: '1m' | '5m' | '15m' | '30m' | '1h' | '1d';
    start_date?: string;
    end_date?: string;
    limit?: number;
  }): Promise<KlineDataResponse> {
    return apiGet(`${this.baseUrl}/kline`, params);
  }

  /**
   * 获取资金流向数据
   */
  async getFundFlow(symbol: string): Promise<UnifiedResponse<any>> {
    return apiGet(`${this.baseUrl}/fund-flow`, { symbol });
  }

  /**
   * 获取龙虎榜数据
   */
  async getLongHuBang(date?: string): Promise<UnifiedResponse<any>> {
    return apiGet(`${this.baseUrl}/lhb`, { date });
  }
}

// 导出单例
export const marketService = new MarketApiService();
```

---

### Step 4: 创建数据适配器层

#### 4.1 适配器模式实现

```typescript
// web/frontend/src/api/adapters/marketAdapter.ts
import type { UnifiedResponse } from '@/types/api-generated';
import { mockMarketOverview } from '@/mock/marketMock';

// 前端数据模型（与后端解耦）
export interface MarketOverview {
  marketIndex: Record<string, number>;
  turnoverRate: number;
  riseFallCount: {
    rise: number;
    fall: number;
    flat: number;
  };
  topETFs: Array<{
    symbol: string;
    name: string;
    changePercent: number;
  }>;
  timestamp: Date;
}

export class MarketDataAdapter {
  /**
   * 适配市场概览数据
   * @param apiResponse - API响应
   * @param fallbackData - 降级Mock数据
   */
  static adaptMarketOverview(
    apiResponse: UnifiedResponse<any>,
    fallbackData: any
  ): MarketOverview {
    // 检查API响应是否成功
    if (!apiResponse.success || !apiResponse.data) {
      console.warn('[MarketAdapter] API调用失败，使用Mock数据', {
        message: apiResponse.message,
        code: apiResponse.code
      });
      return this.adaptMarketOverviewFromMock(fallbackData);
    }

    // 转换后端数据格式到前端模型
    const apiData = apiResponse.data;
    return {
      marketIndex: apiData.market_index || {},
      turnoverRate: apiData.turnover_rate || 0,
      riseFallCount: {
        rise: apiData.rise_fall_count?.rise || 0,
        fall: apiData.rise_fall_count?.fall || 0,
        flat: apiData.rise_fall_count?.flat || 0,
      },
      topETFs: (apiData.top_etfs || []).map((etf: any) => ({
        symbol: etf.symbol,
        name: etf.name,
        changePercent: etf.change_percent,
      })),
      timestamp: new Date(apiData.timestamp),
    };
  }

  /**
   * 从Mock数据适配
   */
  private static adaptMarketOverviewFromMock(mockData: any): MarketOverview {
    return {
      marketIndex: mockData.marketIndex || {},
      turnoverRate: mockData.turnoverRate || 0,
      riseFallCount: mockData.riseFallCount || { rise: 0, fall: 0, flat: 0 },
      topETFs: mockData.topETFs || [],
      timestamp: new Date(mockData.timestamp || Date.now()),
    };
  }
}
```

#### 4.2 带缓存的API服务

```typescript
// web/frontend/src/api/services/marketWithFallback.ts
import { LRUCache } from 'lru-cache';
import { marketService } from './marketService';
import { MarketDataAdapter } from '../adapters/marketAdapter';
import { mockMarketOverview } from '@/mock/marketMock';
import type { MarketOverview } from '../adapters/marketAdapter';

export class MarketApiServiceWithFallback {
  private cache: LRUCache<string, any>;

  constructor() {
    // 初始化LRU缓存（最大100项，5分钟TTL）
    this.cache = new LRUCache({
      max: 100,
      ttl: 5 * 60 * 1000, // 5分钟
    });
  }

  /**
   * 获取市场概览（带缓存和降级）
   */
  async getMarketOverview(forceRefresh = false): Promise<MarketOverview> {
    const cacheKey = 'market:overview';

    // 检查缓存
    if (!forceRefresh && this.cache.has(cacheKey)) {
      console.log('[MarketService] 使用缓存数据');
      return this.cache.get(cacheKey);
    }

    try {
      // 调用API
      const response = await marketService.getMarketOverview();

      // 适配数据
      const adapted = MarketDataAdapter.adaptMarketOverview(
        response,
        mockMarketOverview
      );

      // 存入缓存
      this.cache.set(cacheKey, adapted);

      return adapted;
    } catch (error) {
      console.error('[MarketService] API调用失败，使用Mock数据降级', error);

      // 返回Mock数据
      const fallback = MarketDataAdapter.adaptMarketOverviewFromMock(mockMarketOverview);
      return fallback;
    }
  }

  /**
   * 清除缓存
   */
  clearCache(key?: string): void {
    if (key) {
      this.cache.delete(key);
    } else {
      this.cache.clear();
    }
  }
}

// 导出单例
export const marketServiceWithFallback = new MarketApiServiceWithFallback();
```

---

### Step 5: 创建Vue Composable

```typescript
// web/frontend/src/composables/useMarketData.ts
import { ref, readonly, onMounted, onUnmounted } from 'vue';
import { useIntervalFn } from '@vueuse/core';
import { marketServiceWithFallback } from '@/api/services/marketWithFallback';
import type { MarketOverview } from '@/api/adapters/marketAdapter';

export function useMarketData(autoRefresh = true) {
  const marketData = ref<MarketOverview | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  /**
   * 获取市场数据
   */
  const fetchMarketData = async (forceRefresh = false) => {
    loading.value = true;
    error.value = null;

    try {
      marketData.value = await marketServiceWithFallback.getMarketOverview(forceRefresh);
      console.log('[useMarketData] 数据获取成功', marketData.value);
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error';
      console.error('[useMarketData] 数据获取失败', err);
    } finally {
      loading.value = false;
    }
  };

  /**
   * 刷新数据
   */
  const refresh = () => fetchMarketData(true);

  // 自动刷新（每5分钟）
  let intervalController: ReturnType<typeof useIntervalFn> | null = null;

  if (autoRefresh) {
    intervalController = useIntervalFn(() => {
      console.log('[useMarketData] 自动刷新触发');
      refresh();
    }, 5 * 60 * 1000); // 5分钟
  }

  // 生命周期钩子
  onMounted(() => {
    console.log('[useMarketData] 组件挂载，开始获取数据');
    fetchMarketData();
    intervalController?.start();
  });

  onUnmounted(() => {
    console.log('[useMarketData] 组件卸载，停止自动刷新');
    intervalController?.stop();
  });

  return {
    marketData: readonly(marketData),
    loading: readonly(loading),
    error: readonly(error),
    refresh,
  };
}
```

---

### Step 6: Vue组件集成

```vue
<!-- web/frontend/src/views/Dashboard.vue -->
<script setup lang="ts">
import { useMarketData } from '@/composables/useMarketData';

// 获取市场数据
const { marketData, loading, error, refresh } = useMarketData(autoRefresh = true);
</script>

<template>
  <div class="dashboard">
    <h1>MyStocks 量化交易仪表盘</h1>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error">
      <el-alert type="error" :title="error" />
    </div>

    <!-- 数据展示 -->
    <div v-else-if="marketData" class="market-overview">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card>
            <h3>上证指数</h3>
            <div class="value">{{ marketData.marketIndex['sh000001']?.toFixed(2) || 'N/A' }}</div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card>
            <h3>深证成指</h3>
            <div class="value">{{ marketData.marketIndex['sz399001']?.toFixed(2) || 'N/A' }}</div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card>
            <h3>换手率</h3>
            <div class="value">{{ (marketData.turnoverRate * 100).toFixed(2) }}%</div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card>
            <h3>涨跌统计</h3>
            <div class="value">
              涨{{ marketData.riseFallCount.rise }} /
              跌{{ marketData.riseFallCount.fall }}
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 刷新按钮 -->
      <el-button @click="refresh()" :loading="loading">
        刷新数据
      </el-button>

      <!-- 数据更新时间 -->
      <div class="timestamp">
        更新时间: {{ marketData.timestamp.toLocaleString('zh-CN') }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  padding: 20px;
}

.loading, .error {
  margin: 20px 0;
}

.value {
  font-size: 24px;
  font-weight: bold;
  margin-top: 10px;
}

.timestamp {
  margin-top: 20px;
  color: #999;
  font-size: 12px;
}
</style>
```

---

## 阶段二：新增API流程

### 场景：Web端需要新功能

**示例**: 前端需要"策略回测结果对比"功能，但后端API不存在

### 完整开发流程

#### Step 1: 前端定义需求（契约先行）

```yaml
# docs/api/openapi/strategy-comparison-api.yaml
openapi: 3.0.3
info:
  title: Strategy Comparison API
  version: 1.0.0
  description: 策略回测结果对比接口
paths:
  /api/strategy/comparison:
    post:
      summary: 对比多个策略的回测结果
      tags:
        - Strategy Comparison
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - strategy_ids
              properties:
                strategy_ids:
                  type: array
                  items:
                    type: string
                  description: 策略ID列表
                  example: ["strategy_001", "strategy_002", "strategy_003"]
                metrics:
                  type: array
                  items:
                    type: string
                    enum: [total_return, sharpe_ratio, max_drawdown, win_rate]
                  description: 要对比的指标
                  default: ["total_return", "sharpe_ratio", "max_drawdown"]
      responses:
        '200':
          description: 对比结果
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UnifiedResponse_StrategyComparison'
        '400':
          description: 请求参数错误
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UnifiedResponse_Error'
        '500':
          description: 服务器错误
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UnifiedResponse_Error'
components:
  schemas:
    UnifiedResponse_StrategyComparison:
      type: object
      properties:
        success:
          type: boolean
        code:
          type: integer
        message:
          type: string
        data:
          $ref: '#/components/schemas/StrategyComparisonData'
        timestamp:
          type: string
          format: date-time
        request_id:
          type: string
    StrategyComparisonData:
      type: object
      properties:
        strategies:
          type: array
          items:
            $ref: '#/components/schemas/StrategyComparisonItem'
        comparison_table:
          type: object
          description: 各指标对比表
          additionalProperties:
            type: object
            properties:
              strategy_id:
                type: string
              value:
                type: number
              rank:
                type: integer
    StrategyComparisonItem:
      type: object
      properties:
        strategy_id:
          type: string
        strategy_name:
          type: string
        metrics:
          type: object
          properties:
            total_return:
              type: number
            sharpe_ratio:
              type: number
            max_drawdown:
              type: number
            win_rate:
              type: number
        ranking:
          type: object
          properties:
            overall:
              type: integer
            by_metric:
              type: object
```

---

#### Step 2: 注册契约到平台

```bash
# 创建新契约
api-contract-sync create strategy-comparison 1.0.0 \
  -s docs/api/openapi/strategy-comparison-api.yaml \
  -a "frontend-team" \
  -d "策略对比功能API" \
  -t beta

# 验证契约
api-contract-sync validate docs/api/openapi/strategy-comparison-api.yaml

# 查看契约列表
api-contract-sync list --name strategy-comparison
```

---

#### Step 3: 生成前端类型

```bash
# 重新生成类型文件
cd web/frontend
npx openapi-typescript openapi.json -o src/types/api-generated.ts

# 或使用增量生成
npx openapi-typescript docs/api/openapi/strategy-comparison-api.yaml \
  -o src/types/strategy-comparison.d.ts
```

---

#### Step 4: 创建前端API服务

```typescript
// web/frontend/src/api/services/strategyComparisonService.ts
import { apiPost } from '../apiClient';
import type { UnifiedResponse } from '@/types/api-generated';

export interface StrategyComparisonRequest {
  strategy_ids: string[];
  metrics?: Array<'total_return' | 'sharpe_ratio' | 'max_drawdown' | 'win_rate'>;
}

export interface StrategyComparisonData {
  strategies: Array<{
    strategy_id: string;
    strategy_name: string;
    metrics: {
      total_return: number;
      sharpe_ratio: number;
      max_drawdown: number;
      win_rate: number;
    };
    ranking: {
      overall: number;
      by_metric: Record<string, number>;
    };
  }>;
  comparison_table: Record<string, Record<string, {
    strategy_id: string;
    value: number;
    rank: number;
  }>>;
}

export class StrategyComparisonService {
  /**
   * 对比策略回测结果
   */
  async compareStrategies(
    request: StrategyComparisonRequest
  ): Promise<UnifiedResponse<StrategyComparisonData>> {
    return apiPost('/api/strategy/comparison', request);
  }
}

export const strategyComparisonService = new StrategyComparisonService();
```

---

#### Step 5: 后端实现API

```python
# web/backend/app/api/strategy_comparison.py
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

from app.core.responses import create_unified_success_response, create_unified_error_response

router = APIRouter(prefix="/api/strategy", tags=["strategy-comparison"])


# ==================== 数据模型 ====================

class StrategyComparisonRequest(BaseModel):
    """策略对比请求模型"""
    strategy_ids: List[str] = Field(..., description="策略ID列表", min_items=1, max_items=10)
    metrics: Optional[List[Literal['total_return', 'sharpe_ratio', 'max_drawdown', 'win_rate']]] = Field(
        default=['total_return', 'sharpe_ratio', 'max_drawdown'],
        description="要对比的指标"
    )


class StrategyMetrics(BaseModel):
    """策略指标"""
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float


class StrategyRanking(BaseModel):
    """策略排名"""
    overall: int
    by_metric: dict[str, int]


class StrategyComparisonItem(BaseModel):
    """策略对比项"""
    strategy_id: str
    strategy_name: str
    metrics: StrategyMetrics
    ranking: StrategyRanking


class StrategyComparisonData(BaseModel):
    """策略对比数据"""
    strategies: List[StrategyComparisonItem]
    comparison_table: dict[str, dict[str, dict[str, any]]]


# ==================== API端点 ====================

@router.post("/comparison")
async def compare_strategies(
    request: StrategyComparisonRequest,
    http_request: Request
):
    """
    对比多个策略的回测结果

    Args:
        request: 策略对比请求
        http_request: FastAPI请求对象

    Returns:
        策略对比结果
    """
    request_id = getattr(http_request.state, "request_id", None)

    try:
        # TODO: 实现策略对比逻辑
        # 1. 从数据库查询各策略的回测结果
        # 2. 计算排名
        # 3. 生成对比表

        # Mock数据 - 待替换为真实实现
        strategies_data = []
        for idx, strategy_id in enumerate(request.strategy_ids):
            strategies_data.append({
                "strategy_id": strategy_id,
                "strategy_name": f"策略 {strategy_id}",
                "metrics": {
                    "total_return": 0.15 + idx * 0.05,
                    "sharpe_ratio": 1.5 + idx * 0.3,
                    "max_drawdown": -0.1 - idx * 0.02,
                    "win_rate": 0.6 + idx * 0.05,
                },
                "ranking": {
                    "overall": idx + 1,
                    "by_metric": {
                        "total_return": idx + 1,
                        "sharpe_ratio": idx + 1,
                        "max_drawdown": len(request.strategy_ids) - idx,
                        "win_rate": idx + 1,
                    }
                }
            })

        # 生成对比表
        comparison_table = {}
        for metric in request.metrics or ['total_return', 'sharpe_ratio', 'max_drawdown']:
            comparison_table[metric] = {}
            for item in strategies_data:
                comparison_table[metric][item['strategy_id']] = {
                    "strategy_id": item['strategy_id'],
                    "value": item['metrics'][metric],
                    "rank": item['ranking']['by_metric'][metric]
                }

        result_data = {
            "strategies": strategies_data,
            "comparison_table": comparison_table
        }

        return create_unified_success_response(
            data=result_data,
            message="策略对比成功",
            request_id=request_id,
        )

    except Exception as e:
        logger.error(f"策略对比失败: {str(e)}", exc_info=True)
        return create_unified_error_response(
            message=f"策略对比失败: {str(e)}",
            request_id=request_id,
        )


logger.info("✅ 策略对比API路由已加载")
```

---

#### Step 6: 更新契约并发布

```bash
# 更新契约到1.1.0（新增后端实现后）
api-contract-sync sync strategy-comparison \
  -s docs/api/openapi/strategy-comparison-api.yaml \
  --version 1.1.0 \
  -d "新增后端实现"

# 检查契约差异
api-contract-sync diff $(api-contract-sync list --name strategy-comparison --json | jq '.[0].id') $(api-contract-sync list --name strategy-comparison --json | jq '.[1].id')

# 激活新版本
api-contract-sync activate $(api-contract-sync list --name strategy-comparison --json | jq '.[1].id')
```

---

#### Step 7: 前端集成新API

```vue
<!-- web/frontend/src/views/StrategyComparison.vue -->
<script setup lang="ts">
import { ref } from 'vue';
import { strategyComparisonService } from '@/api/services/strategyComparisonService';
import type { StrategyComparisonRequest } from '@/api/services/strategyComparisonService';

const strategies = ref<string[]>(['strategy_001', 'strategy_002', 'strategy_003']);
const comparisonData = ref<any>(null);
const loading = ref(false);

const compareStrategies = async () => {
  loading.value = true;

  try {
    const request: StrategyComparisonRequest = {
      strategy_ids: strategies.value,
      metrics: ['total_return', 'sharpe_ratio', 'max_drawdown', 'win_rate']
    };

    const response = await strategyComparisonService.compareStrategies(request);

    if (response.success) {
      comparisonData.value = response.data;
    } else {
      console.error('策略对比失败:', response.message);
    }
  } catch (error) {
    console.error('API调用失败:', error);
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="strategy-comparison">
    <h1>策略回测结果对比</h1>

    <el-button @click="compareStrategies" :loading="loading">
      开始对比
    </el-button>

    <div v-if="comparisonData" class="comparison-result">
      <el-table :data="comparisonData.strategies">
        <el-table-column prop="strategy_name" label="策略名称" />
        <el-table-column prop="metrics.total_return" label="总收益率" :formatter="(row) => `${(row.metrics.total_return * 100).toFixed(2)}%`" />
        <el-table-column prop="metrics.sharpe_ratio" label="夏普比率" />
        <el-table-column prop="metrics.max_drawdown" label="最大回撤" :formatter="(row) => `${(row.metrics.max_drawdown * 100).toFixed(2)}%`" />
        <el-table-column prop="metrics.win_rate" label="胜率" :formatter="(row) => `${(row.metrics.win_rate * 100).toFixed(2)}%`" />
        <el-table-column prop="ranking.overall" label="综合排名" />
      </el-table>
    </div>
  </div>
</template>
```

---

## 最佳实践

### 1. 版本管理策略

```bash
# 遵循语义化版本规范 (SemVer)
MAJOR.MINOR.PATCH

# 示例:
# 1.0.0 → 1.0.1 (修复错误，向后兼容)
# 1.0.1 → 1.1.0 (新增功能，向后兼容)
# 1.1.0 → 2.0.0 (破坏性变更，不向后兼容)
```

**破坏性变更检测**:
```bash
# 使用契约管理平台检测破坏性变更
api-contract-sync diff 1 2 --check-breaking

# 输出示例:
# ⚠️ 检测到破坏性变更:
# - /api/market/kline: 参数 interval 从必选改为可选
# - /api/strategy: 删除了字段 description
```

### 2. Mock数据管理

**Mock数据作为降级策略**:
```typescript
// ✅ 推荐: Mock数据作为降级
try {
  data = await apiCall();
} catch (error) {
  data = mockData; // 降级到Mock
}

// ❌ 避免: 硬编码Mock数据在组件中
const data = [ /* 大量硬编码数据 */ ];
```

### 3. 错误处理模式

```typescript
// 统一错误处理
class ApiErrorHandler {
  static handle(error: UnifiedResponseError): void {
    // 根据错误码显示不同提示
    switch (error.code) {
      case 401:
        ElMessage.error('请先登录');
        // 跳转到登录页
        break;
      case 403:
        ElMessage.error('无权限访问');
        break;
      case 500:
        ElMessage.error('服务器错误，请稍后重试');
        break;
      default:
        ElMessage.error(error.message || '请求失败');
    }
  }
}
```

### 4. 缓存策略

```typescript
// 不同数据类型使用不同TTL
const CACHE_TTL = {
  // 实时数据（短缓存）
  MARKET_OVERVIEW: 5 * 60 * 1000,      // 5分钟
  FUND_FLOW: 10 * 60 * 1000,            // 10分钟

  // 静态数据（长缓存）
  STRATEGY_LIST: 30 * 60 * 1000,        // 30分钟
  SYMBOL_INFO: 24 * 60 * 60 * 1000,     // 24小时

  // 历史数据（中等缓存）
  KLINE: 3 * 60 * 1000,                 // 3分钟
};
```

---

## 工具链使用

### 完整开发工作流

```bash
# ===== 前端需求 → 契约定义 =====
# 1. 前端开发者在 docs/api/openapi/ 编写 OpenAPI 规范
vim docs/api/openapi/new-feature-api.yaml

# 2. 验证契约有效性
api-contract-sync validate docs/api/openapi/new-feature-api.yaml

# 3. 注册契约到平台
api-contract-sync create new-feature 1.0.0 \
  -s docs/api/openapi/new-feature-api.yaml \
  -d "新功能API" \
  -t beta


# ===== 生成前端类型 =====
# 4. 生成TypeScript类型
cd web/frontend
npx openapi-typescript ../docs/api/openapi/new-feature-api.yaml \
  -o src/types/new-feature.d.ts


# ===== 前端实现 =====
# 5. 创建API服务层
# 手动编写或使用生成器
vim src/api/services/newFeatureService.ts

# 6. 创建Composable
vim src/composables/useNewFeature.ts

# 7. 创建Vue组件
vim src/views/NewFeature.vue


# ===== 后端实现 =====
# 8. 后端开发者根据契约实现API
# 创建路由文件
vim web/backend/app/api/new_feature.py

# 9. 实现业务逻辑
# 遵循契约中定义的请求/响应模型


# ===== 测试 =====
# 10. 前端测试
cd web/frontend
npm run test

# 11. 后端测试
cd web/backend
pytest tests/api/test_new_feature.py

# 12. 集成测试
bash scripts/tests/run_api_tests.sh


# ===== 部署 =====
# 13. 更新契约版本
api-contract-sync sync new-feature \
  -s docs/api/openapi/new-feature-api.yaml \
  --version 1.0.0

# 14. 激活契约
api-contract-sync activate $(api-contract-sync list --name new-feature --json | jq '.[0].id')

# 15. Pre-commit hooks自动验证
git add .
git commit -m "feat: 添加新功能API"
```

### CI/CD集成

**GitHub Actions自动验证**:
```yaml
# .github/workflows/api-contract-validation.yml
name: API Contract Validation

on:
  pull_request:
    paths:
      - 'docs/api/openapi/**'
      - 'web/backend/app/api/**'
      - 'web/frontend/src/api/**'

jobs:
  contract-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: 验证OpenAPI规范
        run: |
          pip install -r requirements.txt
          api-contract-sync validate docs/api/openapi/*.yaml

      - name: 检测破坏性变更
        run: |
          # 对比PR前后契约差异
          api-contract-sync diff ${{ github.event.before }} ${{ github.sha }}

      - name: 生成TypeScript类型
        run: |
          cd web/frontend
          npm install
          npm run generate-types

      - name: 运行测试
        run: |
          pytest tests/api/
          cd web/frontend && npm test
```

---

## 附录

### A. 相关文档

- [API契约管理平台文档](../mystocks_phase6_api_contract/docs/api/CONTRACT_MANAGEMENT_API.md)
- [API集成指南](./API_INTEGRATION_GUIDE.md)
- [后端开发规范](./guides/后端开发规范.md)
- [前端开发规范](./guides/前端开发规范.md)

### B. 工具安装

```bash
# 后端工具
pip install api-contract-sync

# 前端工具
npm install -g openapi-typescript
npm install @vueuse/core axios lru-cache
```

### C. 快速参考

| 操作 | 命令 |
|------|------|
| 创建契约 | `api-contract-sync create <name> <version> -s <spec>` |
| 验证契约 | `api-contract-sync validate <spec>` |
| 对比版本 | `api-contract-sync diff <from_id> <to_id>` |
| 激活版本 | `api-contract-sync activate <version_id>` |
| 生成类型 | `npx openapi-typescript <spec> -o <output>` |

---

**文档版本**: 1.0.0
**最后更新**: 2025-12-29
**维护者**: MyStocks 开发团队

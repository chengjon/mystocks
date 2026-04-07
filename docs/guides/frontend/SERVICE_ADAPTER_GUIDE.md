# 前端Service适配器层使用指南

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


## 📚 概述

Service适配器层是对后端API的封装，提供类型安全、统一错误处理和易于使用的前端API调用接口。

### 核心功能

- ✅ **类型安全**: 完整的TypeScript类型定义
- ✅ **统一封装**: 所有API调用通过统一的客户端
- ✅ **错误处理**: 自动错误提示和异常处理
- ✅ **认证管理**: JWT token自动管理
- ✅ **拦截器**: 请求/响应拦截和处理
- ✅ **文件上传/下载**: 支持文件操作

---

## 🚀 快速开始

### 1. 基础用法

```typescript
import { marketService, technicalService, tradeService } from '@/services';

// 获取股票列表
const stocks = await marketService.getStockList({ market: 'SZ' });
console.log(stocks.data.stocks);

// 获取行情数据
const quote = await marketService.getQuote('000001.SZ');
console.log(quote.data.current_price);
```

---

### 2. 在Vue组件中使用

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { marketService } from '@/services';
import type { StockSymbol } from '@/services';

const stocks = ref<StockSymbol[]>([]);
const loading = ref(false);

const fetchStocks = async () => {
  loading.value = true;
  try {
    const response = await marketService.getStockList({ market: 'SZ' });
    stocks.value = response.data.stocks;
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchStocks();
});
</script>

<template>
  <div v-loading="loading">
    <div v-for="stock in stocks" :key="stock.symbol">
      {{ stock.symbol }} - {{ stock.name }}
    </div>
  </div>
</template>
```

---

### 3. 在Pinia Store中使用

```typescript
// stores/market.ts
import { defineStore } from 'pinia';
import { marketService } from '@/services';
import type { StockSymbol, StockQuote } from '@/services';

export const useMarketStore = defineStore('market', {
  state: () => ({
    stocks: [] as StockSymbol[],
    quotes: {} as Record<string, StockQuote>,
  }),

  actions: {
    async fetchStocks() {
      const response = await marketService.getStockList();
      this.stocks = response.data.stocks;
    },

    async fetchQuote(symbol: string) {
      const response = await marketService.getQuote(symbol);
      this.quotes[symbol] = response.data;
    },
  },
});
```

---

## 📖 API参考

### Market Service (市场数据)

#### 获取股票列表

```typescript
await marketService.getStockList({
  market: 'SZ',      // 市场代码 (可选)
  sector: '金融',     // 板块 (可选)
  industry: '银行',   // 行业 (可选)
  limit: 50,         // 每页数量
  offset: 0,         // 偏移量
});
```

#### 搜索股票

```typescript
await marketService.searchStocks('平安');
```

#### 获取行情

```typescript
// 单个股票
await marketService.getQuote('000001.SZ');

// 批量获取
await marketService.getBatchQuotes(['000001.SZ', '000002.SZ']);

// 实时行情
await marketService.getRealtimeQuotes(['000001.SZ', '000002.SZ']);
```

#### 获取K线数据

```typescript
await marketService.getKlineData({
  symbol: '000001.SZ',
  period: 'day',        // 1min, 5min, 15min, 30min, 60min, day, week, month
  start_date: '2025-01-01',
  end_date: '2025-12-31',
  limit: 100,
});
```

#### 自选股管理

```typescript
// 获取自选股
await marketService.getWatchlist();

// 添加自选股
await marketService.addToWatchlist({
  symbol: '000001.SZ',
  notes: '关注中',
});

// 删除自选股
await marketService.removeFromWatchlist(1);

// 更新备注
await marketService.updateWatchlistItem(1, '目标价: 15元');
```

---

### Technical Service (技术分析)

#### 获取MA均线

```typescript
await technicalService.getMA({
  symbol: '000001.SZ',
  periods: [5, 10, 20, 30, 60],
  start_date: '2025-01-01',
  end_date: '2025-12-31',
});
```

#### 获取MACD

```typescript
await technicalService.getMACD({
  symbol: '000001.SZ',
  fast_period: 12,
  slow_period: 26,
  signal_period: 9,
});
```

#### 获取KDJ

```typescript
await technicalService.getKDJ({
  symbol: '000001.SZ',
  k_period: 9,
  d_period: 3,
  j_period: 3,
});
```

#### 批量获取指标

```typescript
await technicalService.getBatchIndicators({
  symbol: '000001.SZ',
  indicators: ['MA', 'MACD', 'KDJ', 'BOLL'],
});
```

---

### Trade Service (交易)

#### 创建订单

```typescript
import { OrderType, OrderDirection } from '@/services';

await tradeService.createOrder({
  symbol: '000001.SZ',
  type: OrderType.LIMIT,
  direction: OrderDirection.BUY,
  price: 10.50,
  quantity: 100,
  notes: '测试订单',
});
```

#### 查询订单

```typescript
// 获取订单列表
await tradeService.getOrders({
  status: OrderStatus.PENDING,
  start_date: '2025-01-01',
  limit: 50,
});

// 获取订单详情
await tradeService.getOrder(1);
```

#### 取消订单

```typescript
// 取消单个订单
await tradeService.cancelOrder(1);

// 批量取消
await tradeService.cancelOrders([1, 2, 3]);
```

#### 持仓管理

```typescript
// 获取持仓列表
await tradeService.getPositions();

// 获取持仓详情
await tradeService.getPosition(1);

// 平仓
await tradeService.closePosition({
  position_id: 1,
  quantity: 100,
  price: 11.00,
});
```

#### 账户余额

```typescript
await tradeService.getAccountBalance();
// 返回: {
//   total_balance: 100000,
//   available_balance: 50000,
//   frozen_balance: 5000,
//   market_value: 45000,
//   profit_loss: 5000,
//   profit_loss_percent: 5.0,
// }
```

---

## 🔐 认证管理

### 设置Token

```typescript
import { setAuthToken, initAuthToken } from '@/services';

// 登录后设置token
const login = async (username: string, password: string) => {
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
  const { token } = await response.json();

  setAuthToken(token);
};

// 应用初始化时恢复token
initAuthToken();
```

### 清除Token

```typescript
import { clearAuthToken } from '@/services';

// 登出时清除token
const logout = () => {
  clearAuthToken();
  router.push('/login');
};
```

---

## 🛠️ 高级用法

### 1. 自定义请求配置

```typescript
import { apiClient } from '@/services';

// 不显示错误提示
const data = await apiClient.get('/endpoint', params, { showError: false });

// 自定义超时
const data = await apiClient.get('/endpoint', params, { timeout: 60000 });

// 添加自定义headers
const data = await apiClient.get('/endpoint', params, {
  headers: { 'X-Custom-Header': 'value' },
});
```

---

### 2. 文件上传

```typescript
import { apiClient } from '@/services';

const uploadFile = async (file: File) => {
  const response = await apiClient.upload(
    '/api/upload',
    file,
    (percent) => {
      console.log(`上传进度: ${percent}%`);
    }
  );
  return response;
};
```

---

### 3. 文件下载

```typescript
import { apiClient } from '@/services';

const downloadReport = async () => {
  await apiClient.download(
    '/api/reports/export',
    'report.pdf'
  );
};
```

---

### 4. 并发请求

```typescript
import { marketService, technicalService } from '@/services';

const fetchData = async () => {
  const [stocks, maData, macdData] = await Promise.all([
    marketService.getStockList(),
    technicalService.getMA({ symbol: '000001.SZ', periods: [5, 10, 20] }),
    technicalService.getMACD({ symbol: '000001.SZ' }),
  ]);

  return { stocks, maData, macdData };
};
```

---

### 5. 错误处理

```typescript
import { marketService } from '@/services';

const safeFetch = async () => {
  try {
    const response = await marketService.getStockList();
    return response.data;
  } catch (error) {
    // API客户端已自动显示错误提示
    // 这里可以添加自定义错误处理逻辑
    console.error('获取股票列表失败', error);

    // 返回默认值
    return { stocks: [], total: 0 };
  }
};
```

---

## 🎯 最佳实践

### 1. 在Composable中封装

```typescript
// composables/useMarketData.ts
import { ref } from 'vue';
import { marketService } from '@/services';
import type { StockSymbol } from '@/services';

export function useMarketData() {
  const stocks = ref<StockSymbol[]>([]);
  const loading = ref(false);
  const error = ref<Error | null>(null);

  const fetchStocks = async (params?: any) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await marketService.getStockList(params);
      stocks.value = response.data.stocks;
    } catch (e) {
      error.value = e as Error;
    } finally {
      loading.value = false;
    }
  };

  return {
    stocks,
    loading,
    error,
    fetchStocks,
  };
}
```

---

### 2. 请求去重

```typescript
// utils/request-cache.ts
const pendingRequests = new Map<string, Promise<any>>();

export function cachedRequest<T>(
  key: string,
  request: () => Promise<T>
): Promise<T> {
  if (pendingRequests.has(key)) {
    return pendingRequests.get(key)!;
  }

  const promise = request().finally(() => {
    pendingRequests.delete(key);
  });

  pendingRequests.set(key, promise);
  return promise;
}

// 使用
const fetchStocks = () => {
  return cachedRequest('stocks:list', () =>
    marketService.getStockList()
  );
};
```

---

### 3. 自动重试

```typescript
// utils/retry.ts
export async function retryRequest<T>(
  request: () => Promise<T>,
  maxRetries = 3,
  delay = 1000
): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await request();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, delay * (i + 1)));
    }
  }
  throw new Error('Max retries exceeded');
}

// 使用
const stocks = await retryRequest(() =>
  marketService.getStockList()
);
```

---

## 🐛 故障排除

### 问题1: 401未授权错误

**原因**: Token未设置或已过期

**解决方案**:
```typescript
import { setAuthToken, getAuthToken } from '@/services';

// 检查token
const token = getAuthToken();
if (!token) {
  router.push('/login');
} else {
  setAuthToken(token);
}
```

---

### 问题2: 网络错误

**原因**: 后端服务未启动或网络不通

**解决方案**:
```typescript
// 检查后端服务状态
fetch('/health')
  .then(res => res.json())
  .then(data => console.log('后端服务正常:', data))
  .catch(err => console.error('后端服务异常:', err));
```

---

### 问题3: 类型错误

**原因**: TypeScript类型定义与实际API响应不匹配

**解决方案**:
```bash
# 重新生成TypeScript类型定义
python scripts/generate-types/generate_ts_types.py
```

---

## 🔗 相关文档

- [TypeScript类型生成指南](./TYPESCRIPT_GENERATION_GUIDE.md)
- [API契约管理平台文档](./CONTRACT_MANAGEMENT_API.md)
- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)
- [Pinia状态管理](https://pinia.vuejs.org/)

---

**文档版本**: v1.0.0
**最后更新**: 2025-12-29
**维护者**: MyStocks Frontend Team

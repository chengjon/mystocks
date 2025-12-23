# API-前端映射文档

> **目的**: 清晰记录每个前端页面/组件调用的 API，方便问题排查和维护
> **维护**: 每次添加新功能或修复 bug 时更新此文档
> **最后更新**: 2025-11-09

---

## 📋 目录

1. [快速排查指南](#快速排查指南)
2. [页面级映射](#页面级映射)
3. [组件级映射](#组件级映射)
4. [API 状态监控](#api-状态监控)
5. [常见问题排查](#常见问题排查)

---

## 🔍 快速排查指南

### 排查 Bug 的步骤

1. **定位问题页面/组件** → 在本文档中查找对应的 API 列表
2. **检查 API 状态** → 访问 http://localhost:8000/api/docs 测试 API
3. **查看网络请求** → 浏览器 F12 → Network 标签
4. **验证请求参数** → 对比文档中的参数要求
5. **查看后端日志** → 检查 API 错误信息

### 工具链

| 工具 | 用途 | 访问方式 |
|------|------|----------|
| **Swagger UI** | 测试 API | http://localhost:8000/api/docs |
| **浏览器 DevTools** | 查看网络请求 | F12 → Network |
| **后端日志** | 查看错误详情 | `tail -f logs/app.log` |
| **本文档** | API-页面映射 | 当前文档 |

---

## 📄 页面级映射

### 1. 登录页面 (`/login`)

**文件位置**: `web/frontend/src/views/Login.vue`

**调用的 API**:

| API 端点 | HTTP方法 | 用途 | 请求参数 | 响应数据 |
|----------|---------|------|----------|----------|
| `/api/csrf-token` | GET | 获取 CSRF Token | 无 | `{csrf_token, expires_in}` |
| `/api/auth/login` | POST | 用户登录 | `{username, password}` | `{access_token, token_type}` |

**前端代码示例**:
```javascript
// Login.vue
const login = async () => {
  // 1. 获取 CSRF Token
  const csrfResponse = await axios.get('/api/csrf-token');
  const csrfToken = csrfResponse.data.csrf_token;

  // 2. 登录
  const response = await axios.post('/api/auth/login', {
    username: username.value,
    password: password.value
  }, {
    headers: {
      'X-CSRF-Token': csrfToken
    }
  });

  // 3. 保存 JWT Token
  localStorage.setItem('jwt_token', response.data.access_token);
};
```

**常见 Bug**:
- ❌ **403 错误**: CSRF Token 缺失或过期 → 重新获取 CSRF Token
- ❌ **401 错误**: 用户名密码错误 → 检查凭证

---

### 2. 仪表盘页面 (`/dashboard`)

**文件位置**: `web/frontend/src/views/Dashboard.vue`

**调用的 API**:

| API 端点 | HTTP方法 | 用途 | 刷新频率 | 依赖组件 |
|----------|---------|------|----------|----------|
| `/api/market/realtime` | GET | 实时行情 | 5秒 | MarketOverview |
| `/api/cache/stats` | GET | 缓存统计 | 30秒 | SystemStats |
| `/api/monitoring/metrics` | GET | 系统指标 | 10秒 | MetricsChart |
| `/api/sse/dashboard` | SSE | 实时推送 | 流式 | RealtimePanel |

**前端代码示例**:
```javascript
// Dashboard.vue
import { useMarketStore } from '@/stores/market';

const marketStore = useMarketStore();

// 定时刷新实时行情
setInterval(async () => {
  await marketStore.fetchRealtimeData();
}, 5000);

// SSE 实时推送
const eventSource = new EventSource('/api/sse/dashboard');
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // 更新仪表盘数据
};
```

**常见 Bug**:
- ❌ **数据不刷新**: 检查定时器是否正常工作
- ❌ **SSE 断连**: 检查网络连接和服务器状态
- ❌ **性能问题**: 刷新频率过高，考虑降低频率

---

### 3. 市场数据页面 (`/market`)

**文件位置**: `web/frontend/src/views/MarketData.vue`

**调用的 API**:

| API 端点 | HTTP方法 | 用途 | 触发时机 | 相关组件 |
|----------|---------|------|----------|----------|
| `/api/market/realtime` | GET | 实时行情列表 | 页面加载, 每5秒 | MarketTable |
| `/api/market/kline` | GET | K线数据 | 点击股票 | KLineChart |
| `/api/market/fund-flow` | GET | 资金流向 | 切换标签 | FundFlowTable |
| `/api/market/industry-fund-flow` | GET | 行业资金流向 | 切换到行业视图 | IndustryFundFlow |
| `/api/market/etf/list` | GET | ETF列表 | 切换到ETF标签 | ETFTable |
| `/api/market/chip-distribution` | GET | 筹码分布 | 点击"筹码"按钮 | ChipChart |

**前端代码示例**:
```javascript
// MarketData.vue
const fetchMarketData = async (symbols: string) => {
  try {
    const response = await axios.get('/api/market/realtime', {
      params: { symbols },
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
      }
    });
    marketData.value = response.data.data;
  } catch (error) {
    console.error('获取市场数据失败:', error);
    ElMessage.error('获取市场数据失败');
  }
};

// K线图
const showKLine = async (symbol: string) => {
  const response = await axios.get('/api/market/kline', {
    params: {
      symbol,
      period: 'day',
      start_date: '2025-01-01',
      end_date: new Date().toISOString().split('T')[0]
    }
  });
  klineData.value = response.data.data;
};
```

**常见 Bug**:
- ❌ **K线图不显示**: 检查日期参数格式
- ❌ **资金流向数据为空**: 检查 `industry_type` 参数
- ❌ **实时行情延迟**: 检查刷新间隔和网络延迟

---

### 4. 技术分析页面 (`/technical-analysis`)

**文件位置**: `web/frontend/src/views/TechnicalAnalysis.vue`

**调用的 API**:

| API 端点 | HTTP方法 | 用途 | 请求参数 | 响应字段 |
|----------|---------|------|----------|----------|
| `/api/indicators/calculate` | POST | 计算技术指标 | `{symbol, indicators, period}` | `{MA, MACD, RSI, ...}` |
| `/api/indicators/ma` | GET | 移动平均线 | `{symbol, periods}` | `{MA5, MA10, MA20, ...}` |
| `/api/indicators/macd` | GET | MACD 指标 | `{symbol}` | `{DIF, DEA, MACD}` |
| `/api/indicators/rsi` | GET | RSI 指标 | `{symbol, period}` | `{RSI6, RSI12, RSI24}` |
| `/api/indicators/kdj` | GET | KDJ 指标 | `{symbol}` | `{K, D, J}` |
| `/api/indicators/boll` | GET | 布林带 | `{symbol}` | `{upper, middle, lower}` |

**前端代码示例**:
```javascript
// TechnicalAnalysis.vue
const calculateIndicators = async () => {
  const response = await axios.post('/api/indicators/calculate', {
    symbol: selectedStock.value,
    indicators: ['MA', 'MACD', 'RSI', 'KDJ', 'BOLL'],
    period: 'day'
  }, {
    headers: {
      'Authorization': `Bearer ${jwtToken}`,
      'X-CSRF-Token': csrfToken
    }
  });

  // 更新图表数据
  chartData.value = response.data.data;
};
```

**常见 Bug**:
- ❌ **指标计算失败**: 检查股票代码格式
- ❌ **图表不更新**: 检查响应数据结构
- ❌ **参数错误**: 检查 period 参数值

---

### 5. 自选股页面 (`/watchlist`)

**文件位置**: `web/frontend/src/views/Watchlist.vue`

**调用的 API**:

| API 端点 | HTTP方法 | 用途 | 触发时机 |
|----------|---------|------|----------|
| `/api/watchlist/groups` | GET | 获取自选股分组 | 页面加载 |
| `/api/watchlist/groups` | POST | 创建分组 | 点击"新建分组" |
| `/api/watchlist/stocks` | GET | 获取某分组的股票 | 切换分组 |
| `/api/watchlist/stocks` | POST | 添加股票到分组 | 点击"添加" |
| `/api/watchlist/stocks/{id}` | DELETE | 删除股票 | 点击"删除" |

**前端代码示例**:
```javascript
// Watchlist.vue
// 获取自选股分组
const fetchGroups = async () => {
  const response = await axios.get('/api/watchlist/groups');
  groups.value = response.data.data;
};

// 添加股票到自选
const addStock = async (symbol: string, groupId: number) => {
  await axios.post('/api/watchlist/stocks', {
    symbol,
    group_id: groupId
  }, {
    headers: {
      'Authorization': `Bearer ${jwtToken}`,
      'X-CSRF-Token': csrfToken
    }
  });

  ElMessage.success('添加成功');
  await fetchStocks(groupId);
};
```

**常见 Bug**:
- ❌ **添加失败**: 检查 CSRF Token
- ❌ **删除不生效**: 检查 ID 参数
- ❌ **分组列表为空**: 检查用户认证状态

---

### 6. 缓存管理页面 (`/cache-management`)

**文件位置**: `web/frontend/src/views/CacheManagement.vue`

**调用的 API**:

| API 端点 | HTTP方法 | 用途 | 刷新频率 |
|----------|---------|------|----------|
| `/api/cache/stats` | GET | 缓存统计 | 10秒 |
| `/api/cache/read` | GET | 读取缓存 | 按需 |
| `/api/cache/write` | POST | 写入缓存 | 按需 |
| `/api/cache/evict` | DELETE | 淘汰缓存 | 按需 |
| `/api/cache/clear` | POST | 清空缓存 | 手动触发 |
| `/api/cache/warmup` | POST | 缓存预热 | 手动触发 |
| `/api/cache/hot-keys` | GET | 热点数据 | 30秒 |
| `/api/cache/health` | GET | 健康检查 | 15秒 |

**前端代码示例**:
```javascript
// CacheManagement.vue
const fetchCacheStats = async () => {
  const response = await axios.get('/api/cache/stats');
  stats.value = response.data.data;
};

// 清空缓存
const clearCache = async () => {
  await ElMessageBox.confirm('确定要清空所有缓存吗？', '警告');

  await axios.post('/api/cache/clear', {}, {
    headers: {
      'Authorization': `Bearer ${jwtToken}`,
      'X-CSRF-Token': csrfToken
    }
  });

  ElMessage.success('缓存已清空');
  await fetchCacheStats();
};
```

**常见 Bug**:
- ❌ **统计数据不更新**: 检查定时器
- ❌ **清空失败**: 检查权限和 CSRF Token
- ❌ **预热超时**: 增加请求超时时间

---

## 🧩 组件级映射

### MarketTable 组件

**文件**: `web/frontend/src/components/MarketTable.vue`

**调用的 API**: `/api/market/realtime`

**Props 接收**:
```typescript
interface Props {
  symbols?: string[];
  autoRefresh?: boolean;
  refreshInterval?: number;
}
```

**使用示例**:
```vue
<MarketTable
  :symbols="['000001.SZ', '600000.SH']"
  :auto-refresh="true"
  :refresh-interval="5000"
/>
```

---

### KLineChart 组件

**文件**: `web/frontend/src/components/KLineChart.vue`

**调用的 API**: `/api/market/kline`

**Props 接收**:
```typescript
interface Props {
  symbol: string;
  period: 'minute' | 'day' | 'week' | 'month';
  startDate?: string;
  endDate?: string;
}
```

---

### TechnicalIndicators 组件

**文件**: `web/frontend/src/components/TechnicalIndicators.vue`

**调用的 API**: `/api/indicators/calculate`

**Props 接收**:
```typescript
interface Props {
  symbol: string;
  indicators: string[];
  period: string;
}
```

---

## 📊 API 状态监控

### 健康检查脚本

创建一个简单的健康检查脚本：

```bash
#!/bin/bash
# 文件: scripts/check_api_health.sh

BASE_URL="http://localhost:8000"

echo "=== MyStocks API 健康检查 ==="
echo

# 1. 系统健康检查
echo "1. 系统健康检查..."
curl -s $BASE_URL/health | jq '.'

# 2. CSRF Token
echo -e "\n2. CSRF Token 端点..."
curl -s $BASE_URL/api/csrf-token | jq '.csrf_token' | head -c 20
echo "..."

# 3. 检查主要 API 端点
echo -e "\n\n3. 检查主要 API 端点..."

endpoints=(
  "/api/market/realtime"
  "/api/cache/stats"
  "/api/indicators/ma"
  "/api/watchlist/groups"
  "/api/monitoring/metrics"
)

for endpoint in "${endpoints[@]}"; do
  echo -n "  $endpoint: "
  status=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL$endpoint)
  if [ $status -eq 401 ]; then
    echo "🔒 需要认证 (正常)"
  elif [ $status -eq 200 ]; then
    echo "✅ 正常"
  else
    echo "❌ 异常 ($status)"
  fi
done

echo -e "\n=== 检查完成 ==="
```

**使用方法**:
```bash
chmod +x scripts/check_api_health.sh
./scripts/check_api_health.sh
```

---

## 🔧 常见问题排查

### 问题 1: API 返回 401 Unauthorized

**原因**: JWT Token 缺失或过期

**排查步骤**:
1. 检查 localStorage 中是否有 `jwt_token`
2. 检查请求头是否包含 `Authorization: Bearer <token>`
3. 重新登录获取新 Token

**修复代码**:
```javascript
// 添加 axios 拦截器
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('jwt_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// 处理 401 错误
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('jwt_token');
      router.push('/login');
    }
    return Promise.reject(error);
  }
);
```

---

### 问题 2: API 返回 403 Forbidden

**原因**: CSRF Token 缺失或无效

**排查步骤**:
1. 检查请求头是否包含 `X-CSRF-Token`
2. 检查 CSRF Token 是否过期
3. 重新获取 CSRF Token

**修复代码**:
```javascript
// 全局 CSRF Token 管理
let csrfToken = null;

const getCsrfToken = async () => {
  if (!csrfToken) {
    const response = await axios.get('/api/csrf-token');
    csrfToken = response.data.csrf_token;

    // 1小时后过期
    setTimeout(() => {
      csrfToken = null;
    }, 3600 * 1000);
  }
  return csrfToken;
};

// 在 POST/PUT/DELETE 请求前获取
const submitForm = async (data) => {
  const token = await getCsrfToken();
  await axios.post('/api/endpoint', data, {
    headers: {
      'X-CSRF-Token': token
    }
  });
};
```

---

### 问题 3: 数据加载缓慢

**原因**: API 响应慢或前端轮询过于频繁

**排查步骤**:
1. 浏览器 DevTools → Network → 查看请求耗时
2. 检查是否有不必要的重复请求
3. 检查刷新间隔是否过短

**优化建议**:
```javascript
// 使用防抖避免频繁请求
import { debounce } from 'lodash';

const fetchData = debounce(async () => {
  // API 调用
}, 500);

// 使用 SWR 策略 (Stale-While-Revalidate)
const useSWR = (key, fetcher, options = {}) => {
  const { data, error, mutate } = useSWRVanilla(key, fetcher, {
    refreshInterval: options.refreshInterval || 0,
    revalidateOnFocus: false,
    dedupingInterval: 2000  // 2秒内不重复请求
  });

  return { data, error, mutate };
};
```

---

### 问题 4: SSE 连接断开

**原因**: 网络超时或服务器重启

**排查步骤**:
1. 检查 EventSource 连接状态
2. 检查服务器日志
3. 检查网络稳定性

**修复代码**:
```javascript
// 自动重连 SSE
const connectSSE = (url) => {
  let eventSource;
  let reconnectAttempts = 0;
  const maxReconnectAttempts = 5;

  const connect = () => {
    eventSource = new EventSource(url);

    eventSource.onopen = () => {
      console.log('SSE connected');
      reconnectAttempts = 0;
    };

    eventSource.onerror = (error) => {
      console.error('SSE error:', error);
      eventSource.close();

      // 自动重连
      if (reconnectAttempts < maxReconnectAttempts) {
        reconnectAttempts++;
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
        console.log(`Reconnecting in ${delay}ms...`);
        setTimeout(connect, delay);
      } else {
        ElMessage.error('SSE 连接失败，请刷新页面');
      }
    };

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // 处理消息
    };
  };

  connect();

  // 返回关闭函数
  return () => {
    if (eventSource) {
      eventSource.close();
    }
  };
};
```

---

## 📝 维护指南

### 添加新页面时

1. **在本文档中添加新的页面映射**
2. **列出所有调用的 API**
3. **提供代码示例**
4. **记录常见问题**

### 修复 Bug 时

1. **更新本文档中的"常见 Bug"部分**
2. **添加问题原因和解决方案**
3. **提供修复代码**

### 定期维护

- **每周**: 检查 API 健康状态
- **每月**: 更新文档，移除已废弃的 API
- **每季度**: 重新审查 API-前端映射，优化调用方式

---

## 🔗 相关文档

- **API 完整文档**: [API_GUIDE.md](./API_GUIDE.md)
- **OpenAPI 规范**: [openapi.json](./openapi.json)
- **Swagger UI**: http://localhost:8000/api/docs
- **项目 README**: [../../README.md](../../README.md)

---

**最后更新**: 2025-11-09
**维护者**: 开发团队
**版本**: 1.0.0

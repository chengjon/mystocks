# MyStocks Web 功能与数据打通实施指南

**版本**: 2.0
**更新日期**: 2025-12-30
**目标**: 完成 209 个 API 端点与 Web 页面的真实数据打通

---

## 📋 目录

1. [项目背景与现状](#项目背景与现状)
2. [API 模块架构](#api-模块架构)
3. [实施路线图](#实施路线图)
4. [Phase 1: API 目录标准化](#phase-1-api-目录标准化)
5. [Phase 2: 契约测试体系](#phase-2-契约测试体系)
6. [Phase 3: 自动化测试框架](#phase-3-自动化测试框架)
7. [Phase 4: 数据源打通](#phase-4-数据源打通)
8. [Phase 5: Web 页面集成](#phase-5-web-页面集成)
9. [工具配置](#工具配置)
10. [检查清单](#检查清单)

---

## 项目背景与现状

### 核心成果 (已实现)

| 组件 | 状态 | 说明 |
|------|------|------|
| Web 页面 | ✅ | 前端界面已开发，使用 Mock 数据 |
| API 接口 | ✅ | 209 个 API 已实现 |
| API 契约管理 | ✅ | 版本管理、差异检测、验证、sync |
| 指标管理体系 | ✅ | 47 个技术指标 |
| 数据库支持 | ✅ | PostgreSQL + TDengine |
| Playwright 测试 | ✅ | 已配置 E2E 测试框架 |

### 当前挑战

| 问题 | 严重程度 | 影响 |
|------|----------|------|
| 262 个 TypeScript 错误 | 🔴 高 | 类型安全不足 |
| 仅 5% API 覆盖率 | 🔴 高 | 缺乏全面测试 |
| 4 个契约注册 | 🟡 中 | 契约管理不完整 |
| 手动类型生成 | 🟡 中 | 效率低、易出错 |
| Mock 数据依赖 | 🟡 中 | 未对接真实数据 |

### 已注册契约

| 契约名称 | 模块 | API 数量 |
|----------|------|----------|
| market-data | 行情数据 | 40+ |
| trading | 交易委托 | 30+ |
| technical-analysis | 技术分析 | 8+ |
| strategy-management | 策略管理 | 50+ |

---

## API 模块架构

### 业务模块分布 (共 209 个 API)

| 模块 | 路由前缀 | API 数量 | 优先级 | 数据状态 |
|------|----------|----------|--------|----------|
| 行情数据 | `/api/market/` | 40+ | P0 | Hybrid |
| 策略管理 | `/api/strategy/` | 50+ | P0 | Hybrid |
| 交易委托 | `/api/trade/` | 30+ | P0 | Mock |
| 用户账户 | `/api/user/` | 25+ | P1 | Real |
| 技术指标 | `/api/indicators/` | 35+ | P1 | Real |
| 系统配置 | `/api/system/` | 29+ | P2 | Mock |

### API 分类统计

| 类别 | 模块数 | 接口数量 |
|------|--------|----------|
| 监控系统 | 17 个 | 100% 文档化 |
| 数据管理 | 15 个 | 100% 文档化 |
| 技术分析 | 8 个 | 100% 文档化 |
| 多数据源 | 9 个 | 100% 文档化 |
| AI 策略 | 12 个 | 100% 文档化 |
| GPU 加速 | 8 个 | 100% 文档化 |

---

## 实施路线图

```
12 周实施计划

Week 1-2: Phase 4 - TypeScript 类型整理
├── 类型错误修复 (262 → <50)
├── ECharts 类型标准化
└── Element Plus 兼容性

Week 3: Phase 4.3-4.5 - 契约对齐
├── 契约类型对齐
├── 适配层创建
└── 严格类型检查启用

Week 4-5: Phase 5 - 契约测试
├── 契约验证测试套件
├── 4 个注册 API 测试
└── CI/CD 集成

Week 6: Phase 6 - 开发者体验
├── Pre-commit hooks
├── 代码生成器
└── 一键契约注册

Week 7-12: Phase 7 - 完整 API 注册
├── P0: trading, market, data (30 APIs)
├── P1: backtest, risk (25 APIs)
└── P2: indicators, announcement (40 APIs)
```

### 成功指标

| 指标 | 当前 | Phase 4 后 | Phase 7 后 |
|------|------|------------|------------|
| TypeScript 错误 | 262 | <50 | <20 |
| 契约覆盖率 | 5% | 5% | 60% |
| 已注册 API | 4 | 4 | 115 |
| 类型安全 | ~40% | >90% | >95% |

---

## Phase 1: API 目录标准化

### 1.1 生成 API 目录

```bash
# 生成完整 API 目录
cd web/backend
python scripts/generate_api_catalog.py

# 输出文件
docs/api/catalog.yaml    # YAML 格式 (机器可读)
docs/api/catalog.md      # Markdown 格式 (文档阅读)
```

### 1.2 API 契约核心字段标准

```yaml
# 契约字段定义 (api_id, module, path, method, request_params, etc.)
api_id: market_kline_v1                    # 唯一标识
module: market                             # 业务模块
path: /api/market/kline                    # 路由路径
method: GET                                # 请求方式
request_params:                            # 请求参数
  - name: symbol
    type: string
    required: true
    desc: 股票代码/BTC
response_code:                             # 响应码
  200: 成功
  20101: 标的不存在
response_data:                             # 响应数据格式
  kline: []
  sma: []
  timestamp: []
contract_version: v1.0                     # 契约版本
is_core: true                              # 是否核心 API
```

### 1.3 批量路由扫描

```python
# scripts/scan_routes.py
import os
import csv
from fastapi.openapi.utils import get_openapi
from app.main import app

# 生成路由清单
schema = get_openapi(
    title=app.title,
    version=app.version,
    routes=app.routes
)

route_list = []
for path, methods in schema.get("paths", {}).items():
    for method, details in methods.items():
        if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            route_list.append({
                "path": path,
                "method": method.upper(),
                "summary": details.get("summary", ""),
                "tags": details.get("tags", [])
            })

# 导出到 CSV
with open("api_route_list.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["path", "method", "summary", "tags"])
    writer.writeheader()
    writer.writerows(route_list)

print(f"已扫描到 {len(route_list)} 个 API 路由")
```

### 1.4 契约注册

```python
from app.api.contract.services.contract_registry import contract_registry

# 注册所有端点
result = contract_registry.register_from_openapi(schema)
print(f"已注册: {result['registered']} 个端点")
print(f"未注册: {result['skipped']} 个端点")
```

---

## Phase 2: 契约测试体系

### 2.1 测试金字塔

```
┌─────────────────────┐
│   Playwright E2E    │  (20%：关键业务流程)
│     20-30 个用例     │
├─────────────────────┤
│  API 契约测试        │  (60%：209 个 API 端点)
│   150-180 个测试     │
├─────────────────────┤
│   单元测试           │  (20%：核心业务逻辑)
│   覆盖关键算法       │
└─────────────────────┘
```

### 2.2 契约测试实现

```python
# tests/api/test_contract_consistency.py
import pytest
from playwright.sync_api import sync_playwright


@pytest.mark.contract
def test_market_kline_contract(api):
    """测试 K 线 API 契约一致性"""
    response = api.get("/api/market/kline", params={
        "symbol": "000001",
        "period": "1d",
        "start_ts": 1735689600000,
        "end_ts": 1736294400000
    })

    assert response.ok

    # 契约验证
    result = contract_validator.validate_response(
        path="/api/market/kline",
        method="GET",
        status_code="200",
        response_data=response.json()
    )

    assert result.success, f"契约违规: {result.errors}"


@pytest.mark.contract
def test_indicator_calculation_contract(api):
    """测试指标计算 API 契约"""
    response = api.post("/api/indicators/calculate", data={
        "code": "000001",
        "indicator": "sma",
        "period": 5
    })

    assert response.ok
    data = response.json()

    # 验证响应结构符合契约
    assert "value" in data
    assert "timestamp" in data
```

### 2.3 批量契约测试

```python
def test_all_registered_contracts():
    """测试所有已注册的契约"""
    endpoints = contract_validator.get_endpoint_schema_paths()

    for endpoint in endpoints:
        for status_code, schema in endpoint.get("responses", {}).items():
            if status_code == "default":
                continue

            # 为每个端点生成测试
            test_case = {
                "test_name": f"test_{endpoint['method'].lower()}_{endpoint['path'].replace('/', '_')}_{status_code}",
                "path": endpoint["path"],
                "method": endpoint["method"],
                "status_code": status_code
            }

            # 执行测试
            execute_contract_test(test_case)
```

---

## Phase 3: 自动化测试框架

### 3.1 工具分工

| 工具 | 角色 | 场景 |
|------|------|------|
| PM2 | 服务管理 | API 服务进程管理、日志收集 |
| tmux | 多窗口管理 | 并行监控 API/Web/日志/测试 |
| lnav | 日志分析 | 实时日志筛选、错误定位 |
| Playwright | 测试执行 | API 契约测试 + E2E 测试 |

### 3.2 tmux 会话配置

```bash
# 创建测试会话
tmux new-session -d -s "mystocks-test"

# 窗口 0: API 服务监控
tmux rename-window -t "mystocks-test:0" 'API'
tmux send-keys -t "mystocks-test:0" "pm2 monit" Enter

# 窗口 1: Web 服务
tmux new-window -t "mystocks-test" -n 'Web'
tmux send-keys -t "mystocks-test:1" "npm run dev" Enter

# 窗口 2: 日志监控
tmux new-window -t "mystocks-test" -n 'Logs'
tmux send-keys -t "mystocks-test:2" "lnav -q /opt/claude/mystocks_spec/var/log/" Enter

# 窗口 3: 测试执行
tmux new-window -t "mystocks-test" -n 'Test'
tmux send-keys -t "mystocks-test:3" "cd /opt/claude/mystocks_spec" Enter

# 布局
tmux select-layout -t "mystocks-test" even-horizontal
```

### 3.3 运行测试

```bash
# API 契约测试
pytest tests/api/test_contract_consistency.py -v

# 全量 API 测试
pytest tests/api/ --api-base-url=http://localhost:8020 -v

# E2E 测试
pytest tests/e2e/ -v

# 生成报告
pytest tests/api/ --html=playwright-report/api/test_report.html
```

### 3.4 日志分析

```bash
# 使用 lnav 分析日志
lnav /opt/claude/mystocks_spec/var/log/backend-access.log

# 筛选错误
:filter-in ERROR

# 按模块筛选
:filter-in path=/api/market/

# 导出分析结果
:write-to /tmp/api_analysis.txt
```

---

## Phase 4: 数据源打通

### 4.1 数据源配置

```python
# config/data_sources.json
{
  "modules": [
    {
      "name": "market",
      "data_source": "hybrid",
      "fallback": "mock",
      "cache_ttl": 60
    },
    {
      "name": "strategy",
      "data_source": "hybrid",
      "fallback": "mock",
      "cache_ttl": 300
    },
    {
      "name": "indicators",
      "data_source": "real",
      "fallback": "mock",
      "cache_ttl": 600
    }
  ]
}
```

### 4.2 渐进式切换策略

```
Week 1: API 契约对齐
├── 前端 Mock 服务改造为契约验证代理
├── 契约一致性检查
└── 自动生成 TypeScript 类型

Week 2: 关键功能切换
├── 选择 3-5 个核心页面
├── 实施熔断机制
└── 并行运行验证

Week 3: 全面切换
├── 分批迁移
├── 性能监控
└── 用户体验优化
```

### 4.3 数据适配层

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

### 4.4 Mock 数据模块清单

| 模块 | 当前 | 目标 | 优先级 | 切换计划 |
|------|------|------|--------|----------|
| stock_search | Mock | Real | P0 | Week 2 |
| trading | Mock | Hybrid | P0 | Week 2 |
| monitoring | Mock | Real | P0 | Week 2 |
| wencai | Mock | Mock | P2 | Week 4 |
| tasks | Mock | Real | P1 | Week 3 |

---

## Phase 5: Web 页面集成

### 5.1 API 客户端

```typescript
// src/api/client.ts
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8020',
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

### 5.2 数据 Hook

```typescript
// src/hooks/useMarketData.ts
import { useQuery, useMutation } from '@tanstack/react-query'
import api from '@/api/client'
import { adaptKlineData } from '@/utils/dataAdapter'

export function useKlineData(symbol: string, period: string) {
  return useQuery({
    queryKey: ['kline', symbol, period],
    queryFn: async () => {
      const response = await api.get('/api/market/kline', {
        params: { symbol, period }
      })
      return adaptKlineData(response.data)
    },
    staleTime: 60 * 1000,
    retry: 2,
  })
}

export function useIndicatorCalculate() {
  return useMutation({
    mutationFn: (params: {
      code: string
      indicator: string
      period: number
    }) => api.post('/api/indicators/calculate', params),
  })
}
```

### 5.3 页面集成示例

```vue
<!-- src/pages/Market.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import { useKlineData } from '@/hooks/useMarketData'
import KlineChart from '@/components/KlineChart.vue'
import IndicatorPanel from '@/components/IndicatorPanel.vue'

const props = defineProps<{ symbol: string }>()

const { data: kline, isLoading, error } = useKlineData(props.symbol, '1d')

function handleIndicatorSelect(indicator: string) {
  // 切换指标
}
</script>

<template>
  <div class="market-page">
    <div v-if="isLoading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">错误: {{ error.message }}</div>

    <div v-else class="content">
      <KlineChart :data="kline" />
      <IndicatorPanel @select="handleIndicatorSelect" />
    </div>
  </div>
</template>
```

---

## 工具配置

### PM2 生态系统

```javascript
// ecosystem.config.js
module.exports = {
  apps: [
    {
      name: 'mystocks-api',
      script: 'uvicorn',
      args: 'app.main:app --host 0.0.0.0 --port 8020',
      cwd: '/opt/claude/mystocks_spec/web/backend',
      interpreter: 'python',
      instances: 2,
      exec_mode: 'cluster',
      env: { PYTHONPATH: '/opt/claude/mystocks_spec/web/backend' },
      watch: false,
      max_memory_restart: '500M',
      log_file: '/opt/claude/mystocks_spec/var/log/backend-access.log',
      error_file: '/opt/claude/mystocks_spec/var/log/backend-error.log'
    },
    {
      name: 'mystocks-web',
      script: 'npm',
      args: 'run dev',
      cwd: '/opt/claude/mystocks_spec/web/frontend',
      interpreter: 'node',
      env: { NODE_ENV: 'development', PORT: 5173 }
    }
  ]
}
```

### Playwright 配置

```typescript
// playwright.config.ts
export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  retries: 2,
  reporter: 'html',

  use: {
    baseURL: 'http://localhost:8020',
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
})
```

---

## 检查清单

### Week 1-2: Phase 4.1-4.2
- [ ] 修复 Generated Types 导出 (10 个错误)
- [ ] ECharts 类型标准化 (20 个错误)
- [ ] Element Plus 兼容性 (5 个错误)
- [ ] TypeScript 错误: 262 → ~150

### Week 3: Phase 4.3-4.5
- [ ] 契约类型对齐 (50 个错误)
- [ ] 创建适配层
- [ ] 启用严格类型检查
- [ ] TypeScript 错误: ~150 → <50

### Week 4-5: Phase 5
- [ ] 契约验证测试套件
- [ ] 4 个注册 API 测试覆盖
- [ ] CI/CD 集成
- [ ] API 测试覆盖率 >80%

### Week 6: Phase 6
- [ ] Pre-commit hooks
- [ ] 代码生成器
- [ ] 一键契约注册

### Week 7-12: Phase 7
- [ ] P0 APIs 注册 (30 个)
- [ ] P1 APIs 注册 (25 个)
- [ ] P2 APIs 注册 (40 个)
- [ ] API 注册总数达到 115 个

---

## 快速启动

```bash
# 一键启动所有服务
./scripts/start-system.sh --all

# 创建 tmux 开发会话
./scripts/start-system.sh --tmux

# 运行契约测试
./scripts/start-system.sh --test

# 生成 API 目录
./scripts/start-system.sh --catalog
```

---

## 相关文档

- [Next Development Phases](../api/NEXT_PHASES_EXECUTIVE_SUMMARY.md)
- [API 开发与安全规范](./API开发与安全规范.md)
- [Web 契约开发方案](./web契约开发方案.md)
- [Web 路由与契约开发](./web路由+契约开发.md)

---

*文档版本: 2.0*
*最后更新: 2025-12-30*
*状态: Phase 4 准备开始*

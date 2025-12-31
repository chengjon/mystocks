# API 契约测试套件

## 概述

本目录包含 MyStocks API 的契约一致性测试套件，用于验证 API 实现与 OpenAPI 规范的一致性。

## 测试覆盖

### 已实现测试

#### P0 - 核心API（100%覆盖）
- ✅ 认证 API (`auth.spec.ts`)
  - `/api/auth/login` - 用户登录
  - `/api/auth/logout` - 用户登出
  - `/api/auth/me` - 获取当前用户信息
  - `/api/auth/refresh` - 刷新Token

- ✅ 系统 API (`system.spec.ts`)
  - `/api/system/health` - 系统健康检查
  - `/api/system/architecture` - 系统架构信息
  - `/api/system/datasources` - 数据源列表
  - `/api/system/database/health` - 数据库健康检查
  - `/api/system/database/stats` - 数据库统计
  - `/api/system/logs` - 系统日志
  - `/api/system/logs/summary` - 日志摘要
  - `/api/metrics` - 系统指标
  - `/api/pool-monitoring/health` - 连接池健康检查
  - `/api/pool-monitoring/postgresql/stats` - PostgreSQL连接池统计
  - `/api/pool-monitoring/tdengine/stats` - TDengine连接池统计

#### P1 - 重要API（80%覆盖）
- ✅ 市场数据 API (`market.spec.ts`)
  - `/api/market/quotes` - 获取实时行情
  - `/api/market/kline` - 获取K线数据
  - `/api/market/stocks` - 获取股票列表
  - `/api/market/fund-flow` - 获取资金流向
  - `/api/market/etf/list` - 获取ETF列表

- ✅ 技术指标 API (`technical.spec.ts`)
  - `/api/technical/{symbol}/indicators` - 获取技术指标
  - `/api/technical/{symbol}/trend` - 获取趋势分析
  - `/api/technical/{symbol}/signals` - 获取交易信号
  - `/api/technical/{symbol}/volume` - 获取成交量分析
  - `/api/technical/{symbol}/momentum` - 获取动量分析
  - `/api/technical/{symbol}/volatility` - 获取波动率分析
  - `/api/technical/batch/indicators` - 批量获取指标
  - `/api/technical/{symbol}/history` - 获取历史指标
  - `/api/technical/patterns/{symbol}` - 获取K线形态

- ✅ 问财 API (`wencai.spec.ts`)
  - `/api/market/wencai/query` - 执行问财查询
  - `/api/market/wencai/queries` - 获取查询列表
  - `/api/market/wencai/queries/{query_name}` - 获取特定查询
  - `/api/market/wencai/results/{query_name}` - 获取查询结果
  - `/api/market/wencai/history/{query_name}` - 获取查询历史
  - `/api/market/wencai/custom-query` - 执行自定义查询
  - `/api/market/wencai/refresh/{query_name}` - 刷新查询结果
  - `/api/market/wencai/health` - 问财服务健康检查

- ✅ 策略 API (`strategy.spec.ts`)
  - `/api/strategy/definitions` - 获取策略定义
  - `/api/strategy/run/single` - 执行单个策略
  - `/api/strategy/run/batch` - 批量执行策略
  - `/api/strategy/matched-stocks` - 获取匹配股票列表
  - `/api/strategy/results` - 获取策略执行结果
  - `/api/strategy/stats/summary` - 获取策略统计摘要

- ✅ 回测 API (`backtest.spec.ts`)
  - `/api/v1/strategy/backtest/run` - 运行回测
  - `/api/v1/strategy/backtest/results` - 获取回测结果列表
  - `/api/v1/strategy/backtest/results/{backtest_id}` - 获取特定回测结果
  - `/api/v1/strategy/backtest/results/{backtest_id}/chart-data` - 获取图表数据
  - `/api/v1/sse/backtest` - SSE回测进度推送

- ✅ 缓存 API (`cache.spec.ts`)
  - `/api/cache/status` - 获取缓存状态
  - `/api/cache/{symbol}/{data_type}` - 获取缓存数据
  - `/api/cache/{symbol}` - 获取股票所有缓存
  - `/api/cache/{symbol}/{data_type}/fresh` - 获取或刷新缓存
  - `/api/cache` - 获取所有缓存键
  - `/api/cache/evict/manual` - 手动淘汰缓存
  - `/api/cache/eviction/stats` - 获取缓存淘汰统计
  - `/api/cache/prewarming/trigger` - 触发缓存预热
  - `/api/cache/prewarming/status` - 获取缓存预热状态
  - `/api/cache/monitoring/metrics` - 获取缓存监控指标
  - `/api/cache/monitoring/health` - 缓存健康检查

## 测试统计

| 类别 | API数量 | 已测试 | 覆盖率 |
|------|---------|--------|--------|
| P0 核心 | 30 | 30 | 100% |
| P1 重要 | 85 | 60 | 71% |
| P2 一般 | 94 | 0 | 0% |
| **总计** | **209** | **90** | **43%** |

## 运行测试

### 前置条件

1. 启动后端服务：
```bash
cd web/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

2. 安装 Playwright 浏览器（首次运行）：
```bash
npm install
npx playwright install chromium
```

### 运行所有 API 测试

```bash
npx playwright test tests/api/
```

### 运行特定测试套件

```bash
# 认证测试
npx playwright test tests/api/auth.spec.ts

# 市场数据测试
npx playwright test tests/api/market.spec.ts

# 技术指标测试
npx playwright test tests/api/technical.spec.ts
```

### 运行测试并生成报告

```bash
npx playwright test tests/api/ --reporter=html
npx playwright show-report
```

### 在调试模式下运行

```bash
npx playwright test tests/api/ --debug
```

### 只运行失败的测试

```bash
npx playwright test tests/api/ --project=chromium --only-failed
```

## 测试配置

测试配置文件位于 `tests/api/playwright.config.ts`。

主要配置：
- `baseURL`: `http://localhost:8000` (可通过环境变量 `API_BASE_URL` 覆盖)
- `timeout`: 30000ms (30秒)
- `retries`: 1 (CI环境: 2)
- `workers`: 4 (并行执行)

## 测试数据

测试数据位于 `tests/api/fixtures/api-client.ts`。

可用测试数据：
- 认证凭证: `admin/admin123`, `user/user123`
- 测试股票代码: `600519` (茅台), `000858` (五粮液), `000001` (平安)

## 性能基准

每个API测试都会验证响应时间是否在性能基准内：

| API类型 | 基准时间 |
|---------|---------|
| 认证 | 1000ms |
| 市场数据 | 800ms |
| 技术指标 | 1500ms |
| 策略 | 1500ms |
| 问财 | 2000ms |
| 系统 | 500ms |

## 错误处理

测试使用统一的错误码定义：

```typescript
SUCCESS: 200
BAD_REQUEST: 400
UNAUTHORIZED: 401
FORBIDDEN: 403
NOT_FOUND: 404
INTERNAL_ERROR: 500
VALIDATION_ERROR: 422
```

## 下一步计划

1. 补充 P2 API 测试（94个端点）
2. 增加更多的错误场景测试
3. 添加并发测试和负载测试
4. 实现测试数据生成器
5. 集成 CI/CD 自动化测试

## 报告位置

测试报告生成位置：
- HTML报告: `playwright-report/api/`
- JSON报告: `api-test-results/results.json`
- JUnit报告: `api-test-results/junit.xml`

## 联系方式

测试相关问题请提交 issue 或联系 Test CLI。

# API契约验证计划 - Phase 2前期准备

> **历史计划说明**:
> 本文件是 API 相关的阶段性计划、路线图或方案材料，不是当前 API 契约、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`；若涉及 API 契约事实源，再以实际的 FastAPI 路由 + Pydantic Schema + `/openapi.json` 为准。
>
> 文内优先级、时间线、实施状态和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


**Historical Verification Plan Snapshot Date**: 2026-01-02
**Historical Verification Purpose Snapshot**: 在Phase 2执行前，系统化验证所有前端使用的API端点
**Historical Verification Strategy Snapshot**: API契约驱动 + 数据守卫者协调 + 问题立即报告机制

---

## 执行概览

### 分析结果

- **后端API端点总数**: 356个
- **前端实际使用**: 64个API调用
- **API利用率**: 18% (64/356)
- **数据源分布**:
  - PostgreSQL: 348个 (97.8%)
  - TDengine: 7个 (2.0%)
  - Mock: 1个 (0.3%)

### 验证目标

✅ **Primary Goal**: 确保前端使用的64个API调用：
1. 后端端点已实现（路径匹配）
2. 能够返回真实数据（非Mock）
3. 数据格式符合前端契约
4. 响应时间可接受（<500ms）

⚠️ **Secondary Goal**: 识别292个未使用API的处理策略
- 保留：系统内部使用，未来功能，管理接口
- 废弃：过时功能，重复实现
- 文档化：缺少文档的隐藏功能

---

## API核对清单（按Phase 2模块分类）

### Phase 2.1: Industry & Concept Lists (优先级: 🔴 P0)

**对应页面**: `views/Stocks.vue`
**API调用数**: 3个

| # | API对象 | 方法 | 后端端点路径 | HTTP方法 | 数据源 | 状态 |
|---|---------|------|-------------|----------|--------|------|
| 2.1.1 | `dataApi` | `getStocksIndustries` | `/api/v1/data/stocks/industries` | GET | PostgreSQL | ⏳ 待验证 |
| 2.1.2 | `dataApi` | `getStocksConcepts` | `/api/v1/data/stocks/concepts` | GET | PostgreSQL | ⏳ 待验证 |
| 2.1.3 | `dataApi` | `getStocksBasic` | `/api/v1/data/stocks/basic` | GET | PostgreSQL | ⏳ 待验证 |

**验证步骤**:
```bash
# 1. 端点存在性验证
curl -s http://localhost:8020/openapi.json | jq '.paths["/api/v1/data/stocks/industries"]'

# 2. 契约格式验证
curl -s -H "Authorization: Bearer dev-mock-token-for-development" \
     http://localhost:8020/api/v1/data/stocks/industries | jq '.'

# 3. 真实数据验证（USE_MOCK_DATA=false）
# 预期：返回数据库中的行业列表
# 如果：空数组或错误 → 立即报告给用户

# 4. 前端契约匹配验证
# 检查：web/frontend/src/api/types/generated-types.ts
# 验证：Industry接口字段匹配
```

**数据守卫者触发条件**:
- ❌ 端点返回404/405
- ❌ 端点返回500/502
- ❌ 数据为空数组（但数据库有数据）
- ❌ 字段类型不匹配
- ❌ 响应时间 > 2秒

---

### Phase 2.2: Stock List & Search (优先级: 🔴 P0)

**对应页面**: `views/Stocks.vue`
**API调用数**: 已在2.1中统计

| # | API对象 | 方法 | 参数 | 验证要点 |
|---|---------|------|------|---------|
| 2.2.1 | `dataApi` | `getStocksBasic` | `page`, `page_size` | 分页逻辑 |
| 2.2.2 | `dataApi` | `getStocksIndustries` | 无 | 行业过滤 |
| 2.2.3 | `dataApi` | `getStocksConcepts` | 无 | 概念过滤 |

**验证步骤**:
```bash
# 1. 分页测试
curl -s -H "Authorization: Bearer dev-mock-token-for-development" \
     "http://localhost:8020/api/v1/data/stocks/basic?page=1&page_size=20" | jq '.data | length'

# 2. 搜索功能（如果有独立search端点）
curl -s -H "Authorization: Bearer dev-mock-token-for-development" \
     "http://localhost:8020/api/v1/data/stocks/search?keyword=平安" | jq '.'
```

---

### Phase 2.3: K-Line Data (优先级: 🔴 P0)

**对应页面**:
- `views/TechnicalAnalysis.vue` (使用 `dataApi.getKline`)
- `components/market/ProKLineChart.vue` (使用 `marketApi.getKLineData`)

**API调用数**: 2个

| # | API对象 | 方法 | 后端端点 | 关键参数 | 状态 |
|---|---------|------|----------|---------|------|
| 2.3.1 | `dataApi` | `getKline` | `/api/v1/market/kline` | symbol, period, adjust | ⏳ 待验证 |
| 2.3.2 | `marketApi` | `getKLineData` | `/api/v1/market/kline` | 同上 | ⏳ 待验证 |

**验证步骤**:
```bash
# 1. 基础K线测试
curl -s "http://localhost:8020/api/v1/market/kline?symbol=000001&period=daily&adjust=qfq&limit=1000" | jq '.data.klines | length'

# 2. 性能限制验证（Gemini建议）
# 测试 limit 参数是否生效
curl -s "http://localhost:8020/api/v1/market/kline?symbol=000001&period=daily" | jq '.data | length'
# 预期：最多1000条（默认limit）

# 3. 数据完整性检查
# - OHLCV字段齐全
# - 日期按升序排列
# - 数据量合理（不是空的，也不是10万条）
```

**数据守卫者触发条件**:
- ❌ 返回数据点数 > 5000（可能缺少limit限制）
- ❌ 返回数据点数 = 0（但数据库有该股票数据）
- ❌ K线数据缺少OHLCV任一字段
- ❌ 数据顺序错误（未按日期升序）

---

### Dashboard相关API (优先级: 🟡 P1)

**对应页面**: `views/EnhancedDashboard.vue`
**API调用数**: 7个

| # | API对象 | 方法 | 后端端点 | 依赖模块 | 状态 |
|---|---------|------|----------|---------|------|
| 2.4.1 | `dashboardApi` | `getMarketOverview` | `/api/v1/markets/overview` | 市场概览 | ⏳ |
| 2.4.2 | `dashboardApi` | `getPriceDistribution` | `/api/v1/markets/price-distribution` | 价格分布 | ⏳ |
| 2.4.3 | `dashboardApi` | `getHotIndustries` | `/api/v1/markets/hot-industries` | 热门行业 | ⏳ |
| 2.4.4 | `dashboardApi` | `getHotConcepts` | `/api/v1/markets/hot-concepts` | 热门概念 | ⏳ |
| 2.4.5 | `dashboardApi` | `getWatchlist` | `/watchlist/symbols` | 监控列表 | ⏳ |
| 2.4.6 | `dashboardApi` | `addToWatchlist` | POST `/watchlist/add` | 添加监控 | ⏳ |
| 2.4.7 | `dashboardApi` | `removeFromWatchlist` | DELETE `/watchlist/{symbol}` | 移除监控 | ⏳ |

**注意**: Dashboard数据可能依赖复杂的数据聚合，验证时重点关注：
- 聚合查询性能（是否超时）
- 数据新鲜度（是否实时更新）
- 缓存策略（是否命中缓存）

---

### Strategy相关API (优先级: 🟢 P2)

**涉及页面**:
- `views/BacktestAnalysis.vue` (4个API)
- `views/strategy/*.vue` (多个页面)

**核心API列表**:

| # | API对象 | 方法 | 后端端点 | 状态 |
|---|---------|------|----------|------|
| 2.5.1 | `strategyApi` | `getDefinitions` | `/api/v1/strategy/definitions` | ⏳ |
| 2.5.2 | `strategyApi` | `getBacktestResults` | `/api/v1/backtest/results` | ⏳ |
| 2.5.3 | `strategyApi` | `runBacktest` | POST `/api/v1/backtest/run` | ⏳ |
| 2.5.4 | `strategyApi` | `getBacktestChartData` | `/api/v1/backtest/results/{id}/chart-data` | ⏳ |
| 2.5.5 | `strategyApi` | `runSingle` | POST `/api/v1/strategy/run/single` | ⏳ |
| 2.5.6 | `strategyApi` | `runBatch` | POST `/api/v1/strategy/run/batch` | ⏳ |
| 2.5.7 | `strategyApi` | `getResults` | `/api/v1/strategy/results` | ⏳ |
| 2.5.8 | `strategyApi` | `getStats` | `/api/v1/strategy/stats` | ⏳ |
| 2.5.9 | `strategyApi` | `getMatchedStocks` | `/api/v1/strategy/matched-stocks` | ⏳ |

**注意**: Strategy模块可能涉及：
- 长时间运行（backtest）
- 复杂计算（策略匹配）
- 大量数据处理（batch scan）

验证时重点关注响应时间和资源使用。

---

### Trade Management API (优先级: 🟢 P2)

**对应页面**: `views/TradeManagement.vue`
**API调用数**: 5个

| # | API对象 | 方法 | 后端端点 | 状态 |
|---|---------|------|----------|------|
| 2.6.1 | `tradeApi` | `getAccountOverview` | `/api/v1/trade/portfolio` | ⏳ |
| 2.6.2 | `tradeApi` | `getPositions` | `/api/v1/trade/positions` | ⏳ |
| 2.6.3 | `tradeApi` | `getTradeHistory` | `/api/v1/trade/trades` | ⏳ |
| 2.6.4 | `tradeApi` | `getTradeStatistics` | `/api/v1/trade/statistics` | ⏳ |
| 2.6.5 | `tradeApi` | `createOrder` | POST `/api/v1/trade/execute` | ⏳ |

**数据守卫者注意**: 交易数据敏感性高，验证时注意：
- ❌ 绝不能返回其他用户的交易数据
- ❌ 权限验证是否正确
- ❌ 金额计算是否精确

---

### Risk Monitor API (优先级: 🟢 P2)

**对应页面**: `views/RiskMonitor.vue`
**API调用数**: 6个

| # | API对象 | 方法 | 后端端点 | 状态 |
|---|---------|------|----------|------|
| 2.7.1 | `riskApi` | `getDashboard` | `/api/v1/risk/dashboard` | ⏳ |
| 2.7.2 | `riskApi` | `getMetricsHistory` | `/api/v1/risk/metrics/history` | ⏳ |
| 2.7.3 | `riskApi` | `getAlerts` | `/api/v1/risk/alerts` | ⏳ |
| 2.7.4 | `riskApi` | `getVarCvar` | POST `/api/v1/risk/var-cvar` | ⏳ |
| 2.7.5 | `riskApi` | `getBeta` | POST `/api/v1/risk/beta` | ⏳ |
| 2.7.6 | `riskApi` | `createAlert` | POST `/api/v1/risk/alerts/generate` | ⏳ |

---

### Technical Analysis API (优先级: 🟢 P2)

**对应页面**:
- `views/Analysis.vue` (7个调用)
- `views/technical/TechnicalAnalysis.vue` (2个调用)

| # | API对象 | 方法 | 后端端点 | 状态 |
|---|---------|------|----------|------|
| 2.8.1 | `technicalApi` | `getIndicators` | `/{symbol}/indicators` | ⏳ |
| 2.8.2 | `technicalApi` | `getBatchIndicators` | POST `/batch/indicators` | ⏳ |
| 2.8.3 | `technicalApi` | `getTrend` | `/{symbol}/trend` | ⏳ |
| 2.8.4 | `technicalApi` | `getMomentum` | `/{symbol}/momentum` | ⏳ |
| 2.8.5 | `technicalApi` | `getVolatility` | `/{symbol}/volatility` | ⏳ |
| 2.8.6 | `technicalApi` | `getVolume` | `/{symbol}/volume` | ⏳ |
| 2.8.7 | `technicalApi` | `getSignals` | `/{symbol}/signals` | ⏳ |

---

### Monitoring API (优先级: 🟢 P3)

**对应页面**: `views/monitoring/MonitoringDashboard.vue`
**API调用数**: 6个

| # | API对象 | 方法 | 后端端点 | 状态 |
|---|---------|------|----------|------|
| 2.9.1 | `monitoringApi` | `getSummary` | `/monitoring/summary` | ⏳ |
| 2.9.2 | `monitoringApi` | `getRealtimeData` | `/monitoring/realtime` | ⏳ |
| 2.9.3 | `monitoringApi` | `getAlerts` | `/monitoring/alerts` | ⏳ |
| 2.9.4 | `monitoringApi` | `getDragonTiger` | `/dragon-tiger` | ⏳ |
| 2.9.5 | `monitoringApi` | `stopMonitoring` | POST `/monitoring/control/stop` | ⏳ |
| 2.9.6 | `monitoringApi` | `startMonitoring` | POST `/monitoring/control/start` | ⏳ |

---

## API契约验证策略

### 验证层次金字塔

```
                    ╔═══════════════════════════╗
                    ║   Layer 4: 数据完整性   ║
                    ║   真实数据 vs Mock数据    ║
                    ╚═══════════════════════════╝
                    ╔═══════════════════════════╗
                    ║   Layer 3: 性能验证      ║
                    ║   响应时间 < 500ms       ║
                    ╚═══════════════════════════╝
                    ╔═══════════════════════════╗
                    ║   Layer 2: 契约格式验证  ║
                    ║   OpenAPI Schema匹配    ║
                    ╚═══════════════════════════╝
                    ╔═══════════════════════════╗
                    ║   Layer 1: 端点存在性   ║
                    ║   404 vs 200             ║
                    ╚═══════════════════════════╝
```

### 自动化验证脚本

**工具栈**:
- **OpenAPI Schema Validation**: `openapi-spec-validator`
- **API Contract Testing**: `pactum` 或 `requests + pytest`
- **Performance Testing**: `locust` 或 `apachebench`

**验证脚本示例**:
```python
# tests/contract/test_api_contracts.py

import pytest
import requests
from typing import Dict, Any

BASE_URL = "http://localhost:8020"
AUTH_TOKEN = "dev-mock-token-for-development"

class APIContractTest:
    """API契约测试基类"""

    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    def test_endpoint_exists(self, endpoint: str, method: str = "GET"):
        """Layer 1: 端点存在性验证"""
        url = f"{BASE_URL}{endpoint}"
        response = requests.request(method, url, headers=self.headers)

        # 不应该返回404
        assert response.status_code != 404, f"端点不存在: {endpoint}"

        # 不应该返回405 (Method Not Allowed)
        assert response.status_code != 405, f"方法不支持: {method} {endpoint}"

        return response

    def test_response_format(self, endpoint: str, expected_schema: Dict[str, Any]):
        """Layer 2: 契约格式验证"""
        response = self.test_endpoint_exists(endpoint)

        # 应该返回200或422 (验证错误)
        assert response.status_code in [200, 422], f"Unexpected status: {response.status_code}"

        if response.status_code == 200:
            data = response.json()

            # 验证UnifiedResponse格式
            assert "code" in data, "Missing 'code' field"
            assert "message" in data, "Missing 'message' field"
            assert "data" in data, "Missing 'data' field"

    def test_response_time(self, endpoint: str, max_ms: int = 500):
        """Layer 3: 性能验证"""
        import time

        start = time.time()
        response = self.test_endpoint_exists(endpoint)
        duration_ms = (time.time() - start) * 1000

        assert duration_ms < max_ms, f"响应过慢: {duration_ms}ms > {max_ms}ms"

    def test_real_data(self, endpoint: str, min_data_size: int = 1):
        """Layer 4: 数据完整性验证"""
        response = self.test_endpoint_exists(endpoint)

        if response.status_code == 200:
            data = response.json()

            # 数据不应该为空（除非预期为空）
            if isinstance(data.get("data"), list):
                assert len(data["data"]) >= min_data_size, \
                    f"数据不足: {len(data['data'])} < {min_data_size}"


# Phase 2.1 测试用例
class TestPhase21_IndustryConcept(APIContractTest):

    def test_2_1_1_industries_endpoint(self):
        """测试: /api/v1/data/stocks/industries"""
        self.test_endpoint_exists("/api/v1/data/stocks/industries")
        self.test_response_format("/api/v1/data/stocks/industries")
        self.test_response_time("/api/v1/data/stocks/industries", max_ms=300)
        self.test_real_data("/api/v1/data/stocks/industries", min_data_size=50)

    def test_2_1_2_concepts_endpoint(self):
        """测试: /api/v1/data/stocks/concepts"""
        self.test_endpoint_exists("/api/v1/data/stocks/concepts")
        self.test_response_format("/api/v1/data/stocks/concepts")
        self.test_response_time("/api/v1/data/stocks/concepts", max_ms=300)
        self.test_real_data("/api/v1/data/stocks/concepts", min_data_size=100)

    def test_2_1_3_stock_list_endpoint(self):
        """测试: /api/v1/data/stocks/basic"""
        self.test_endpoint_exists("/api/v1/data/stocks/basic?page=1&page_size=20")
        self.test_response_format("/api/v1/data/stocks/basic?page=1&page_size=20")
        self.test_response_time("/api/v1/data/stocks/basic?page=1&page_size=20", max_ms=500)
```

**执行验证**:
```bash
# 安装依赖
pip install pytest requests

# 运行Phase 2.1验证
pytest tests/contract/test_api_contracts.py::TestPhase21_IndustryConcept -v

# 生成覆盖率报告
pytest tests/contract/test_api_contracts.py --cov=web/frontend/src/api --cov-report=html
```

---

## 数据守卫者协调机制

### 问题分级与报告流程

**🔴 Critical Level**: 阻塞Phase 2执行
- **症状**: API返回404, 500, 数据完全缺失
- **行动**: 立即报告用户，等待数据层修复
- **预期响应时间**: 用户在24小时内提供数据或明确替代方案
- **示例**: "数据库中没有stock_industries表"

**🟠 High Level**: 影响功能但不阻塞
- **症状**: API返回数据但格式不匹配，性能差（>2秒）
- **行动**: 记录问题，继续验证其他API，汇总报告
- **预期响应时间**: 用户在48小时内确认处理方案
- **示例**: "行业数据字段名是industry_name，但前端期望industry"

**🟡 Medium Level**: 优化建议
- **症状**: 缺少性能限制，缓存未启用
- **行动**: 记录优化建议，Phase 2执行前处理
- **示例**: "K线API缺少limit参数"

### 立即报告机制

**触发条件**:
```python
# 验证脚本中定义
CRITICAL_ISSUES = [
    "endpoint_not_found",      # 404
    "method_not_allowed",      # 405
    "internal_error",          # 500
    "empty_data_when_expected", # 数据应该存在但为空
    "authentication_failed",   # 401/403
    "timeout",                 # >5秒
]

def check_and_report(endpoint: str, response: requests.Response):
    """检查并立即报告问题"""

    for issue in CRITICAL_ISSUES:
        if issue in response.text or response.status_code in [404, 500, 502]:
            # 🔴 立即报告
            print(f"\n{'='*60}")
            print(f"🔴 CRITICAL ISSUE DETECTED!")
            print(f"{'='*60}")
            print(f"API端点: {endpoint}")
            print(f"HTTP状态: {response.status_code}")
            print(f"响应内容: {response.text[:200]}")
            print(f"{'='*60}")
            print("\n📢 立即通知用户（数据守卫者）")
            print(f"   用户需要: 提供数据源或修复数据库")
            print(f"   预期时间: 24小时内响应")
            print(f"   下一步: 等待用户确认后再继续")

            # 写入问题日志
            with open("API_VERIFICATION_ISSUES.md", "a") as f:
                f.write(f"\n## 🔴 {endpoint}\n\n")
                f.write(f"- **状态**: {response.status_code}\n")
                f.write(f"- **时间**: {datetime.now().isoformat()}\n")
                f.write(f"- **响应**: {response.text[:500]}\n")
                f.write(f"- **需要**: 用户介入（数据层）\n")

            return True  # 阻塞继续验证

    return False  # 继续验证
```

**用户交互示例**:
```
Claude: 🔴 发现Critical Issue！
      API端点: /api/v1/data/stocks/industries
      问题: HTTP 500 - "relation 'stock_industries' does not exist"

      📢 请您确认：
      1. 数据库中是否存在stock_industries表？
      2. 是否需要运行数据导入脚本？
      3. 或者暂时使用Mock数据？

用户: 明白了。数据库表还没创建。你先暂停验证，
      我现在运行数据导入脚本，完成后通知你继续。

Claude: ✅ 已暂停API验证。等待数据库准备完成通知...
```

---

## API契约系统整合

### OpenAPI Schema自动生成

```python
# web/backend/app/core/openapi.py

from fastapi.openapi.utils import get_openapi
from app.api.data import stocks_router

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="MyStocks API",
        version="2.0.0",
        description="股票量化交易系统API",
        routes=app.routes,
    )

    # 自动添加所有已注册路由
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

### 前端类型自动生成

```bash
# 从OpenAPI Schema生成TypeScript类型
cd web/frontend

# 1. 安装工具
npm install -g openapi-typescript

# 2. 生成类型定义
openapi-typescript http://localhost:8020/openapi.json -o src/api/types/generated-types.ts

# 3. 验证生成结果
cat src/api/types/generated-types.ts | head -20
```

**生成的类型示例**:
```typescript
// src/api/types/generated-types.ts

export interface Industry {
  industry_name: string;
  industry_code: string;
  description?: string;
  stock_count?: number;
}

export interface Concept {
  concept_name: string;
  concept_code: string;
  description?: string;
}

export interface UnifiedResponse<T> {
  code: number | null;
  message: string;
  data: T;
}

export interface APIResponse_Industries extends UnifiedResponse<Industry[]> {}
```

### 契约匹配验证

```python
# tests/contract/test_contract_matching.py

def test_frontend_backend_contract_match():
    """验证前后端契约一致性"""

    # 1. 获取后端OpenAPI Schema
    import requests
    openapi_schema = requests.get("http://localhost:8020/openapi.json").json()

    # 2. 读取前端类型定义
    with open("web/frontend/src/api/types/generated-types.ts") as f:
        frontend_types = f.read()

    # 3. 验证关键类型存在
    assert "Industry" in frontend_types, "前端缺少Industry类型定义"
    assert "Concept" in frontend_types, "前端缺少Concept类型定义"

    # 4. 验证字段名称一致
    # 提取后端Schema中的字段名
    industries_schema = openapi_schema["components"]["schemas"]["Industry"]
    backend_fields = set(industries_schema["properties"].keys())

    # 解析前端类型定义
    # （简化示例，实际需要TypeScript解析器）
    assert "industry_name" in frontend_types, "前端缺少industry_name字段"
    assert "industry_code" in frontend_types, "前端缺少industry_code字段"
```

---

## 执行时间表

### Week 1: Phase 2.1 API验证 (2-3天)

**Day 1: 准备工作**
- [ ] 设置测试环境（pytest, requests）
- [ ] 生成前端TypeScript类型
- [ ] 创建自动化验证脚本
- [ ] 用户确认数据库准备就绪

**Day 2: 执行验证**
- [ ] 运行Phase 2.1测试套件
- [ ] 收集验证结果
- [ ] 生成问题报告
- [ ] 向用户报告Critical Issues

**Day 3: 问题修复**
- [ ] 用户解决数据层问题
- [ ] 重新验证修复的API
- [ ] 更新验证报告
- [ ] Phase 2.1验证完成 ✅

### Week 2-3: Phase 2.2-2.3 API验证 (5-7天)

**策略**: 滚动式验证
- 每个Phase子模块独立验证
- 发现问题立即报告
- 验证通过后进入下一阶段

---

## 验证输出文档

### 1. API验证进度跟踪表

**文件**: `docs/reports/API_VERIFICATION_PROGRESS.md`

| API端点 | Layer 1 | Layer 2 | Layer 3 | Layer 4 | 状态 | 备注 |
|---------|---------|---------|---------|---------|------|------|
| `/api/v1/data/stocks/industries` | ✅ | ✅ | ✅ | ✅ | ✅ 完成 | 50+行业 |
| `/api/v1/data/stocks/concepts` | ✅ | ✅ | ⚠️ | ⏳ | 🟡 进行中 | 响应时间700ms |
| `/api/v1/data/stocks/basic` | ✅ | ✅ | ⏳ | ⏳ | ⏳ 待验证 | - |

**状态图例**:
- ✅ 通过
- ⏳ 待验证
- ⚠️ 警告
- ❌ 失败
- 🟡 部分通过
- 🔴 阻塞

### 2. 问题汇总报告

**文件**: `docs/reports/API_VERIFICATION_ISSUES.md`

```markdown
# API验证问题汇总

## 🔴 Critical Issues (阻塞Phase 2)

### Issue #1: stock_industries表不存在
- **端点**: `/api/v1/data/stocks/industries`
- **发现时间**: 2026-01-02 10:30
- **错误信息**: `relation "stock_industries" does not exist`
- **影响**: 阻塞Phase 2.1执行
- **行动**: 用户确认数据库准备中，预计24小时完成
- **状态**: ⏳ 等待用户响应

## 🟠 High Priority Issues

### Issue #2: 概念API响应时间过长
- **端点**: `/api/v1/data/stocks/concepts`
- **发现时间**: 2026-01-02 11:15
- **问题**: 响应时间700ms (目标<300ms)
- **建议**: 添加数据库索引或启用缓存
- **状态**: ⏳ 待优化

## 🟡 Medium Priority Issues

### Issue #3: K线API缺少limit参数
- **端点**: `/api/v1/market/kline`
- **发现时间**: 2026-01-02 11:45
- **建议**: 添加默认limit=1000，最大limit=5000
- **状态**: ⏳ 待实现（已纳入Gemini建议）
```

---

## 下一步行动

### 立即执行 (今天)

1. **创建验证脚本模板**
   ```bash
   mkdir -p tests/contract
   cp scripts/dev/api_contract_verification_template.py tests/contract/
   ```

2. **生成OpenAPI Schema**
   ```bash
   curl http://localhost:8020/openapi.json -o docs/api/openapi.json
   ```

3. **询问用户数据库状态**
   - PostgreSQL数据库是否已创建？
   - stock_industries, stock_concepts表是否存在？
   - 是否有测试数据？

### 本周完成

1. **完成Phase 2.1验证** (3个API)
2. **生成验证报告**
3. **建立问题报告机制**

### 成功标准

- [ ] Phase 2.1的3个API全部通过4层验证
- [ ] 无Critical Issues遗留
- [ ] 用户数据守卫者机制建立
- [ ] 可以安全进入Phase 2.1执行

---

**创建日期**: 2026-01-02
**状态**: 🎯 Ready to Start
**下一步**: 询问用户数据库准备状态，然后开始API验证
**预计完成**: Phase 2.1验证完成后（2-3天）

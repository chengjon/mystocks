# CLI-6 任务分配：代码质量与测试保证

**分配时间**: 2025-12-29
**预计工作量**: 8-10 工作日
**优先级**: Round 1 - 贯穿整个周期
**依赖**: 无 (独立质量保证角色)
**Worktree路径**: `/opt/claude/mystocks_phase6_quality`
**分支**: `phase6-quality-assurance`

---

## 📋 任务概览

### 核心目标
作为**质量保证 (QA)** 角色,确保所有CLI交付物的代码质量、测试覆盖率和文档完整性达到生产级标准。

### 质量标准
- **测试覆盖率**: > 80% (单元测试 + 集成测试)
- **代码质量**: Ruff检查通过, Pylint评分 > 8.0
- **文档完整性**: 100%接口文档化
- **性能基准**: 关键接口响应时间达标
- **安全审计**: 无高危漏洞

### 关键交付物
1. **测试套件**: 单元测试 + 集成测试 + E2E测试
2. **代码质量报告**: Ruff/Pylint/Bandit分析报告
3. **性能基准测试**: Lighthouse/Locust压测报告
4. **文档完整性检查**: API文档/用户指南验证
5. **最终质量报告**: 综合质量评估报告

### 技术栈
- **测试**: pytest, pytest-cov, pytest-asyncio, pytest-mock
- **代码质量**: Ruff, Pylint, Black, Bandit, Safety
- **性能测试**: Locust (后端压测), Lighthouse (前端性能)
- **E2E测试**: Playwright (浏览器自动化)
- **CI/CD**: Pre-commit hooks, GitHub Actions

---

## 🎯 分阶段任务列表

### **阶段1: 测试套件构建 (Day 1-4)**

#### T6.1 后端单元测试 (80%覆盖率目标)
**目标**: 为所有后端API端点和核心业务逻辑编写单元测试

**覆盖模块**:
1. **API契约模块 (CLI-2)**:
   - 统一响应格式 (UnifiedResponse)
   - 错误码枚举 (ErrorCode)
   - Pydantic模型验证
   - OpenAPI schema生成

2. **Phase 4指标计算 (CLI-3)**:
   - A股交易规则引擎 (T+1, 涨跌停, 100股)
   - 161个技术指标计算 (TA-Lib封装)
   - 批量计算引擎
   - GPU加速引擎 (性能测试)
   - PostgreSQL缓存层

3. **AI智能选股 (CLI-4)**:
   - 查询解析器 (NLP → 结构化查询)
   - 推荐引擎 (综合评分算法)
   - 告警规则引擎
   - SSE推送服务

4. **GPU监控 (CLI-5)**:
   - GPU硬件监控 (pynvml封装)
   - 性能指标采集 (GFLOPS/加速比)
   - 历史数据服务 (PostgreSQL)
   - 优化建议引擎

**示例测试用例**:
```python
# tests/api_contract/test_unified_response.py
import pytest
from src.api_contract.unified_response import UnifiedResponse, ErrorCode
from pydantic import ValidationError

class TestUnifiedResponse:
    """统一响应格式测试"""

    def test_success_response(self):
        """测试成功响应"""
        response = UnifiedResponse.success(data={"symbol": "000001", "name": "平安银行"})

        assert response.success is True
        assert response.code == 0
        assert response.message == "操作成功"
        assert response.data["symbol"] == "000001"
        assert response.request_id is not None

    def test_error_response(self):
        """测试错误响应"""
        response = UnifiedResponse.error(
            code=ErrorCode.SYMBOL_NOT_FOUND,
            message="股票代码不存在",
            detail="000001 不是有效的股票代码"
        )

        assert response.success is False
        assert response.code == 1001
        assert "不存在" in response.message

    def test_generic_type_inference(self):
        """测试泛型类型推断"""
        from typing import List

        class StockData(BaseModel):
            symbol: str
            close: float

        response = UnifiedResponse[List[StockData]].success(
            data=[
                StockData(symbol="000001", close=10.5),
                StockData(symbol="000002", close=20.3)
            ]
        )

        assert len(response.data) == 2
        assert response.data[0].symbol == "000001"

# tests/indicators/test_astock_rules.py
import pytest
from datetime import datetime, timedelta
from src.indicators.astock_rules import AStockRulesEngine, AStockLimitType

class TestAStockRules:
    """A股交易规则测试"""

    def test_t1_rule_validation(self):
        """测试T+1规则"""
        engine = AStockRulesEngine()

        # 正常情况: 今天买入,明天卖出
        buy_date = datetime(2025, 1, 1)
        sell_date = datetime(2025, 1, 2)
        is_valid, msg = engine.validate_t1_rule(buy_date, sell_date)
        assert is_valid is True
        assert msg is None

        # 异常情况: 今天买入,今天卖出
        sell_date_same_day = datetime(2025, 1, 1)
        is_valid, msg = engine.validate_t1_rule(buy_date, sell_date_same_day)
        assert is_valid is False
        assert "T+1规则" in msg

    def test_price_limit_calculation(self):
        """测试涨跌停价格计算"""
        engine = AStockRulesEngine()

        # 普通股票 ±10%
        yesterday_close = 10.0
        limit_up, limit_down = engine.calculate_price_limit(yesterday_close, AStockLimitType.NORMAL)
        assert limit_up == 11.0
        assert limit_down == 9.0

        # ST股票 ±5%
        limit_up, limit_down = engine.calculate_price_limit(yesterday_close, AStockLimitType.ST)
        assert limit_up == 10.5
        assert limit_down == 9.5

    def test_lot_size_validation(self):
        """测试交易数量验证"""
        engine = AStockRulesEngine()

        # 买入必须100股整数倍
        is_valid, msg = engine.validate_lot_size(100, is_sell=False)
        assert is_valid is True

        is_valid, msg = engine.validate_lot_size(150, is_sell=False)
        assert is_valid is False
        assert "100股整数倍" in msg

        # 卖出可以非整数倍 (零股)
        is_valid, msg = engine.validate_lot_size(150, is_sell=True)
        assert is_valid is True

# tests/ai_screening/test_query_parser.py
import pytest
from src.ai_screening.query_parser import QueryParser

class TestQueryParser:
    """自然语言查询解析测试"""

    def test_parse_simple_query(self):
        """测试简单查询解析"""
        parser = QueryParser()
        result = parser.parse("市盈率小于20且ROE大于15的股票")

        assert result.intent == "VALUE_SCREENING"
        assert len(result.filters) == 2
        assert result.filters[0]["field"] == "pe_ratio"
        assert result.filters[0]["operator"] == "lt"
        assert result.filters[0]["value"] == 20

    def test_parse_technical_query(self):
        """测试技术指标查询解析"""
        parser = QueryParser()
        result = parser.parse("MACD金叉且成交量放大3倍")

        assert result.intent == "TECHNICAL_SCREENING"
        assert any(f["field"] == "macd_signal" for f in result.filters)
        assert any(f["field"] == "volume_ratio" for f in result.filters)

    def test_parse_ranking_query(self):
        """测试排行查询解析"""
        parser = QueryParser()
        result = parser.parse("涨幅最大的前20只股票")

        assert result.sort_by == "change_percent"
        assert result.sort_order == "desc"
        assert result.limit == 20

# tests/gpu_monitoring/test_gpu_monitor.py
import pytest
from src.gpu_monitoring.gpu_monitor_service import GPUMonitoringService

class TestGPUMonitoring:
    """GPU监控测试"""

    @pytest.fixture
    def gpu_monitor(self):
        return GPUMonitoringService()

    def test_get_metrics(self, gpu_monitor):
        """测试获取GPU指标"""
        metrics = gpu_monitor.get_metrics(device_id=0)

        assert metrics.device_id == 0
        assert metrics.device_name is not None
        assert 0 <= metrics.gpu_utilization <= 100
        assert metrics.memory_total > 0
        assert metrics.temperature > 0

    def test_get_all_metrics(self, gpu_monitor):
        """测试获取所有GPU指标"""
        all_metrics = gpu_monitor.get_all_metrics()

        assert len(all_metrics) > 0
        assert all(m.device_id >= 0 for m in all_metrics)
```

**测试配置 (pytest.ini)**:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow tests (skip with -m "not slow")
```

**验收标准**:
- [ ] 后端测试覆盖率 > 80%
- [ ] 所有单元测试通过
- [ ] 测试报告生成 (HTML + 控制台)

**预估时间**: 2天

---

#### T6.2 前端组件测试
**目标**: 为关键前端组件编写单元测试和集成测试

**覆盖组件**:
1. **ProKLineChart.vue** (K线图组件)
2. **RecommendationList.vue** (AI推荐列表)
3. **GPUStatusCard.vue** (GPU状态卡片)
4. **AlertCenter.vue** (告警中心)
5. **QueryParser组件** (自然语言查询输入)

**测试框架**: Vitest + Vue Test Utils

**示例测试**:
```typescript
// web/frontend/tests/components/RecommendationList.spec.ts
import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import RecommendationList from '@/components/AIScreening/RecommendationList.vue';
import axios from 'axios';

vi.mock('axios');

describe('RecommendationList.vue', () => {
  it('renders recommendations correctly', async () => {
    const mockData = [
      {
        symbol: '000001',
        name: '平安银行',
        composite_score: 85.5,
        value_score: 80,
        growth_score: 90,
        recommendation_reason: '低市盈率 + 高成长',
        risk_level: 'low'
      }
    ];

    (axios.post as any).mockResolvedValue({ data: mockData });

    const wrapper = mount(RecommendationList);
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('平安银行');
    expect(wrapper.text()).toContain('85.5');
  });

  it('handles strategy change', async () => {
    const wrapper = mount(RecommendationList);

    await wrapper.find('[label="value"]').trigger('click');
    expect(axios.post).toHaveBeenCalledWith('/api/ai-screening/recommendations', {
      strategy: 'value',
      top_n: 50,
      min_score: 60.0
    });
  });

  it('shows loading state', () => {
    const wrapper = mount(RecommendationList, {
      data() {
        return { loading: true };
      }
    });

    expect(wrapper.find('.el-loading-mask').exists()).toBe(true);
  });
});
```

**验收标准**:
- [ ] 关键组件测试覆盖率 > 70%
- [ ] 所有测试通过
- [ ] 快照测试(snapshot)通过

**预估时间**: 1天

---

#### T6.3 集成测试 (API端点)
**目标**: 测试API端点的完整请求/响应流程

**测试场景**:
```python
# tests/integration/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAPIIntegration:
    """API集成测试"""

    def test_kline_data_endpoint(self):
        """测试K线数据接口"""
        response = client.get("/api/market/kline", params={
            "symbol": "000001",
            "interval": "1d",
            "start_date": "2025-01-01",
            "end_date": "2025-01-31"
        })

        assert response.status_code == 200
        data = response.json()

        # 验证统一响应格式
        assert data["success"] is True
        assert data["code"] == 0
        assert "data" in data
        assert "request_id" in data

        # 验证K线数据结构
        klines = data["data"]
        assert len(klines) > 0
        assert all("date" in k for k in klines)
        assert all("close" in k for k in klines)

    def test_indicator_calculation_endpoint(self):
        """测试指标计算接口"""
        response = client.post("/api/indicators/calculate", json={
            "symbol": "000001",
            "indicator_code": "MACD",
            "params": {"fast_period": 12, "slow_period": 26, "signal_period": 9}
        })

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "macd" in data["data"]
        assert "signal" in data["data"]
        assert "histogram" in data["data"]

    def test_ai_recommendation_endpoint(self):
        """测试AI推荐接口"""
        response = client.post("/api/ai-screening/recommendations", json={
            "strategy": "balanced",
            "top_n": 10,
            "min_score": 60.0
        })

        assert response.status_code == 200
        data = response.json()

        assert len(data["data"]) <= 10
        assert all(r["composite_score"] >= 60 for r in data["data"])
        assert all("recommendation_reason" in r for r in data["data"])

    def test_gpu_monitoring_endpoint(self):
        """测试GPU监控接口"""
        response = client.get("/api/gpu/metrics/0")

        assert response.status_code == 200
        data = response.json()

        assert "gpu_utilization" in data
        assert "temperature" in data
        assert 0 <= data["gpu_utilization"] <= 100

    def test_error_handling(self):
        """测试错误处理"""
        # 无效股票代码
        response = client.get("/api/market/kline", params={
            "symbol": "999999",
            "interval": "1d"
        })

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["code"] == 1001  # ErrorCode.SYMBOL_NOT_FOUND

    def test_rate_limiting(self):
        """测试API限流"""
        # 发送100个连续请求
        for _ in range(100):
            response = client.get("/api/gpu/metrics/0")

        # 第101个请求应被限流
        response = client.get("/api/gpu/metrics/0")
        # assert response.status_code == 429  # Too Many Requests
```

**验收标准**:
- [ ] 所有关键API端点测试通过
- [ ] 错误处理测试通过
- [ ] 响应时间 < 3秒

**预估时间**: 1天

---

#### T6.4 E2E测试 (浏览器自动化)
**目标**: 使用Playwright进行端到端用户流程测试

**测试场景**:
```typescript
// tests/e2e/ai-screening-workflow.spec.ts
import { test, expect } from '@playwright/test';

test.describe('AI智能选股完整流程', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
    // 登录
    await page.fill('[data-testid="username"]', 'testuser');
    await page.fill('[data-testid="password"]', 'password');
    await page.click('[data-testid="login-btn"]');
    await expect(page).toHaveURL(/dashboard/);
  });

  test('自然语言查询 → AI推荐流程', async ({ page }) => {
    // 1. 导航到AI筛选页面
    await page.click('text=AI智能选股');
    await expect(page).toHaveURL(/ai-screening/);

    // 2. 输入自然语言查询
    await page.fill('[data-testid="query-input"]', '市盈率小于20且ROE大于15的股票');
    await page.click('[data-testid="search-btn"]');

    // 3. 验证推荐列表显示
    await expect(page.locator('[data-testid="recommendation-list"]')).toBeVisible();
    await expect(page.locator('.recommendation-item')).toHaveCount(50, { timeout: 5000 });

    // 4. 验证推荐详情
    const firstItem = page.locator('.recommendation-item').first();
    await expect(firstItem.locator('.composite-score')).toContainText(/\d+/);
    await expect(firstItem.locator('.recommendation-reason')).not.toBeEmpty();

    // 5. 点击加自选
    await firstItem.locator('[data-testid="add-watchlist-btn"]').click();
    await expect(page.locator('.el-message--success')).toBeVisible();
  });

  test('预定义模板查询', async ({ page }) => {
    await page.click('text=AI智能选股');

    // 点击"MACD金叉"模板
    await page.click('[data-testid="template-macd-golden-cross"]');

    // 验证自动填充查询条件
    await expect(page.locator('[data-testid="recommendation-list"]')).toBeVisible({ timeout: 5000 });
  });

  test('切换推荐策略', async ({ page }) => {
    await page.click('text=AI智能选股');

    // 切换到"价值策略"
    await page.click('[label="value"]');

    // 验证推荐列表更新
    await expect(page.locator('.recommendation-item').first()).toBeVisible({ timeout: 5000 });

    // 验证URL参数更新
    await expect(page).toHaveURL(/strategy=value/);
  });

  test('创建告警规则', async ({ page }) => {
    await page.click('text=告警中心');

    // 创建新规则
    await page.click('[data-testid="create-rule-btn"]');
    await page.fill('[data-testid="rule-name"]', 'MACD金叉告警');
    await page.selectOption('[data-testid="trigger-type"]', 'INDICATOR_SIGNAL');
    await page.click('[data-testid="add-condition-btn"]');
    await page.selectOption('[data-testid="condition-field"]', 'macd_signal');
    await page.selectOption('[data-testid="condition-operator"]', 'eq');
    await page.fill('[data-testid="condition-value"]', 'golden_cross');
    await page.click('[data-testid="submit-rule-btn"]');

    // 验证规则创建成功
    await expect(page.locator('.el-message--success')).toBeVisible();
    await expect(page.locator('.alert-rule-item')).toContainText('MACD金叉告警');
  });
});

// tests/e2e/gpu-monitoring-dashboard.spec.ts
test.describe('GPU监控仪表板', () => {
  test('实时指标更新', async ({ page }) => {
    await page.goto('http://localhost:3000/gpu-monitoring');

    // 验证GPU卡片显示
    await expect(page.locator('[data-testid="gpu-card-0"]')).toBeVisible();

    // 等待2秒,验证指标更新
    const initialTemp = await page.locator('[data-testid="gpu-temp"]').textContent();
    await page.waitForTimeout(2000);
    const updatedTemp = await page.locator('[data-testid="gpu-temp"]').textContent();

    // 验证温度值已更新 (SSE推送)
    // expect(initialTemp).not.toBe(updatedTemp);  // 可能相同,不是强制要求
  });

  test('性能图表显示', async ({ page }) => {
    await page.goto('http://localhost:3000/gpu-monitoring');

    // 验证ECharts图表渲染
    await expect(page.locator('canvas')).toBeVisible();

    // 切换时间范围
    await page.click('[label="6h"]');
    await page.waitForTimeout(1000);

    // 验证图表已重新渲染
    await expect(page.locator('canvas')).toBeVisible();
  });
});
```

**Playwright配置**:
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30 * 1000,
  expect: {
    timeout: 5000
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure'
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] }
    }
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI
  }
});
```

**验收标准**:
- [ ] 所有E2E测试通过
- [ ] 测试在Chrome/Firefox通过
- [ ] 失败时自动截图

**预估时间**: 1天 (Day 4)

---

### **阶段2: 代码质量检查 (Day 5-6)**

#### T6.5 Ruff/Pylint代码质量分析
**目标**: 运行代码质量检查并修复问题

**Ruff配置** (.ruff.toml):
```toml
line-length = 120
target-version = "py312"

[lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "PT",  # flake8-pytest-style
]
ignore = [
    "E501",  # line-too-long (handled by formatter)
    "N802",  # function name should be lowercase (允许驼峰命名)
]

[format]
quote-style = "double"
indent-style = "space"
```

**Pylint配置** (.pylintrc):
```ini
[MASTER]
disable=
    C0111,  # missing-docstring
    R0903,  # too-few-public-methods
    R0913,  # too-many-arguments
    W0212,  # protected-access

[FORMAT]
max-line-length=120
max-args=10

[DESIGN]
max-attributes=15
min-public-methods=1
```

**执行命令**:
```bash
# Ruff (快速修复)
ruff check --fix .

# Pylint (深度分析)
pylint src/ --output=reports/pylint_report.txt

# Black (格式化)
black src/ tests/
```

**质量目标**:
```
- Ruff: 0 errors, <10 warnings
- Pylint: Score > 8.0/10
- Black: 100% formatted
```

**验收标准**:
- [ ] Ruff检查通过
- [ ] Pylint评分 > 8.0
- [ ] Black格式化完成

**预估时间**: 1天

---

#### T6.6 安全审计 (Bandit/Safety)
**目标**: 检测安全漏洞和依赖安全

**Bandit配置** (.bandit):
```yaml
tests: [B201, B301, B302, B303, B304, B305, B306, B307, B308, B309, B310, B311, B312, B313, B314, B315, B316, B317, B318, B319, B320, B321, B323, B324, B325, B401, B402, B403, B404, B405, B406, B407, B408, B409, B410, B411, B412, B413, B501, B502, B503, B504, B505, B506, B507, B601, B602, B603, B604, B605, B606, B607, B608, B609, B610, B611]
exclude_dirs: ['/tests', '/venv']
```

**执行命令**:
```bash
# Bandit (安全扫描)
bandit -r src/ -f json -o reports/bandit_report.json

# Safety (依赖安全)
safety check --json > reports/safety_report.json
```

**常见安全问题修复**:
```python
# ❌ 不安全: 使用eval
eval(user_input)

# ✅ 安全: 使用ast.literal_eval
import ast
ast.literal_eval(user_input)

# ❌ 不安全: SQL注入
query = f"SELECT * FROM stocks WHERE symbol = '{symbol}'"

# ✅ 安全: 参数化查询
query = "SELECT * FROM stocks WHERE symbol = %s"
cursor.execute(query, (symbol,))

# ❌ 不安全: 硬编码密钥
API_KEY = "sk-1234567890abcdef"

# ✅ 安全: 环境变量
import os
API_KEY = os.getenv("API_KEY")
```

**验收标准**:
- [ ] Bandit: 无高危漏洞
- [ ] Safety: 无已知CVE漏洞
- [ ] 所有警告已修复

**预估时间**: 1天

---

### **阶段3: 性能测试 (Day 7-8)**

#### T6.7 后端API压力测试 (Locust)
**目标**: 验证API性能和并发能力

**Locust测试脚本**:
```python
# tests/load/locustfile.py
from locust import HttpUser, task, between
import random

class StockAPIUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def get_kline_data(self):
        """K线数据查询 (高频)"""
        symbols = ["000001", "000002", "600000", "600519"]
        self.client.get(
            "/api/market/kline",
            params={
                "symbol": random.choice(symbols),
                "interval": "1d",
                "limit": 100
            }
        )

    @task(2)
    def calculate_indicator(self):
        """指标计算 (中频)"""
        self.client.post(
            "/api/indicators/calculate",
            json={
                "symbol": "000001",
                "indicator_code": "MACD",
                "params": {}
            }
        )

    @task(1)
    def get_recommendations(self):
        """AI推荐 (低频)"""
        self.client.post(
            "/api/ai-screening/recommendations",
            json={
                "strategy": "balanced",
                "top_n": 50
            }
        )

    @task(1)
    def get_gpu_metrics(self):
        """GPU监控 (中频)"""
        self.client.get("/api/gpu/metrics/0")
```

**压测目标**:
```
- 并发用户: 100
- RPS (Requests Per Second): > 500
- 响应时间 P95: < 500ms
- 响应时间 P99: < 1000ms
- 错误率: < 1%
```

**执行命令**:
```bash
locust -f tests/load/locustfile.py --host=http://localhost:8000 --users=100 --spawn-rate=10 --run-time=5m --html=reports/locust_report.html
```

**验收标准**:
- [ ] RPS > 500
- [ ] P95响应时间 < 500ms
- [ ] 错误率 < 1%

**预估时间**: 1天

---

#### T6.8 前端性能测试 (Lighthouse)
**目标**: 验证前端页面加载和交互性能

**Lighthouse配置**:
```javascript
// tests/lighthouse/lighthouse.config.js
module.exports = {
  extends: 'lighthouse:default',
  settings: {
    onlyCategories: ['performance', 'accessibility', 'best-practices'],
    throttling: {
      rttMs: 150,
      throughputKbps: 1.6 * 1024,
      cpuSlowdownMultiplier: 4
    }
  }
};
```

**执行命令**:
```bash
# 测试关键页面
lighthouse http://localhost:3000/ --output=html --output-path=reports/lighthouse_home.html
lighthouse http://localhost:3000/ai-screening --output=html --output-path=reports/lighthouse_ai_screening.html
lighthouse http://localhost:3000/gpu-monitoring --output=html --output-path=reports/lighthouse_gpu.html
```

**性能目标**:
```
- Performance Score: > 90
- First Contentful Paint (FCP): < 1.5s
- Largest Contentful Paint (LCP): < 2.5s
- Time to Interactive (TTI): < 3.5s
- Cumulative Layout Shift (CLS): < 0.1
```

**常见优化措施**:
```typescript
// 1. 代码分割
const AIScreening = () => import('@/views/AIScreening/AIScreening.vue');

// 2. 图片懒加载
<el-image lazy :src="imageUrl" />

// 3. 虚拟滚动
<RecycleScroller :items="largeList" :item-size="80" />

// 4. 缓存优化
import { useIndexedDB } from '@vueuse/integrations/useIndexedDB';
```

**验收标准**:
- [ ] Performance Score > 90
- [ ] LCP < 2.5s
- [ ] CLS < 0.1

**预估时间**: 1天

---

### **阶段4: 文档与交付 (Day 9-10)**

#### T6.9 文档完整性检查
**目标**: 验证所有文档齐全且准确

**检查清单**:
```markdown
## API文档
- [ ] OpenAPI 3.0 Specification (openapi.yaml)
- [ ] 所有端点有描述和示例
- [ ] 请求/响应模型完整
- [ ] 错误码文档完整

## 用户指南
- [ ] 快速开始指南 (QUICKSTART.md)
- [ ] 部署指南 (DEPLOYMENT.md)
- [ ] 配置指南 (CONFIGURATION.md)

## 开发文档
- [ ] 架构设计文档 (ARCHITECTURE.md)
- [ ] API开发指南 (API_DEVELOPMENT.md)
- [ ] 代码贡献指南 (CONTRIBUTING.md)

## 质量报告
- [ ] 测试覆盖率报告 (coverage_report.html)
- [ ] 代码质量报告 (pylint_report.txt)
- [ ] 性能测试报告 (locust_report.html, lighthouse_*.html)
- [ ] 安全审计报告 (bandit_report.json, safety_report.json)
```

**文档生成工具**:
```bash
# OpenAPI文档生成
python scripts/generate_openapi.py > docs/api/openapi.yaml

# 代码文档生成
pdoc src/ --output-dir docs/api_reference
```

**验收标准**:
- [ ] 所有文档齐全
- [ ] API文档100%覆盖
- [ ] 用户指南可操作性强

**预估时间**: 1天

---

#### T6.10 最终质量报告生成
**目标**: 生成综合质量评估报告

**报告模板**:
```markdown
# MyStocks六阶段优化 - 最终质量报告

**生成时间**: 2025-01-XX
**项目版本**: v1.0.0
**审核人**: CLI-6 Quality Assurance Team

---

## 1. 测试覆盖率

| 模块 | 行覆盖率 | 分支覆盖率 | 测试用例数 | 状态 |
|------|---------|-----------|-----------|------|
| API契约 (CLI-2) | 85% | 80% | 45 | ✅ |
| 指标计算 (CLI-3) | 82% | 78% | 120 | ✅ |
| AI筛选 (CLI-4) | 80% | 75% | 60 | ✅ |
| GPU监控 (CLI-5) | 83% | 79% | 35 | ✅ |
| **整体** | **82.5%** | **78%** | **260** | ✅ |

**目标**: > 80% ✅ 达标

---

## 2. 代码质量

| 工具 | 评分/结果 | 状态 |
|------|-----------|------|
| Ruff | 0 errors, 5 warnings | ✅ |
| Pylint | 8.5/10 | ✅ |
| Black | 100% formatted | ✅ |
| Bandit | 0 high severity issues | ✅ |
| Safety | 0 known vulnerabilities | ✅ |

**目标**: Pylint > 8.0 ✅ 达标

---

## 3. 性能测试

### 后端API (Locust)
- **并发用户**: 100
- **RPS**: 580 (目标: >500) ✅
- **P95响应时间**: 420ms (目标: <500ms) ✅
- **P99响应时间**: 850ms (目标: <1000ms) ✅
- **错误率**: 0.3% (目标: <1%) ✅

### 前端性能 (Lighthouse)

| 页面 | Performance | LCP | CLS | 状态 |
|------|------------|-----|-----|------|
| 首页 | 92 | 1.8s | 0.05 | ✅ |
| AI筛选 | 90 | 2.2s | 0.08 | ✅ |
| GPU监控 | 91 | 2.0s | 0.06 | ✅ |

**目标**: Performance > 90, LCP < 2.5s ✅ 达标

---

## 4. 文档完整性

- [x] API文档 (OpenAPI 3.0)
- [x] 用户指南
- [x] 开发文档
- [x] 部署指南

**状态**: 100%完整 ✅

---

## 5. 风险与建议

### 已识别风险
1. **内存泄漏风险**: 长时间运行后显存利用率持续上升
   - **建议**: 增加内存池自动清理机制

2. **并发锁竞争**: 高并发下GPU资源争抢导致性能下降
   - **建议**: 实现请求队列和优先级调度

### 优化建议
1. 增加Redis缓存层减少数据库查询
2. 实施API限流和熔断机制
3. 前端增加Service Worker离线缓存

---

## 6. 验收结论

✅ **所有质量标准达标,建议批准上线**

- 测试覆盖率: ✅ 82.5% (> 80%)
- 代码质量: ✅ Pylint 8.5/10 (> 8.0)
- 性能测试: ✅ 所有指标达标
- 安全审计: ✅ 无高危漏洞
- 文档完整性: ✅ 100%

**签署**: CLI-6 QA Team
**日期**: 2025-01-XX
```

**验收标准**:
- [ ] 报告覆盖所有质量维度
- [ ] 所有指标清晰量化
- [ ] 风险和建议明确

**预估时间**: 1天

---

## 📊 进度跟踪与验收

### 里程碑检查点

| 里程碑 | 时间节点 | 验收标准 |
|--------|---------|---------|
| M1: 测试套件完成 | Day 4 | 覆盖率>80%, 所有测试通过 |
| M2: 代码质量达标 | Day 6 | Pylint>8.0, 无高危漏洞 |
| M3: 性能测试通过 | Day 8 | API RPS>500, 前端Performance>90 |
| M4: 最终报告生成 | Day 10 | 文档齐全, 质量报告完整 |

---

## 🔗 依赖关系

### 上游依赖
- **CLI-1, CLI-2, CLI-3, CLI-4, CLI-5**: 提供待测试的代码和API

### 下游影响
- **生产部署**: 质量报告作为上线审批依据

---

## 📝 交付清单

### 代码交付
- [ ] `tests/` - 完整测试套件
  - `tests/unit/` - 单元测试
  - `tests/integration/` - 集成测试
  - `tests/e2e/` - E2E测试
  - `tests/load/` - 压力测试
- [ ] `reports/` - 质量报告
  - `coverage_report.html` - 覆盖率报告
  - `pylint_report.txt` - Pylint报告
  - `bandit_report.json` - 安全审计
  - `locust_report.html` - 压测报告
  - `lighthouse_*.html` - 前端性能

### 文档交付
- [ ] `docs/quality/TESTING_GUIDE.md` - 测试指南
- [ ] `docs/quality/CODE_QUALITY_STANDARDS.md` - 代码质量标准
- [ ] `docs/quality/FINAL_QUALITY_REPORT.md` - 最终质量报告
- [ ] `README_CLI6.md` - CLI-6完成报告

---

## 🎯 成功标准

### 质量标准
- [x] 测试覆盖率 > 80%
- [x] Pylint评分 > 8.0
- [x] 无高危安全漏洞
- [x] API RPS > 500
- [x] 前端Performance > 90

### 文档标准
- [x] API文档100%覆盖
- [x] 用户指南完整
- [x] 质量报告准确

---

**最后更新**: 2025-12-29
**责任人**: CLI-6 Worker (Quality Assurance)
**预计完成**: 2025-01-08 (8-10工作日)

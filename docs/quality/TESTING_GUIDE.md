# MyStocks 测试指南

## 概述

本指南涵盖了 MyStocks 项目的测试策略、测试工具和最佳实践。

## 测试层次

```
┌─────────────────────────────────────┐
│     E2E 测试 (端到端)                │
│  Playwright (浏览器自动化)           │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│     集成测试 (API端点)               │
│  FastAPI TestClient                  │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│     单元测试 (函数/类)               │
│  pytest                             │
└─────────────────────────────────────┘
```

## 测试覆盖率目标

- **单元测试覆盖率**: > 80%
- **集成测试覆盖**: 所有关键API端点
- **E2E测试覆盖**: 核心用户流程

## 运行测试

### 运行所有测试

```bash
pytest
```

### 运行特定测试

```bash
# 运行特定文件
pytest tests/unit/test_stock_service.py

# 运行特定测试类
pytest tests/unit/test_stock_service.py::TestStockService

# 运行特定测试函数
pytest tests/unit/test_stock_service.py::TestStockService::test_get_stock
```

### 生成覆盖率报告

```bash
# HTML报告
pytest --cov=src --cov-report=html

# 控制台报告
pytest --cov=src --cov-report=term-missing

# XML报告 (CI/CD)
pytest --cov=src --cov-report=xml
```

### 按标记运行测试

```bash
# 只运行单元测试
pytest -m unit

# 只运行集成测试
pytest -m integration

# 只运行E2E测试
pytest -m e2e

# 排除慢速测试
pytest -m "not slow"
```

## 单元测试

### 基础示例

```python
import pytest
from src.services.stock_service import StockService
from src.models import StockData

class TestStockService:
    """股票服务单元测试"""

    @pytest.fixture
    def stock_service(self):
        """创建测试服务实例"""
        return StockService()

    @pytest.fixture
    def mock_stock_data(self):
        """模拟股票数据"""
        return {
            "symbol": "000001",
            "name": "平安银行",
            "price": 10.5,
            "change": 0.5,
            "change_percent": 5.0
        }

    def test_get_stock_data_success(self, stock_service, mock_stock_data):
        """测试成功获取股票数据"""
        # Arrange (准备)
        symbol = "000001"

        # Act (执行)
        data = stock_service.get_stock(symbol)

        # Assert (断言)
        assert data.symbol == symbol
        assert data.price > 0
        assert isinstance(data, StockData)

    def test_get_stock_data_not_found(self, stock_service):
        """测试股票不存在"""
        with pytest.raises(StockNotFoundError) as exc_info:
            stock_service.get_stock("999999")

        assert exc_info.value.code == "STOCK_NOT_FOUND"

    @pytest.mark.parametrize("symbol,expected_name", [
        ("000001", "平安银行"),
        ("000002", "万科A"),
        ("600000", "浦发银行")
    ])
    def test_get_stock_names(self, stock_service, symbol, expected_name):
        """参数化测试"""
        data = stock_service.get_stock(symbol)
        assert data.name == expected_name
```

### Mock使用示例

```python
from unittest.mock import Mock, patch
import pytest

class TestExternalAPI:
    """外部API测试"""

    @patch('src.services.akshare_adapter.akshare')
    def test_fetch_data_success(self, mock_akshare):
        """测试成功获取数据"""
        # 设置mock返回值
        mock_akshare.stock_zh_a_hist.return_value = pd.DataFrame({
            'date': ['2025-01-01', '2025-01-02'],
            'close': [10.5, 10.8]
        })

        # 执行测试
        adapter = AkshareAdapter()
        data = adapter.fetch_stock_data("000001")

        # 验证mock被调用
        mock_akshare.stock_zh_a_hist.assert_called_once()

        # 验证数据
        assert len(data) == 2
        assert data[0]['close'] == 10.5

    @patch('src.services.akshare_adapter.akshare')
    def test_fetch_data_failure(self, mock_akshare):
        """测试获取数据失败"""
        # 设置mock抛出异常
        mock_akshare.stock_zh_a_hist.side_effect = Exception("API error")

        # 执行测试并验证异常
        adapter = AkshareAdapter()
        with pytest.raises(APIError):
            adapter.fetch_stock_data("000001")
```

### 异步测试

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
class TestAsyncAPI:
    """异步API测试"""

    async def test_get_realtime_data(self):
        """测试获取实时数据"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/data/realtime/000001")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
```

## 集成测试

### FastAPI TestClient

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestStockAPIIntegration:
    """股票API集成测试"""

    def test_health_check(self):
        """测试健康检查"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "healthy"

    def test_get_kline_data(self):
        """测试K线数据接口"""
        response = client.get("/api/data/kline/000001", params={
            "interval": "1d",
            "limit": 100
        })

        assert response.status_code == 200
        data = response.json()

        # 验证统一响应格式
        assert "success" in data
        assert "code" in data
        assert "message" in data
        assert "data" in data
        assert "request_id" in data

        # 验证数据结构
        klines = data["data"]
        assert len(klines) > 0
        assert all("date" in k for k in klines)
        assert all("close" in k for k in klines)

    def test_calculate_indicator(self):
        """测试指标计算接口"""
        response = client.post("/api/indicators/calculate", json={
            "symbol": "000001",
            "indicator_code": "MACD",
            "params": {
                "fast_period": 12,
                "slow_period": 26,
                "signal_period": 9
            }
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # 验证指标数据
        result = data["data"]
        assert "macd" in result
        assert "signal" in result
        assert "histogram" in result

    def test_error_handling(self):
        """测试错误处理"""
        # 无效股票代码
        response = client.get("/api/data/stock/999999")

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["code"] == "1001"  # ErrorCode.STOCK_NOT_FOUND

    def test_rate_limiting(self):
        """测试API限流"""
        # 发送多个请求
        for _ in range(10):
            response = client.get("/api/data/stock/000001")

        # 第11个请求可能被限流
        response = client.get("/api/data/stock/000001")
        assert response.status_code in [200, 429]
```

### 数据库集成测试

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.database import Base
from src.models import Stock

@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    # 使用内存数据库
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    yield session

    session.close()
    engine.dispose()

class TestDatabaseIntegration:
    """数据库集成测试"""

    def test_create_and_query_stock(self, db_session):
        """测试创建和查询股票"""
        # 创建股票
        stock = Stock(symbol="000001", name="平安银行", price=10.5)
        db_session.add(stock)
        db_session.commit()

        # 查询股票
        queried_stock = db_session.query(Stock).filter_by(symbol="000001").first()

        assert queried_stock is not None
        assert queried_stock.name == "平安银行"
        assert queried_stock.price == 10.5
```

## E2E测试 (Playwright)

### 基础配置

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30 * 1000,
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

### E2E测试示例

```typescript
import { test, expect } from '@playwright/test';

test.describe('AI智能选股流程', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test('自然语言查询到推荐列表', async ({ page }) => {
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

  test('切换推荐策略', async ({ page }) => {
    await page.click('text=AI智能选股');

    // 切换到价值策略
    await page.click('[label="value"]');

    // 验证推荐列表更新
    await expect(page.locator('.recommendation-item').first()).toBeVisible({ timeout: 5000 });
    await expect(page).toHaveURL(/strategy=value/);
  });
});
```

### 运行E2E测试

```bash
# 运行所有E2E测试
npm run test:e2e

# 运行特定测试
npx playwright test tests/e2e/ai-screening.spec.ts

# 调试模式
npx playwright test --debug

# 查看报告
npx playwright show-report
```

## 性能测试

### Locust压力测试

```python
# tests/load/locustfile.py
from locust import HttpUser, task, between

class StockAPIUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def get_kline_data(self):
        """K线数据查询（高频）"""
        self.client.get("/api/data/kline/000001")

    @task(1)
    def calculate_indicator(self):
        """指标计算（低频）"""
        self.client.post("/api/indicators/calculate", json={
            "symbol": "000001",
            "indicator_code": "MACD"
        })
```

### 运行Locust

```bash
# Web界面模式
locust -f tests/load/locustfile.py --host=http://localhost:8000

# 无头模式
locust -f tests/load/locustfile.py \
  --host=http://localhost:8000 \
  --users=100 \
  --spawn-rate=10 \
  --run-time=5m \
  --headless \
  --html=reports/locust_report.html
```

## 测试最佳实践

### 1. AAA模式

所有测试应遵循 AAA (Arrange-Act-Assert) 模式：

```python
def test_example():
    # Arrange (准备测试数据和环境)
    service = StockService()
    symbol = "000001"

    # Act (执行被测试的功能)
    result = service.get_stock(symbol)

    # Assert (验证结果)
    assert result.symbol == symbol
```

### 2. 测试独立性

每个测试应该独立，不依赖其他测试：

```python
# ❌ 不好的示例
class TestWithDependency:
    def test_1(self):
        global.data = load_data()

    def test_2(self):
        assert global.data is not None  # 依赖test_1

# ✅ 好的示例
class TestIndependent:
    @pytest.fixture
    def data(self):
        return load_data()

    def test_1(self, data):
        assert data is not None

    def test_2(self, data):
        assert data is not None
```

### 3. 使用Fixture

使用pytest fixture管理测试资源：

```python
@pytest.fixture(scope="session")
def database():
    """会话级别的数据库fixture"""
    db = setup_database()
    yield db
    cleanup_database(db)

@pytest.fixture
def stock_data(database):
    """函数级别的测试数据"""
    return create_test_stock(database)
```

### 4. 清晰的断言信息

使用清晰的断言消息：

```python
# ❌ 不好的示例
assert result.success

# ✅ 好的示例
assert result.success, f"Expected success but got: {result}"
assert len(data) > 0, f"Data list is empty: {data}"
```

### 5. 避免测试实现细节

测试行为而非实现：

```python
# ❌ 测试实现细节
def test_get_stock_internal(self):
    result = service._fetch_from_database("000001")  # 测试私有方法
    assert result is not None

# ✅ 测试公开接口
def test_get_stock(self):
    result = service.get_stock("000001")  # 测试公开方法
    assert result.symbol == "000001"
```

## 持续集成

### GitHub Actions配置

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: |
          pytest --cov=src --cov-report=xml --cov-report=html

      - name: Upload coverage
        uses: codecov/codecov-action@v2
        with:
          file: ./coverage.xml
```

## 测试报告

### 查看测试报告

```bash
# pytest-html插件
pytest --html=reports/test_report.html --self-contained-html

# Allure报告
pytest --alluredir=allure-results
allure serve allure-results
```

---

遵循这些测试实践将确保代码质量和系统稳定性。

# MyStocks Web端"完全可用"衡量标准和测试方案

## 概述

本文档为MyStocks量化交易系统的Web端"完全可用"制定全面的衡量标准和测试方案，涵盖功能性、性能、可靠性、安全性、用户体验和数据质量六个维度。

## 项目架构概览

- **后端架构**: FastAPI + PostgreSQL + TDengine + Socket.IO (端口8000)
- **前端架构**: Vue3 + Vite + Element Plus + 图表库 (端口3001)
- **核心功能**: 股票数据查询、技术分析、策略管理、实时监控、风险管理

---

## 1. 功能性标准

### 1.1 核心功能模块完整性

#### 1.1.1 股票数据查询模块

**量化指标:**
- 股票搜索响应成功率 ≥ 99.5%
- 实时数据更新延迟 ≤ 500ms
- 历史数据查询范围 ≥ 10年
- 支持查询字段数量 ≥ 50个

**测试方法:**
```javascript
// Playwright端到端测试示例
test('股票查询功能完整性', async ({ page }) => {
  await page.goto('/dashboard');

  // 测试搜索功能
  await page.fill('[data-testid="stock-search"]', '平安银行');
  await page.press('[data-testid="stock-search"]', 'Enter');

  // 验证搜索结果
  await expect(page.locator('[data-testid="search-results"]')).toBeVisible();
  await expect(page.locator('[data-testid="stock-000001"]')).toContainText('平安银行');

  // 测试详情页
  await page.click('[data-testid="stock-000001"]');
  await expect(page.locator('[data-testid="stock-detail"]')).toBeVisible();

  // 验证数据完整性
  const price = await page.locator('[data-testid="current-price"]').textContent();
  const volume = await page.locator('[data-testid="volume"]').textContent();
  expect(price).toMatch(/^\d+\.\d{2}$/);
  expect(volume).toMatch(/^\d+$/);
});
```

**通过标准:**
- 所有API接口正常响应，错误率 ≤ 0.5%
- 数据字段完整率 ≥ 98%
- 支持多种查询方式（代码、名称、拼音）
- 实时数据推送正常

#### 1.1.2 技术分析模块

**量化指标:**
- 技术指标计算准确率 ≥ 99.9%
- 图表渲染时间 ≤ 1秒
- 支持技术指标数量 ≥ 30个
- 自定义策略保存成功率 ≥ 99%

**测试方法:**
```python
# API测试示例
import pytest
import requests
import time

@pytest.mark.parametrize("indicator", ["MA", "MACD", "RSI", "BOLL"])
def test_technical_indicators_accuracy(indicator):
    """测试技术指标计算准确性"""
    # 获取标准数据
    response = requests.get(f"http://localhost:8000/api/indicators/{indicator}",
                          params={"symbol": "000001", "period": "daily"})
    assert response.status_code == 200

    data = response.json()
    # 验证数据格式和数值合理性
    assert "values" in data
    assert len(data["values"]) > 0

    # 验证最后一个值不为空且在合理范围内
    latest_value = data["values"][-1]
    assert latest_value is not None
    assert isinstance(latest_value, (int, float))

def test_chart_rendering_performance():
    """测试图表渲染性能"""
    start_time = time.time()

    # 模拟大量数据点
    response = requests.get("http://localhost:8000/api/chart/kline",
                          params={"symbol": "000001", "period": "1min", "count": 1000})

    render_time = time.time() - start_time
    assert render_time <= 1.0  # 渲染时间不超过1秒
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1000
```

#### 1.1.3 策略管理模块

**量化指标:**
- 策略创建成功率 ≥ 99%
- 策略回测响应时间 ≤ 5秒
- 策略执行准确率 ≥ 99.5%
- 支持策略类型数量 ≥ 10种

**测试方案:**
```javascript
test('策略管理功能', async ({ page }) => {
  // 登录并进入策略管理
  await loginAsUser(page, 'admin', 'admin123');
  await page.goto('/strategy');

  // 创建新策略
  await page.click('[data-testid="create-strategy"]');
  await page.fill('[data-testid="strategy-name"]', '测试均线策略');
  await page.selectOption('[data-testid="strategy-type"]', 'MA交叉');
  await page.fill('[data-testid="ma-short"]', '5');
  await page.fill('[data-testid="ma-long"]', '20');
  await page.click('[data-testid="save-strategy"]');

  // 验证策略保存成功
  await expect(page.locator('[data-testid="success-message"]')).toBeVisible();

  // 运行回测
  await page.click('[data-testid="run-backtest"]');
  await expect(page.locator('[data-testid="backtest-results"]')).toBeVisible({timeout: 5000});

  // 验证回测结果
  const totalReturn = await page.locator('[data-testid="total-return"]').textContent();
  expect(parseFloat(totalReturn)).not.toBeNaN();
});
```

### 1.2 API接口测试标准

**量化指标:**
- API响应成功率 ≥ 99.8%
- 平均响应时间 ≤ 200ms
- 并发处理能力 ≥ 1000 QPS
- 错误码规范覆盖率 = 100%

**测试工具和方式:**
- **Postman/Newman**: API自动化测试
- **JMeter**: 压力测试和性能测试
- **pytest**: 后端单元测试
- **自定义监控**: 实时API监控

### 1.3 跨浏览器兼容性

**支持浏览器版本:**
- Chrome ≥ 90
- Firefox ≥ 88
- Safari ≥ 14
- Edge ≥ 90

**测试通过标准:**
- 功能一致性 = 100%
- UI显示一致性 ≥ 95%
- 性能差异 ≤ 20%

---

## 2. 性能标准

### 2.1 响应时间标准

| 操作类型 | 响应时间目标 | 最大可接受时间 |
|---------|------------|--------------|
| 页面加载 | ≤ 2秒 | ≤ 3秒 |
| API调用 | ≤ 200ms | ≤ 500ms |
| 数据查询 | ≤ 1秒 | ≤ 2秒 |
| 图表渲染 | ≤ 1秒 | ≤ 2秒 |
| 实时数据推送 | ≤ 100ms | ≤ 200ms |

### 2.2 并发性能标准

**量化指标:**
- 支持并发用户数 ≥ 1000
- 系统吞吐量 ≥ 500 QPS
- 峰值负载下响应时间增长 ≤ 50%
- 错误率在峰值负载下 ≤ 1%

### 2.3 资源使用标准

**前端资源:**
- 首屏加载资源大小 ≤ 2MB
- JavaScript包大小 ≤ 1MB
- CSS包大小 ≤ 200KB
- 图片资源优化率 ≥ 80%

**后端资源:**
- CPU使用率 ≤ 70%（正常负载）
- 内存使用率 ≤ 80%
- 数据库连接池使用率 ≤ 80%
- 磁盘I/O延迟 ≤ 10ms

### 2.4 性能测试工具和方法

**工具选择:**
```bash
# 使用Lighthouse进行性能审计
npx lighthouse http://localhost:3000 --output=json --output-path=./lighthouse-report.json

# 使用WebPageTest进行性能测试
docker run webpagetest/server webpagetest/server

# 使用JMeter进行压力测试
jmeter -n -t performance_test.jmx -l results.jtl
```

**测试脚本示例:**
```javascript
// 性能监控脚本
const performanceMetrics = {
  measurePageLoad: () => {
    const navigation = performance.getEntriesByType('navigation')[0];
    return {
      loadTime: navigation.loadEventEnd - navigation.loadEventStart,
      domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
      firstPaint: performance.getEntriesByType('paint')[0].startTime,
      firstContentfulPaint: performance.getEntriesByType('paint')[1].startTime
    };
  },

  measureAPICall: async (url) => {
    const start = performance.now();
    const response = await fetch(url);
    const end = performance.now();
    return {
      responseTime: end - start,
      status: response.status,
      size: response.headers.get('content-length')
    };
  }
};
```

---

## 3. 可靠性标准

### 3.1 系统可用性

**量化指标:**
- 系统可用性 ≥ 99.9%
- 计划外停机时间 ≤ 4小时/月
- 数据备份成功率 ≥ 99.99%
- 故障恢复时间 ≤ 5分钟（RTO）
- 数据恢复点 ≤ 1小时（RPO）

### 3.2 错误处理标准

**错误分类和处理:**
```javascript
// 错误处理测试
const errorScenarios = [
  {
    type: '网络错误',
    test: async () => {
      // 模拟网络断开
      await page.setOffline(true);
      const response = await page.evaluate(() => fetch('/api/data'));
      expect(response.status).toBe(0);
    },
    expectedBehavior: '显示网络错误提示，提供重试选项'
  },
  {
    type: '服务器错误',
    test: async () => {
      // 模拟500错误
      await page.route('/api/strategy', route => route.fulfill({status: 500}));
      await page.click('[data-testid="save-strategy"]');
      await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    },
    expectedBehavior: '显示友好错误信息，记录错误日志'
  },
  {
    type: '数据验证错误',
    test: async () => {
      await page.fill('[data-testid="price-input"]', 'invalid');
      await page.click('[data-testid="submit"]');
      await expect(page.locator('[data-testid="validation-error"]')).toBeVisible();
    },
    expectedBehavior: '显示具体验证错误，高亮错误字段'
  }
];
```

### 3.3 数据一致性标准

**量化指标:**
- 数据同步延迟 ≤ 1秒
- 数据准确率 ≥ 99.99%
- 数据完整性验证通过率 = 100%
- 并发更新冲突处理成功率 ≥ 99.5%

**数据一致性测试:**
```python
# 数据一致性测试
def test_data_consistency():
    """测试多数据源一致性"""
    # 从PostgreSQL读取
    pg_data = get_postgresql_data("SELECT * FROM stock_quotes WHERE symbol='000001'")

    # 从TDengine读取
    td_data = get_tdengine_data("SELECT * FROM stock_quotes WHERE symbol='000001'")

    # 从API获取实时数据
    api_data = get_api_data("/api/stock/000001")

    # 验证数据一致性
    assert abs(pg_data['price'] - td_data['price']) < 0.01
    assert abs(pg_data['price'] - api_data['price']) < 0.01
```

### 3.4 容错和恢复测试

**测试场景:**
- 数据库连接中断恢复
- 第三方API故障处理
- 内存泄漏检测
- 长时间运行稳定性

**测试实现:**
```python
@pytest.mark.slow
def test_long_running_stability():
    """长时间运行稳定性测试"""
    start_time = time.time()

    # 模拟24小时运行
    for hour in range(24):
        # 执行典型操作
        for _ in range(100):
            perform_user_actions()

        # 检查内存使用
        memory_usage = psutil.Process().memory_info().rss / 1024 / 1024
        assert memory_usage < 500  # 内存使用不超过500MB

        # 检查数据库连接
        assert check_database_connections() > 0

        # 强制垃圾回收
        gc.collect()

    total_time = time.time() - start_time
    assert total_time < 24 * 60 * 60 * 1.1  # 允许10%误差
```

---

## 4. 安全性标准

### 4.1 身份认证和授权

**量化指标:**
- 密码强度要求：至少8位，包含大小写字母、数字、特殊字符
- 会话超时时间：30分钟
- 登录失败锁定：5次失败后锁定15分钟
- 权限验证覆盖率 = 100%

**安全测试:**
```javascript
// 认证授权测试
describe('安全性测试', () => {
  test('密码强度验证', async ({ page }) => {
    await page.goto('/register');

    // 测试弱密码
    await page.fill('[data-testid="password"]', '123456');
    await page.click('[data-testid="register"]');
    await expect(page.locator('[data-testid="password-error"]')).toContainText('密码强度不够');

    // 测试强密码
    await page.fill('[data-testid="password"]', 'MyStocks@2024');
    await expect(page.locator('[data-testid="password-success"]')).toBeVisible();
  });

  test('会话超时', async ({ page }) => {
    await loginAsUser(page, 'user', 'user123');

    // 等待会话超时
    await page.waitForTimeout(31 * 60 * 1000); // 31分钟

    // 验证会话已过期
    await page.reload();
    await expect(page.locator('[data-testid="login-form"]')).toBeVisible();
  });

  test('权限控制', async ({ page }) => {
    await loginAsUser(page, 'user', 'user123');

    // 尝试访问管理员功能
    await page.goto('/admin');
    await expect(page.locator('[data-testid="access-denied"]')).toBeVisible();
  });
});
```

### 4.2 数据保护

**安全标准:**
- 敏感数据加密存储（密码、令牌等）
- HTTPS强制使用
- SQL注入防护覆盖率 = 100%
- XSS攻击防护覆盖率 = 100%
- CSRF令牌验证覆盖率 = 100%

**安全扫描工具:**
```bash
# 使用OWASP ZAP进行安全扫描
docker run -t owasp/zap2docker-stable zap-baseline.py -t http://localhost:3000

# 使用semgrep进行代码安全扫描
semgrep --config=auto web/frontend/src/

# 使用bandit进行Python安全扫描
bandit -r web/backend/
```

### 4.3 API安全

**安全措施:**
- API速率限制：100请求/分钟/用户
- 请求大小限制：≤10MB
- 输入验证和清理
- API密钥管理
- CORS配置正确性

**API安全测试:**
```python
# API安全测试
def test_sql_injection_protection():
    """测试SQL注入防护"""
    malicious_inputs = [
        "'; DROP TABLE users; --",
        "' OR '1'='1",
        "1; DELETE FROM stock_quotes WHERE 1=1; --"
    ]

    for payload in malicious_inputs:
        response = requests.get("http://localhost:8000/api/stock/search",
                              params={"q": payload})
        assert response.status_code != 500
        assert "error" in response.json() or len(response.json()) == 0

def test_rate_limiting():
    """测试API速率限制"""
    for i in range(105):  # 超过限制
        response = requests.get("http://localhost:8000/api/data/stocks")
        if i >= 100:
            assert response.status_code == 429

def test_xss_protection():
    """测试XSS防护"""
    xss_payloads = [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "<img src=x onerror=alert('xss')>"
    ]

    for payload in xss_payloads:
        # 测试搜索功能
        response = requests.post("http://localhost:8000/api/stock/search",
                               json={"query": payload})

        # 响应中不应包含未转义的脚本
        assert "<script>" not in response.text
        assert "javascript:" not in response.text
```

---

## 5. 用户体验标准

### 5.1 界面响应性

**量化指标:**
- 页面加载完成时间 ≤ 2秒
- 交互响应时间 ≤ 200ms
- 动画流畅度 ≥ 60 FPS
- 首次内容绘制（FCP）≤ 1.5秒
- 最大内容绘制（LCP）≤ 2.5秒

**性能监控:**
```javascript
// 用户体验监控
const UXMetrics = {
  measureInteractionTime: (element, action) => {
    const start = performance.now();
    return element[action]().then(() => {
      return performance.now() - start;
    });
  },

  measureScrollPerformance: () => {
    let frameCount = 0;
    let lastTime = performance.now();

    const measureFrames = () => {
      frameCount++;
      const currentTime = performance.now();

      if (currentTime - lastTime >= 1000) {
        const fps = Math.round(frameCount * 1000 / (currentTime - lastTime));
        console.log(`FPS: ${fps}`);
        frameCount = 0;
        lastTime = currentTime;
      }

      requestAnimationFrame(measureFrames);
    };

    requestAnimationFrame(measureFrames);
  }
};
```

### 5.2 可用性标准

**量化指标:**
- 任务完成率 ≥ 95%
- 用户错误率 ≤ 5%
- 学习时间 ≤ 30分钟（新用户）
- 用户满意度 ≥ 4.5/5.0

**可用性测试:**
```javascript
// 可用性测试场景
const usabilityTests = [
  {
    name: '股票查询任务',
    steps: [
      '打开搜索框',
      '输入股票代码',
      '选择搜索结果',
      '查看股票详情'
    ],
    maxCompletionTime: 30000, // 30秒
    allowedErrors: 1
  },
  {
    name: '策略创建任务',
    steps: [
      '进入策略管理',
      '点击创建策略',
      '填写策略信息',
      '保存策略'
    ],
    maxCompletionTime: 60000, // 60秒
    allowedErrors: 0
  }
];
```

### 5.3 无障碍访问

**WCAG 2.1 AA级标准:**
- 键盘导航支持
- 屏幕阅读器兼容
- 色彩对比度 ≥ 4.5:1
- 焦点指示器清晰可见
- ARIA标签完整

**无障碍测试:**
```javascript
// 无障碍测试
test('无障碍访问测试', async ({ page }) => {
  // 测试键盘导航
  await page.keyboard.press('Tab');
  const focusedElement = await page.evaluate(() => document.activeElement.tagName);
  expect(['BUTTON', 'INPUT', 'SELECT', 'A']).toContain(focusedElement);

  // 测试ARIA标签
  const searchButton = page.locator('[data-testid="search-button"]');
  await expect(searchButton).toHaveAttribute('aria-label');

  // 测试色彩对比度（需要axe-core）
  await injectAxe(page);
  await checkA11y(page);
});
```

### 5.4 响应式设计

**支持设备和分辨率:**
- 桌面端：≥ 1024x768
- 标准分辨率：1920x1080

**响应式测试:**
```javascript
// 桌面端响应式测试
test(`响应式测试 - 桌面端`, async ({ page }) => {
  await page.setViewportSize({ width: 1920, height: 1080 });
  await page.goto('/dashboard');

  // 验证布局适配
  await expect(page.locator('[data-testid="sidebar"]')).toBeVisible();
  await expect(page.locator('[data-testid="main-content"]')).toBeVisible();
});
```

---

## 6. 数据质量标准

### 6.1 数据准确性

**量化指标:**
- 实时价格准确率 ≥ 99.99%
- 历史数据完整率 ≥ 99.95%
- 数据更新频率：实时数据≤1秒，历史数据≤5分钟
- 数据异常率 ≤ 0.01%

**数据质量测试:**
```python
# 数据质量测试
def test_real_time_data_accuracy():
    """测试实时数据准确性"""
    # 获取多个数据源的数据进行对比
    sources = ['tushare', 'akshare', 'eastmoney']
    symbol = '000001'

    data_results = []
    for source in sources:
        data = get_data_from_source(source, symbol)
        if data:
            data_results.append(data['current_price'])

    # 验证数据一致性（允许0.01的误差）
    if len(data_results) >= 2:
        max_diff = max(data_results) - min(data_results)
        assert max_diff <= 0.01

def test_historical_data_integrity():
    """测试历史数据完整性"""
    # 检查最近一年的数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    data = get_historical_data('000001', start_date, end_date)

    # 验证数据点数量（考虑交易日）
    expected_days = get_trading_days_count(start_date, end_date)
    actual_count = len(data)

    # 允许5%的缺失率
    assert actual_count >= expected_days * 0.95

    # 验证数据连续性
    for i in range(1, len(data)):
        prev_date = data[i-1]['date']
        curr_date = data[i]['date']

        # 检查日期跳跃是否合理（考虑周末和节假日）
        days_diff = (curr_date - prev_date).days
        assert days_diff <= 7  # 最多间隔7天
```

### 6.2 数据实时性

**实时性标准:**
- Level-1实时数据延迟 ≤ 100ms
- Level-2深度数据延迟 ≤ 200ms
- K线数据更新延迟 ≤ 500ms
- 新闻资讯延迟 ≤ 5分钟

**实时性测试:**
```javascript
// 实时数据测试
test('实时数据延迟测试', async ({ page }) => {
  await page.goto('/stock/000001');

  // 监听WebSocket连接
  const wsMessages = [];
  page.on('websocket', ws => {
    ws.on('framesent', event => wsMessages.push({type: 'sent', payload: event.payload}));
    ws.on('framereceived', event => wsMessages.push({type: 'received', payload: event.payload}));
  });

  // 等待实时数据推送
  const startTime = Date.now();
  await page.waitForFunction(
    () => document.querySelector('[data-testid="last-update"]') !== null,
    {timeout: 5000}
  );

  const updateTime = Date.now();
  const delay = updateTime - startTime;

  // 验证延迟不超过500ms
  expect(delay).toBeLessThan(500);

  // 验证WebSocket消息格式
  const receivedMessages = wsMessages.filter(m => m.type === 'received');
  expect(receivedMessages.length).toBeGreaterThan(0);

  // 验证消息包含必要字段
  const latestMessage = JSON.parse(receivedMessages[receivedMessages.length - 1].payload);
  expect(latestMessage).toHaveProperty('price');
  expect(latestMessage).toHaveProperty('volume');
  expect(latestMessage).toHaveProperty('timestamp');
});
```

### 6.3 数据完整性

**完整性检查:**
- 主键约束验证通过率 = 100%
- 外键约束验证通过率 = 100%
- 数据类型约束验证通过率 = 100%
- 业务规则验证通过率 ≥ 99.9%

**数据完整性测试:**
```sql
-- 数据完整性SQL检查
-- 检查股票价格数据合理性
SELECT
    symbol,
    COUNT(*) as total_records,
    COUNT(CASE WHEN price <= 0 THEN 1 END) as invalid_price,
    COUNT(CASE WHEN volume < 0 THEN 1 END) as invalid_volume,
    MIN(price) as min_price,
    MAX(price) as max_price
FROM stock_quotes
WHERE trade_date >= CURRENT_DATE - INTERVAL '1 day'
GROUP BY symbol
HAVING COUNT(CASE WHEN price <= 0 OR volume < 0 THEN 1 END) > 0;

-- 检查数据连续性
SELECT
    symbol,
    trade_date,
    LAG(trade_date) OVER (PARTITION BY symbol ORDER BY trade_date) as prev_date
FROM stock_quotes
WHERE symbol = '000001'
AND trade_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY trade_date;
```

---

## 7. 测试执行方案

### 7.1 测试环境配置

**环境要求:**
```yaml
# docker-compose.test.yml
version: '3.8'
services:
  frontend:
    build: ./web/frontend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=test
      - VITE_API_BASE_URL=http://localhost:8000

  backend:
    build: ./web/backend
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=test
      - DATABASE_URL=postgresql://test:test@postgres:5432/mystocks_test
      - REDIS_URL=redis://redis:6379

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=mystocks_test
      - POSTGRES_USER=test
      - POSTGRES_PASSWORD=test
    ports:
      - "5432:5432"

  tdengine:
    image: tdengine/tdengine:2.4.0
    ports:
      - "6030:6030"

  redis:
    image: redis:6
    ports:
      - "6379:6379"
```

### 7.2 自动化测试流水线

**CI/CD配置:**
```yaml
# .github/workflows/web-usability-tests.yml
name: Web Usability Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # 每天凌晨2点执行

jobs:
  setup-and-test:
    timeout-minutes: 60
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: web/frontend/package-lock.json

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Start test environment
        run: |
          docker-compose -f docker-compose.test.yml up -d
          sleep 30  # 等待服务启动

      - name: Install dependencies
        run: |
          cd web/frontend && npm ci
          cd ../backend && pip install -r requirements.txt

      - name: Install Playwright
        run: npx playwright install --with-deps

      - name: Run functional tests
        run: |
          npx playwright test --config=playwright.config.web.ts

      - name: Run performance tests
        run: |
          npm run test:performance

      - name: Run security tests
        run: |
          npm run test:security
          bandit -r web/backend/

      - name: Run API tests
        run: |
          pytest web/backend/tests/api/ -v --junitxml=api-results.xml

      - name: Generate test report
        run: |
          npm run test:report

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: |
            playwright-report/
            test-results/
            coverage-report/
          retention-days: 30

      - name: Cleanup
        if: always()
        run: |
          docker-compose -f docker-compose.test.yml down -v
```

### 7.3 测试执行脚本

**完整测试执行脚本:**
```bash
#!/bin/bash
# run-web-usability-tests.sh

set -e

echo "🚀 开始执行MyStocks Web端可用性测试"

# 检查环境
echo "📋 检查测试环境..."
python check_environment.py

# 启动测试环境
echo "🐳 启动Docker测试环境..."
docker-compose -f docker-compose.test.yml up -d
sleep 30

# 功能性测试
echo "🧪 执行功能性测试..."
npx playwright test --config=playwright.config.web.ts tests/e2e/functional/
python -m pytest web/backend/tests/functional/ -v

# 性能测试
echo "⚡ 执行性能测试..."
npx playwright test --config=playwright.config.web.ts tests/e2e/performance/
cd web/frontend && npm run test:performance

# 安全性测试
echo "🔒 执行安全性测试..."
npx playwright test --config=playwright.config.web.ts tests/e2e/security/
bandit -r web/backend/ -f json -o security-report.json

# 用户体验测试
echo "👤 执行用户体验测试..."
npx playwright test --config=playwright.config.web.ts tests/e2e/usability/
lighthouse http://localhost:3000 --output=json --output-path=lighthouse-report.json

# 数据质量测试
echo "📊 执行数据质量测试..."
python -m pytest tests/data_quality/ -v

# 生成综合报告
echo "📄 生成测试报告..."
node generate-test-report.js

echo "✅ 所有测试执行完成"
echo "📊 查看详细报告: open test-report.html"

# 清理环境
docker-compose -f docker-compose.test.yml down -v
```

### 7.4 测试报告模板

**报告生成脚本:**
```javascript
// generate-test-report.js
const fs = require('fs');
const path = require('path');

class TestReportGenerator {
  constructor() {
    this.reportData = {
      timestamp: new Date().toISOString(),
      summary: {},
      functional: {},
      performance: {},
      security: {},
      usability: {},
      dataQuality: {},
      recommendations: []
    };
  }

  async generateReport() {
    // 收集各类型测试结果
    await this.collectFunctionalResults();
    await this.collectPerformanceResults();
    await this.collectSecurityResults();
    await this.collectUsabilityResults();
    await this.collectDataQualityResults();

    // 生成HTML报告
    const htmlReport = this.generateHTMLReport();
    fs.writeFileSync('test-report.html', htmlReport);

    // 生成JSON报告
    fs.writeFileSync('test-report.json', JSON.stringify(this.reportData, null, 2));

    console.log('✅ 测试报告已生成: test-report.html');
  }

  generateHTMLReport() {
    return `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MyStocks Web端可用性测试报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f5f5f5; padding: 20px; border-radius: 8px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 8px; }
        .pass { color: #28a745; }
        .fail { color: #dc3545; }
        .warning { color: #ffc107; }
        .metric { display: inline-block; margin: 10px; padding: 10px; background: #f8f9fa; border-radius: 4px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>MyStocks Web端可用性测试报告</h1>
        <p>生成时间: ${this.reportData.timestamp}</p>
    </div>

    <div class="section">
        <h2>测试概览</h2>
        <div class="metric">
            <strong>总测试用例:</strong> ${this.reportData.summary.totalTests}
        </div>
        <div class="metric pass">
            <strong>通过:</strong> ${this.reportData.summary.passed}
        </div>
        <div class="metric fail">
            <strong>失败:</strong> ${this.reportData.summary.failed}
        </div>
        <div class="metric">
            <strong>通过率:</strong> ${this.reportData.summary.passRate}%
        </div>
    </div>

    <div class="section">
        <h2>功能性测试结果</h2>
        ${this.renderFunctionalResults()}
    </div>

    <div class="section">
        <h2>性能测试结果</h2>
        ${this.renderPerformanceResults()}
    </div>

    <div class="section">
        <h2>安全性测试结果</h2>
        ${this.renderSecurityResults()}
    </div>

    <div class="section">
        <h2>用户体验测试结果</h2>
        ${this.renderUsabilityResults()}
    </div>

    <div class="section">
        <h2>数据质量测试结果</h2>
        ${this.renderDataQualityResults()}
    </div>

    <div class="section">
        <h2>改进建议</h2>
        ${this.renderRecommendations()}
    </div>
</body>
</html>`;
  }

  renderFunctionalResults() {
    const results = this.reportData.functional;
    return `
    <table>
        <tr><th>功能模块</th><th>测试用例</th><th>通过率</th><th>状态</th></tr>
        <tr><td>股票查询</td><td>${results.searchTests}</td><td>${results.searchPassRate}%</td><td class="${results.searchPassRate >= 95 ? 'pass' : 'fail'}">${results.searchPassRate >= 95 ? '✅' : '❌'}</td></tr>
        <tr><td>技术分析</td><td>${results.analysisTests}</td><td>${results.analysisPassRate}%</td><td class="${results.analysisPassRate >= 95 ? 'pass' : 'fail'}">${results.analysisPassRate >= 95 ? '✅' : '❌'}</td></tr>
        <tr><td>策略管理</td><td>${results.strategyTests}</td><td>${results.strategyPassRate}%</td><td class="${results.strategyPassRate >= 95 ? 'pass' : 'fail'}">${results.strategyPassRate >= 95 ? '✅' : '❌'}</td></tr>
    </table>`;
  }

  renderPerformanceResults() {
    const results = this.reportData.performance;
    return `
    <table>
        <tr><th>性能指标</th><th>目标值</th><th>实际值</th><th>状态</th></tr>
        <tr><td>页面加载时间</td><td>≤2s</td><td>${results.pageLoadTime}s</td><td class="${results.pageLoadTime <= 2 ? 'pass' : 'fail'}">${results.pageLoadTime <= 2 ? '✅' : '❌'}</td></tr>
        <tr><td>API响应时间</td><td>≤200ms</td><td>${results.apiResponseTime}ms</td><td class="${results.apiResponseTime <= 200 ? 'pass' : 'fail'}">${results.apiResponseTime <= 200 ? '✅' : '❌'}</td></tr>
        <tr><td>并发用户数</td><td>≥1000</td><td>${results.concurrentUsers}</td><td class="${results.concurrentUsers >= 1000 ? 'pass' : 'fail'}">${results.concurrentUsers >= 1000 ? '✅' : '❌'}</td></tr>
    </table>`;
  }

  // ... 其他渲染方法
}

// 执行报告生成
const generator = new TestReportGenerator();
generator.generateReport().catch(console.error);
```

---

## 8. 持续监控和改进

### 8.1 生产环境监控

**监控指标:**
```yaml
# monitoring-config.yml
metrics:
  application:
    - name: page_load_time
      threshold: 2000
      unit: ms
    - name: api_response_time
      threshold: 200
      unit: ms
    - name: error_rate
      threshold: 0.01
      unit: percentage
    - name: concurrent_users
      threshold: 1000
      unit: count

  business:
    - name: search_success_rate
      threshold: 0.995
      unit: percentage
    - name: data_accuracy
      threshold: 0.9999
      unit: percentage
    - name: user_satisfaction
      threshold: 4.5
      unit: score
```

### 8.2 自动化告警

**告警规则:**
```javascript
// alerting-rules.js
const alertingRules = {
  critical: [
    {
      name: 'system_down',
      condition: 'availability < 0.99',
      action: 'immediate_notification',
      channels: ['email', 'sms', 'slack']
    },
    {
      name: 'data_quality_issue',
      condition: 'data_accuracy < 0.999',
      action: 'immediate_notification',
      channels: ['email', 'slack']
    }
  ],

  warning: [
    {
      name: 'performance_degradation',
      condition: 'page_load_time > 2000',
      action: 'daily_report',
      channels: ['email']
    },
    {
      name: 'error_rate_increase',
      condition: 'error_rate > 0.01',
      action: 'immediate_notification',
      channels: ['slack']
    }
  ]
};
```

---

## 9. 总结和最佳实践

### 9.1 通过标准总结

MyStocks Web端要达到"完全可用"标准，需要满足以下核心要求：

| 维度 | 通过标准 | 关键指标 |
|-----|---------|----------|
| **功能性** | 核心功能覆盖率 ≥ 95% | 搜索成功率≥99.5%，功能完整性100% |
| **性能** | 响应时间达标率 ≥ 95% | 页面加载≤2s，API响应≤200ms |
| **可靠性** | 系统可用性 ≥ 99.9% | 故障恢复≤5分钟，错误率≤0.1% |
| **安全性** | 安全漏洞 = 0 | 通过OWASP安全扫描，认证授权100% |
| **用户体验** | 满意度 ≥ 4.5/5.0 | 任务完成率≥95%，界面响应≤200ms |
| **数据质量** | 数据准确率 ≥ 99.99% | 实时性≤1s，完整性≥99.95% |

### 9.2 最佳实践建议

1. **测试左移**: 在开发阶段就开始测试，尽早发现问题
2. **自动化优先**: 重点自动化回归测试和性能测试
3. **持续监控**: 建立生产环境实时监控体系
4. **用户反馈**: 定期收集用户体验反馈并持续改进
5. **安全优先**: 将安全测试贯穿整个开发流程
6. **性能优化**: 定期进行性能审计和优化

### 9.3 实施路线图

**第一阶段（1-2周）: 基础测试框架**
- 搭建Playwright端到端测试环境
- 建立API自动化测试体系
- 配置CI/CD测试流水线

**第二阶段（3-4周）: 全面测试覆盖**
- 实施所有功能模块测试
- 建立性能测试基准
- 完成安全扫描和修复

**第三阶段（5-6周）: 监控和优化**
- 建立生产环境监控
- 实施用户体验监控
- 建立持续改进流程

通过这套完整的衡量标准和测试方案，可以确保MyStocks Web端达到生产环境"完全可用"的高质量标准，为用户提供稳定、安全、高效的量化交易服务体验。

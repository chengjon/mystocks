# Backend API 自动化测试文档

**创建日期**: 2026-01-06
**测试框架**: Playwright E2E
**测试目标**: MyStocks Backend API (FastAPI)

---

## 📋 测试概览

### 测试套件

本项目包含两个 API 自动化测试套件：

#### 1. **backend-api-critical.spec.ts** （推荐）
- **用途**: 快速验证关键 API 端点
- **测试端点**: 8个关键端点 + 4个带参数端点
- **运行时间**: ~30秒
- **稳定性**: ✅ 高（避免超时问题）

**测试端点列表**:
- ✅ `/health` - 健康检查
- ✅ `/openapi.json` - OpenAPI 规范
- ✅ `/api/v1/market/status` - 市场状态
- ✅ `/api/v1/data-sources/` - 数据源列表
- ✅ `/api/data-quality/status/overview` - 数据质量概览
- ✅ `/api/dashboard/summary` - 仪表板摘要
- ✅ `/api/monitoring/summary` - 监控摘要
- ✅ `/api/v1/market/stock/list` - 股票列表（带参数）
- ✅ `/api/v1/market/kline` - K线数据（带参数）
- ✅ `/api/stock-search/search` - 股票搜索（带参数）
- ✅ `/api/technical/{symbol}/indicators` - 技术指标（带参数）

#### 2. **backend-api-automation.spec.ts** （完整版）
- **用途**: 全面测试所有 GET 端点
- **测试端点**: 所有可测试的 GET 端点（~172个）
- **运行时间**: ~10-15分钟
- **稳定性**: ⚠️ 中等（可能遇到超时）

**功能**:
- 自动从 OpenAPI JSON 提取所有 API 端点
- 过滤可测试的 GET 端点
- 自动替换路径参数
- 批量测试所有端点
- 生成详细的测试报告

---

## 🚀 快速开始

### 前置条件

1. **启动后端服务**:
```bash
pm2 start ecosystem.config.js --only mystocks-backend
# 或
cd /opt/claude/mystocks_spec/web/backend && ./start_backend.sh
```

2. **验证后端服务状态**:
```bash
curl http://localhost:8000/health
# 应该返回: {"status": "healthy"}
```

### 运行测试

#### 方法 1: 使用便捷脚本（推荐）

```bash
cd /opt/claude/mystocks_spec/web/frontend
./run-api-tests.sh
```

#### 方法 2: 直接运行 Playwright

**运行简化版测试**（推荐）:
```bash
cd /opt/claude/mystocks_spec
npx playwright test backend-api-critical --config=playwright.e2e.config.ts
```

**运行完整版测试**（需要更多时间）:
```bash
cd /opt/claude/mystocks_spec
npx playwright test backend-api-automation --config=playwright.e2e.config.ts
```

---

## 📊 测试报告

### 查看报告

测试运行后，会自动生成 HTML 报告：

```bash
# 报告位置
playwright-report/index.html

# 在浏览器中打开
xdg-open playwright-report/index.html  # Linux
open playwright-report/index.html        # macOS
start playwright-report/index.html       # Windows
```

### 报告内容

- ✅ **通过/失败统计**
- 📈 **响应时间分析**
- 🔍 **错误详情**
- 📸 **失败截图**（如果有）
- 🎬 **测试录制**（trace viewer）

---

## 🧪 测试用例详解

### 1. Critical Endpoints Test

**测试目标**: 验证关键端点的可用性和响应格式

**验证项**:
- HTTP 状态码 < 500
- 响应时间 < 5秒
- JSON 响应格式正确
- 符合 UnifiedResponse 规范

**示例输出**:
```
🧪 Health Check
  URL: http://localhost:8000/health
  Status: 200
  Duration: 20ms
  ✅ PASS
  ✓ Has 'code' field (UnifiedResponse)
  ✓ Has 'data' field (UnifiedResponse)
```

### 2. Parameterized Endpoints Test

**测试目标**: 测试需要参数的端点

**测试端点**:
- 股票列表 (`/api/v1/market/stock/list?limit=10`)
- K线数据 (`/api/v1/market/kline?stock_code=000001.SZ&period=daily&limit=5`)
- 股票搜索 (`/api/stock-search/search?query=600519`)
- 技术指标 (`/api/technical/000001.SZ/indicators`)

**参数替换规则**:
```typescript
// 测试参数映射
{stock_code} → '000001.SZ'
{symbol}      → '600519.SH'
{id}          → '1'
{period}      → 'daily'
{start_date} → '2024-01-01'
{end_date}   → '2024-12-31'
```

### 3. Performance Test

**性能目标**:
- 健康检查端点: < 100ms
- 其他关键端点: < 500ms
- 允许慢端点比例: < 20%

---

## 🔧 配置说明

### Playwright 配置

**配置文件**: `/opt/claude/mystocks_spec/playwright.e2e.config.ts`

**关键设置**:
```typescript
{
  testDir: './tests/e2e',
  timeout: 180 * 1000,      // 3分钟超时
  workers: 2,                // 2个并发worker
  retries: 1,                // 失败重试1次
  baseURL: 'http://localhost:8000'
}
```

### 测试过滤

**只运行特定测试**:
```bash
# 只运行 Critical Endpoints 测试
npx playwright test backend-api-critical --config=playwright.e2e.config.ts --grep "Critical Endpoints"

# 只运行 Performance 测试
npx playwright test backend-api-critical --config=playwright.e2e.config.ts --grep "Performance"
```

**排除特定测试**:
```bash
# 排除 Parameterized 测试
npx playwright test backend-api-critical --config=playwright.e2e.config.ts --grep-invert "Parameterized"
```

---

## 📝 测试最佳实践

### 1. 持续集成 (CI)

**GitHub Actions 示例**:
```yaml
name: API E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd /opt/claude/mystocks_spec
          npm ci
      - name: Install Playwright Browsers
        run: npx playwright install --with-deps
      - name: Start backend
        run: pm2 start ecosystem.config.js --only mystocks-backend
      - name: Run API tests
        run: npx playwright test backend-api-critical --config=playwright.e2e.config.ts
      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
```

### 2. 定期测试

**使用 cron 定期运行测试**:
```bash
# 每小时运行一次
0 * * * * cd /opt/claude/mystocks_spec && ./web/frontend/run-api-tests.sh
```

### 3. 性能监控

**记录性能指标**:
```bash
# 运行测试并保存性能数据
npx playwright test backend-api-critical \
  --config=playwright.e2e.config.ts \
  --reporter=json > test-results/performance-$(date +%Y%m%d-%H%M%S).json
```

---

## 🐛 故障排查

### 问题 1: 后端服务未启动

**错误信息**: `❌ Backend service is not running!`

**解决方案**:
```bash
pm2 start ecosystem.config.js --only mystocks-backend
```

### 问题 2: 测试超时

**错误信息**: `Timeout 30000ms exceeded`

**解决方案**:
1. 检查后端服务性能
2. 使用简化版测试（`backend-api-critical`）
3. 增加超时时间：
```bash
npx playwright test backend-api-critical \
  --config=playwright.e2e.config.ts \
  --timeout=60000
```

### 问题 3: OpenAPI JSON 无法访问

**错误信息**: `❌ OpenAPI JSON is not accessible!`

**解决方案**:
```bash
# 检查 OpenAPI 端点
curl http://localhost:8000/openapi.json

# 如果返回 404，检查后端日志
pm2 logs mystocks-backend
```

### 问题 4: Playwright 浏览器未安装

**错误信息**: `executables don't exist`

**解决方案**:
```bash
npx playwright install --with-deps
```

---

## 📚 扩展测试

### 添加新的测试端点

编辑 `backend-api-critical.spec.ts`:

```typescript
const CRITICAL_ENDPOINTS = [
  // ... 现有端点
  { path: '/api/v1/your-new-endpoint', name: 'Your New Endpoint' },
];
```

### 添加新的测试套件

创建新文件 `tests/e2e/your-api-test.spec.ts`:

```typescript
import { test, expect } from '@playwright/test';

test.describe('Your API Module', () => {
  test('should return correct data', async ({ request }) => {
    const response = await request.get('http://localhost:8000/api/v1/your-endpoint');
    expect(response.status()).toBe(200);

    const json = await response.json();
    expect(json).toHaveProperty('code', 200);
  });
});
```

---

## 🎯 测试目标

### Phase 1: 核心功能（当前阶段）
- ✅ 关键端点可用性
- ✅ 响应格式验证
- ✅ 基本性能测试

### Phase 2: 扩展功能（计划中）
- ⏳ POST/PUT/DELETE 请求测试
- ⏳ 认证流程测试
- ⏳ 完整业务流程测试
- ⏳ 数据一致性验证

### Phase 3: 性能优化（计划中）
- ⏳ 负载测试
- ⏳ 压力测试
- ⏳ 并发测试
- ⏳ 性能回归检测

---

## 📞 联系方式

**问题反馈**: 请在项目仓库创建 Issue
**文档更新**: 2026-01-06
**维护者**: Claude Code (Frontend Design Specialist)

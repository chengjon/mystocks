# MyStocks Web端可用性测试指南

## 概述

本指南详细介绍如何使用MyStocks Web端可用性测试套件来验证Web应用的"完全可用"标准。测试套件涵盖了功能性、性能、可靠性、安全性、用户体验和数据质量六个核心维度。

## 🚀 快速开始

### 1. 环境准备

确保以下环境已经准备就绪：

**必需软件:**
- Node.js ≥ 18
- Python ≥ 3.9
- Playwright 浏览器
- Docker (可选，用于容器化测试)

**Web服务:**
- 前端服务运行在 `http://localhost:3000`
- 后端API运行在 `http://localhost:8000`

### 2. 一键执行测试

```bash
# 执行所有测试
./scripts/tests/web-usability-runner.sh

# 或使用Node.js版本
node scripts/tests/web-usability-runner.js
```

### 3. 查看结果

测试完成后，在浏览器中打开生成的报告：
```bash
open test-results/index.html
```

## 📋 测试内容详解

### 🧪 功能性测试

验证所有核心功能是否按预期工作。

**测试范围:**
- 股票搜索和查询
- 技术分析功能
- 策略创建和管理
- 实时监控和提醒
- 用户认证和权限

**通过标准:**
- 功能覆盖率 ≥ 95%
- 核心功能成功率 ≥ 99%
- API响应成功率 ≥ 99.8%

**执行方式:**
```bash
# 仅执行功能性测试
./scripts/tests/web-usability-runner.sh functional

# 或使用Playwright直接运行
npx playwright test --config=playwright.config.web.ts --grep="functional"
```

### ⚡ 性能测试

确保应用在各种条件下都能快速响应。

**测试指标:**
- 页面加载时间 ≤ 2秒
- API响应时间 ≤ 200ms
- Lighthouse性能评分 ≥ 90
- 并发用户支持 ≥ 1000

**测试类型:**
```bash
# 性能测试包含：
# 1. Lighthouse审计
npx lighthouse http://localhost:3000 --output=json

# 2. API性能测试
# 3. 并发负载测试
# 4. 资源使用测试
```

### 🔒 安全性测试

检测和防止常见的安全威胁。

**安全检查项:**
- XSS攻击防护
- SQL注入防护
- CSRF防护
- 认证授权验证
- 敏感信息泄露检测

**安全工具集成:**
```bash
# 后端安全扫描
bandit -r web/backend/ -f json -o security-report.json

# 前端依赖安全检查
npm audit --json

# OWASP ZAP扫描
docker run -t owasp/zap2docker-stable zap-baseline.py -t http://localhost:3000
```

### 👤 用户体验测试

确保界面友好且易于使用。

**UX测试维度:**
- 响应式设计适配
- 无障碍访问支持
- 交互反馈及时性
- 导航流畅性

**设备支持:**
- 桌面端 (1920x1080)

### 📊 数据质量测试

保证数据的准确性、完整性和实时性。

**质量标准:**
- 数据准确率 ≥ 99.99%
- 实时数据延迟 ≤ 1秒
- 历史数据完整率 ≥ 99.95%
- 数据格式验证通过率 = 100%

## 🛠️ 测试配置

### 环境变量配置

创建 `.env.test` 文件：

```bash
# 服务地址
BASE_URL=http://localhost:3000
API_URL=http://localhost:8000

# 测试配置
TEST_TIMEOUT=120000
TEST_RETRIES=2

# 认证信息
TEST_USERNAME=admin
TEST_PASSWORD=admin123

# 测试环境
ENVIRONMENT=dev
```

### Playwright配置

编辑 `playwright.config.web.ts`：

```typescript
export default defineConfig({
  testDir: './tests/e2e',
  timeout: 60 * 1000,
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    video: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
});
```

## 📈 高级用法

### 1. 持续集成

在GitHub Actions中集成：

```yaml
name: Web Usability Tests

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
      - name: Run Tests
        run: ./scripts/tests/web-usability-runner.sh --env staging
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: test-results/
```

### 2. 环境切换

不同环境的测试配置：

```bash
# 开发环境
./scripts/tests/web-usability-runner.sh -e dev

# 测试环境
./scripts/tests/web-usability-runner.sh -e staging

# 生产环境（谨慎使用）
./scripts/tests/web-usability-runner.sh -e prod
```

### 3. 测试分类执行

```bash
# 快速测试（跳过耗时测试）
./scripts/tests/web-usability-runner.sh -q

# 跳过特定测试类型
./scripts/tests/web-usability-runner.sh --skip-security

# 仅执行特定测试类型
./scripts/tests/web-usability-runner.sh functional
```

### 4. 详细输出

```bash
# 详细输出模式
./scripts/tests/web-usability-runner.sh -v

# 指定输出目录
./scripts/tests/web-usability-runner.sh -o ./custom-results
```

## 📊 测试报告解读

### 报告结构

测试报告包含以下部分：

1. **测试概览** - 总体通过率和关键指标
2. **功能性测试结果** - 各功能模块的测试详情
3. **性能测试结果** - 响应时间和性能评分
4. **安全性测试结果** - 安全漏洞和风险评估
5. **用户体验测试结果** - UX指标和可用性评分
6. **数据质量测试结果** - 数据准确性和完整性

### 通过标准评估

系统需要满足以下标准才能通过"完全可用"评估：

| 维度 | 通过标准 | 关键指标 |
|-----|---------|----------|
| **功能性** | ≥95% | 搜索成功率≥99.5%，功能完整性100% |
| **性能** | ≥95% | 页面加载≤2s，API响应≤200ms |
| **安全性** | 100% | 无高危漏洞，认证授权100% |
| **用户体验** | ≥90% | 任务完成率≥95%，界面响应≤200ms |
| **数据质量** | ≥99% | 数据准确率≥99.99%，实时性≤1s |

### 问题排查

**常见问题及解决方案:**

1. **测试超时**
   ```bash
   # 增加超时时间
   export TEST_TIMEOUT=300000
   ./scripts/tests/web-usability-runner.sh
   ```

2. **服务连接失败**
   ```bash
   # 检查服务状态
   curl http://localhost:3000
   curl http://localhost:8000/health
   ```

3. **Playwright浏览器问题**
   ```bash
   # 重新安装浏览器
   npx playwright install --with-deps
   ```

## 🔧 自定义测试

### 添加新的测试用例

1. **在现有测试文件中添加:**

```javascript
test('新增功能测试', async ({ page }) => {
  await page.goto(BASE_URL);
  // 测试逻辑
  await expect(page.locator('[data-testid="new-element"]')).toBeVisible();
});
```

2. **创建新的测试文件:**

```javascript
// tests/e2e/new-feature.spec.js
const { test, expect } = require('@playwright/test');

test.describe('新功能测试', () => {
  test('功能基本测试', async ({ page }) => {
    // 测试代码
  });
});
```

### 自定义性能指标

修改 `scripts/tests/web-usability-runner.js`：

```javascript
async runCustomPerformanceTest() {
  // 自定义性能测试逻辑
  const customMetrics = {
    databaseQueryTime: await this.measureDatabaseQueryTime(),
    chartRenderTime: await this.measureChartRenderTime()
  };
  return customMetrics;
}
```

### 添加新的安全检查

```javascript
async runCustomSecurityTest() {
  // 自定义安全检查逻辑
  const securityChecks = [
    { name: '自定义检查', check: async () => { /* 检查逻辑 */ } }
  ];
  return securityChecks;
}
```

## 📚 最佳实践

### 1. 测试编写最佳实践

- **使用data-testid**：为测试元素添加专门的test id
- **避免硬编码等待**：使用page.waitForSelector等智能等待
- **保持测试独立**：每个测试应该能独立运行
- **添加适当断言**：验证关键状态和内容

### 2. 持续改进建议

- **定期更新测试**：随着功能迭代更新测试用例
- **监控测试执行时间**：优化过慢的测试
- **分析测试失败模式**：识别系统常见问题
- **扩展测试覆盖范围**：逐步增加测试场景

### 3. 测试数据管理

- **使用测试专用数据**：避免影响生产数据
- **数据隔离**：每个测试使用独立的数据集
- **数据清理**：测试后清理生成的数据
- **数据版本控制**：管理测试数据的变更

## 🆘 故障排除

### 常见错误及解决方案

**1. Element not found**
```javascript
// 解决方案：增加等待时间或使用更精确的选择器
await page.waitForSelector('[data-testid="element"]', { timeout: 10000 });
```

**2. Network timeout**
```javascript
// 解决方案：增加网络超时时间
await page.goto(url, { timeout: 60000 });
```

**3. Permission denied**
```bash
# 解决方案：检查文件权限
chmod +x scripts/tests/web-usability-runner.sh
```

### 调试技巧

1. **使用调试模式**
```bash
npx playwright test --debug tests/e2e/login.spec.js
```

2. **生成可视化测试报告**
```bash
npx playwright test --reporter=html
```

3. **录制测试脚本**
```bash
npx playwright codegen http://localhost:3000
```

## 📞 支持与反馈

如果在使用过程中遇到问题或有改进建议，请：

1. 查看详细日志：`test-results/*.log`
2. 检查测试配置：确认环境变量设置正确
3. 参考文档：查看 `docs/standards/WEB_USABILITY_STANDARDS.md`
4. 提交Issue：在项目仓库中创建问题报告

## 🔗 相关文档

- [Web端可用性标准](../standards/WEB_USABILITY_STANDARDS.md)
- [Playwright官方文档](https://playwright.dev/)
- [Lighthouse性能测试指南](https://developers.google.com/web/tools/lighthouse)
- [OWASP安全测试指南](https://owasp.org/www-project-web-security-testing-guide/)

---

**注意：** 本测试套件旨在帮助确保MyStocks Web系统达到生产环境"完全可用"的高质量标准。请定期执行测试并根据结果持续改进系统质量。

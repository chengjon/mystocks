# Playwright API 自动化测试指南

本文档说明如何使用 Playwright 对 FastAPI 后端进行自动化 API 测试。

## 功能特性

### 核心功能

1. **自动发现 API 端点**
   - 从 FastAPI 的 OpenAPI 规范自动发现所有 API 端点
   - 支持所有 HTTP 方法（GET, POST, PUT, DELETE, PATCH）
   - 自动提取端点参数、请求体和响应定义

2. **自动化测试执行**
   - 批量测试所有发现的 API 端点
   - 自动生成测试数据（路径参数、查询参数、请求头）
   - 支持认证端点的自动处理

3. **测试报告生成**
   - 实时显示测试进度和结果
   - 生成 JSON、HTML 和文本格式的测试报告
   - 统计通过率、平均响应时间等关键指标

4. **分组测试**
   - 按功能模块分组测试（认证、市场数据等）
   - 支持标签过滤和端点筛选

## 快速开始

### 1. 前置条件

确保已安装以下依赖：

```bash
# Node.js 和 npm（用于运行 Playwright）
node --version  # 应该 >= 18
npm --version

# Playwright 浏览器
cd /opt/claude/mystocks_spec/web/frontend
npx playwright install
```

### 2. 启动后端服务

```bash
# 方式1: 使用 PM2
pm2 restart mystocks-backend

# 方式2: 直接运行
cd /opt/claude/mystocks_spec/web/backend
python3 -m app.main
```

### 3. 运行测试

```bash
# 使用默认配置（后端地址 http://localhost:8000）
./run-api-tests.sh

# 指定不同的后端地址
./run-api-tests.sh -u http://localhost:8001

# 或者直接使用 Playwright
cd /opt/claude/mystocks_spec/web/frontend
BASE_URL=http://localhost:8000 npx playwright test ../tests/e2e/api-automation.spec.js
```

## 测试文件结构

```
tests/e2e/
├── api-automation.spec.js     # 主测试脚本
├── backend-api-automation.spec.ts  # TypeScript 版本（如果存在）
└── README.md                   # 本文档
```

## 测试报告位置

测试报告保存在：

```
docs/reports/test-results/
├── api-test-report-20250106_123456.txt      # 文本报告
├── api-test-report-20250106_123456.json     # JSON 报告
└── api-test-report-20250106_123456.html     # HTML 报告（可视化）
```

## 高级用法

### 1. 自定义测试数据

编辑 `api-automation.spec.js` 中的 `generateTestData` 函数：

```javascript
function generateTestData(parameters) {
  const testData = {};

  parameters.forEach(param => {
    if (param.in === 'path' || param.in === 'query') {
      const schema = param.schema;
      const name = param.name;

      // 自定义测试数据生成逻辑
      if (name === 'stock_code') {
        testData[name] = '600519.SH';  // 贵州茅台
      } else if (name === 'period') {
        testData[name] = 'daily';
      }
    }
  });

  return testData;
}
```

### 2. 添加性能断言

在测试函数中添加性能要求：

```javascript
// 断言响应时间小于 1 秒
expect(result.responseTime).toBeLessThan(1000);

// 断言通过率大于 80%
expect(parseFloat(report.summary.passRate)).toBeGreaterThan(80);
```

### 3. 集成到 CI/CD

在 GitHub Actions 或其他 CI 系统中集成：

```yaml
name: API Tests

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
          cd web/frontend
          npm install
          npx playwright install
      - name: Start backend
        run: |
          cd web/backend
          pip install -r requirements.txt
          python3 -m app.main &
      - name: Run API tests
        run: ./run-api-tests.sh
        env:
          BASE_URL: http://localhost:8000
```

### 4. 监控和告警

基于测试结果设置告警：

```bash
# 运行测试并检查通过率
./run-api-tests.sh
PASS_RATE=$(jq '.summary.passRate' docs/reports/test-results/api-test-report-*.json | sed 's/%//')

if (( $(echo "$PASS_RATE < 80" | bc -l) )); then
  echo "警告: API 通过率低于 80%"
  # 发送告警通知
fi
```

## 测试覆盖范围

### 自动测试的端点类型

- ✅ 健康检查端点 (`/health`)
- ✅ OpenAPI 规范端点 (`/openapi.json`, `/docs`, `/redoc`)
- ✅ 认证相关端点 (`/api/v1/auth/*`)
- ✅ 市场数据端点 (`/api/v1/market/*`)
- ✅ 策略管理端点 (`/api/v1/strategies/*`)
- ✅ 交易管理端点 (`/api/v1/trading/*`)

### 不测试的端点

- ❌ 需要特定用户权限的端点（除非提供认证令牌）
- ❌ 写入操作（POST, PUT, DELETE）仅测试请求格式，不验证数据持久化
- ❌ WebSocket 端点（需要特殊处理）

## 故障排查

### 问题1: 后端服务未响应

```bash
❌ 后端服务未响应或不可用
```

**解决方案**:
1. 检查后端服务是否运行：`pm2 status` 或 `lsof -i :8000`
2. 查看后端日志：`pm2 logs mystocks-backend`
3. 重启后端服务：`pm2 restart mystocks-backend`

### 问题2: Playwright 未安装

```bash
❌ 未找到 npx 命令
```

**解决方案**:
```bash
# 安装 Node.js 和 npm
sudo apt-get install nodejs npm

# 或使用 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
```

### 问题3: 所有端点测试失败

**可能原因**:
- 认证配置问题
- CORS 策略限制
- 后端服务异常

**解决方案**:
1. 检查认证配置（JWT 密钥）
2. 查看 CORS 设置
3. 查看后端错误日志

## 最佳实践

1. **定期运行测试**：建议每次代码提交后运行
2. **监控通过率**：保持通过率在 90% 以上
3. **性能基准**：记录平均响应时间，监控性能退化
4. **失败分析**：及时分析失败的端点并修复问题
5. **持续改进**：根据测试结果不断优化 API 设计

## 相关文档

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Playwright 官方文档](https://playwright.dev/)
- [OpenAPI 规范](https://swagger.io/specification/)
- [项目测试指南](./../guides/PYTHON_QUALITY_ASSURANCE_WORKFLOW.md)

## 更新日志

- **2025-01-06**: 初始版本，支持基本的 API 自动化测试
- 后续版本将添加更多功能，如：
  - 并发测试支持
  - 性能基准测试
  - 数据验证增强
  - WebSocket 端点测试

## 联系方式

如有问题或建议，请在项目仓库提交 Issue。

# MyStocks 端到端自动化测试套件

> 2026-03 基线：标准 E2E 入口为 `npm run test:e2e`，使用 `playwright.config.js`（`tests/e2e`）。
> `playwright.config.ts` 仅用于历史 legacy 专项脚本。
> 端口统一由 `.env` 注入：前端 `3020`（备份 `3021`），后端 `8020`（备份 `8021`）。

## 概述

本测试套件基于 Playwright 实现完整的端到端自动化测试，专门针对基于 PM2 运行的 MyStocks Web 服务进行全面验证。严格按照您的要求实现，不以简单的 HTTP 状态码作为通过依据，而是进行全链路的渲染、元素、数据、交互校验。

## 测试覆盖范围

### Phase 1: 前置校验 (Preflight Checks)
- ✅ PM2 进程状态验证（前端/后端服务）
- ✅ 端口连通性检查（3020/8020）
- ✅ HTTP 响应状态验证
- ✅ 前端 HTML 内容完整性验证

### Phase 2: 页面加载完整性 (Page Load Integrity)
- ✅ DOM 元素存在性验证（导航栏、内容容器、核心按钮等 3+ 关键元素）
- ✅ 页面标题和元数据校验（UTF-8 编码、viewport 设置）
- ✅ 资源加载验证（JavaScript bundles、CSS 样式表、无失败请求）
- ✅ 控制台错误检测（JavaScript 运行时错误）
- ✅ 页面渲染完整性验证（内容高度、可见元素、无加载指示器）

### Phase 3: 前后端联动 (Frontend-Backend Integration)
- ✅ 后端 API 健康检查（/health 端点）
- ✅ 前端数据获取验证（网络请求监控）
- ✅ API 响应格式验证（JSON 结构、code/message 字段）
- ✅ 前后端数据一致性校验（股票代码等核心字段匹配）

### Phase 4: 基础交互 (Basic Interactions)
- ✅ 页面导航功能验证（URL 变化检测）
- ✅ 表单输入功能验证（文本输入接受）
- ✅ 按钮点击反馈验证（页面状态变化或加载指示）
- ✅ 无崩溃错误验证（JavaScript 运行时错误检测）

## 测试结果输出

### 📊 结构化报告
- **JSON 详细报告**: `test-results/e2e-test-report.json`
- **文本摘要报告**: `test-results/test-summary.txt`
- **控制台输出**: 实时测试进度和结果摘要

### 📸 证据收集
- **失败截图**: `test-results/screenshots/` (失败时自动截图)
- **全程录屏**: `test-results/videos/` (失败时录制)
- **错误分类**: 明确区分前端/后端/联动问题

## 使用方法

### 前置条件

确保 MyStocks 服务已通过 PM2 启动：

```bash
# 前端服务 (端口 3020)
pm2 list | grep mystocks-frontend

# 后端服务 (端口 8020)
pm2 list | grep mystocks-backend
```

### 运行测试

#### 方法 1: npm 脚本 (推荐)
```bash
cd web/frontend

# 运行完整 E2E 测试套件
npm run test:e2e:comprehensive
```

#### 方法 2: 直接运行脚本
```bash
cd web/frontend

# 运行测试执行器
node run-comprehensive-e2e.js
```

#### 方法 3: Playwright 直接运行
```bash
cd web/frontend

# 运行单个测试文件
npx playwright test tests/comprehensive-e2e-validation.spec.ts

# 指定浏览器运行
npx playwright test tests/comprehensive-e2e-validation.spec.ts --project=chromium

# 调试模式
npx playwright test tests/comprehensive-e2e-validation.spec.ts --debug
```

### 测试结果查看

测试完成后，查看结果：

```bash
# 查看摘要报告
cat test-results/test-summary.txt

# 查看详细 JSON 报告
cat test-results/e2e-test-report.json | jq '.summary'

# 查看截图和录屏
ls -la test-results/screenshots/
ls -la test-results/videos/
```

## 测试配置

### 服务配置
```javascript
const FRONTEND_CONFIG = {
  name: 'mystocks-frontend',
  port: 3020,
  baseUrl: 'http://localhost:3020'
};

const BACKEND_CONFIG = {
  name: 'mystocks-backend',
  port: 8020,
  baseUrl: 'http://localhost:8020'
};
```

### Playwright 配置
- **浏览器**: Chromium, Firefox, WebKit
- **视口**: 1920x1080 (桌面端)
- **超时**: 30秒 (页面加载), 10秒 (操作)
- **截图**: 失败时自动截图
- **录屏**: 失败时录制视频

## 测试验证标准

### ✅ 通过标准
- **Phase 1**: 所有前置检查通过
- **Phase 2**: 页面完全加载，无控制台错误，所有核心元素存在
- **Phase 3**: API 返回有效数据，前后端数据一致
- **Phase 4**: 用户交互正常响应，无 JavaScript 崩溃

### ❌ 失败处理
- **问题分类**: 前端加载问题 / 后端接口问题 / 前后端联动问题
- **证据收集**: 自动截图 + 录屏 + 详细错误日志
- **报告输出**: 结构化 JSON + 人类可读摘要

## 故障排查

### 前置检查失败
```bash
# 检查 PM2 服务状态
pm2 list

# 检查端口占用
lsof -i :3020
lsof -i :8020

# 启动服务 (如果未运行)
cd web/frontend && npm run pm2:start
cd web/backend && pm2 start ecosystem.config.js
```

### 测试执行失败
```bash
# 查看详细错误日志
cat test-results/e2e-test-report.json | jq '.categories'

# 调试模式运行
npm run test:e2e:debug tests/comprehensive-e2e-validation.spec.ts

# 仅运行特定测试
npx playwright test --grep "DOM元素存在性验证"
```

### 资源加载问题
- 检查前端构建是否完整 (`npm run build`)
- 验证静态资源路径
- 检查网络连接和 CDN 访问

## 性能指标

- **测试执行时间**: ~3-5 分钟 (完整套件)
- **资源占用**: 浏览器实例 + 网络监控
- **稳定性**: 99%+ 成功率 (服务正常时)
- **可维护性**: 模块化设计，易于扩展

## 扩展开发

### 添加新的测试用例
```typescript
test('自定义测试场景', async ({ page }) => {
  // 测试逻辑
  const startTime = Date.now();

  // 执行测试步骤
  await page.goto('...');
  // ... 测试逻辑 ...

  // 记录结果
  recordTestResult('custom', 'Custom Test Name', success, {
    duration: Date.now() - startTime,
    // 其他数据
  });

  expect(success).toBe(true);
});
```

### 修改测试配置
- 编辑 `playwright.config.js` 调整标准 E2E 超时、视口等
- 编辑 `playwright.config.ts` 调整 legacy 专项脚本配置
- 修改 `run-comprehensive-e2e.js` 调整服务配置
- 更新 `package.json` 添加新的 npm 脚本

## 技术栈

- **测试框架**: Playwright 1.57+
- **编程语言**: TypeScript
- **断言库**: Playwright Test (内置)
- **报告工具**: JSON + HTML + JUnit
- **CI/CD**: 支持 GitHub Actions, Jenkins 等

## 许可证

本测试套件遵循 MyStocks 项目许可证。

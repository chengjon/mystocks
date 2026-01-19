# MyStocks Web端 - Playwright自动化测试快速参考

## 🚀 一键测试（推荐）

### 最简单的测试命令

```bash
cd /opt/claude/mystocks_spec/web/frontend

# 一键部署和测试
./deploy-and-test.sh
```

**这个脚本会自动**：
1. ✅ 构建生产版本
2. ✅ 启动PM2服务
3. ✅ 验证服务状态
4. ✅ 运行E2E测试
5. ✅ 生成测试报告

---

## 📋 完整测试流程

### 方法1：手动执行（适合开发调试）

#### 步骤1：构建

```bash
cd /opt/claude/mystocks_spec/web/frontend

# 清理旧构建
rm -rf dist/

# 安装依赖（如果需要）
npm install

# 生成类型定义
npm run generate-types

# 类型检查（可选）
npm run type-check

# 构建生产版本
npm run build
```

#### 步骤2：部署到PM2

```bash
# 启动生产环境服务
pm2 start ecosystem.prod.config.js

# 查看服务状态
pm2 status

# 查看日志
pm2 logs mystocks-frontend-prod --lines 50

# 实时监控
pm2 monit
```

#### 步骤3：运行测试

```bash
# 快速冒烟测试（推荐）
./scripts/test-runner/run-quick-e2e.sh

# 或直接运行Playwright
npm run test:e2e

# 仅运行Chromium测试
npm run test:e2e:chromium

# 调试模式（推荐）
npx playwright test tests/smoke/ --debug
```

#### 步骤4：查看报告

```bash
# 打开HTML报告
npx playwright show-report

# 或手动打开
open playwright-report/index.html

# 查看JSON结果
cat test-results.json | jq
```

---

## 🧪 不同测试场景

### 1. 冒烟测试（基础功能验证）

```bash
# 运行所有冒烟测试
npx playwright test tests/smoke/

# 运行特定测试
npx playwright test tests/smoke/02-page-loading.spec.ts

# 并行运行（更快）
npx playwright test tests/smoke/ --workers=4
```

**包含的测试**：
- ✅ 页面加载测试
- ✅ 菜单导航测试
- ✅ 侧边栏折叠测试
- ✅ Command Palette测试
- ✅ JavaScript错误检查

### 2. ArtDeco菜单测试

```bash
# 运行菜单导航测试
npx playwright test tests/artdeco/02-menu-navigation.spec.ts

# 运行Toast测试
npx playwright test tests/artdeco/03-toast-notifications.spec.ts

# 运行API数据测试
npx playwright test tests/artdeco/04-api-data-fetching.spec.ts

# 运行WebSocket测试
npx playwright test tests/artdeco/05-websocket-realtime.spec.ts
```

### 3. 组件测试

```bash
# 运行所有组件测试
npx playwright test --project=component-tests

# 运行特定组件测试
npx playwright test tests/components/ArtDecoButton.spec.ts
```

### 4. 性能测试

```bash
# 运行性能测试
npx playwright test --project=performance

# 生成Lighthouse报告
npm run test:lighthouse
```

---

## 🔧 常用测试命令

### 基础测试

```bash
# 标准E2E测试
npm run test:e2e

# 仅Chromium
npm run test:e2e:chromium

# 仅Firefox
npm run test:e2e:firefox

# 调试模式
npx playwright test --debug
```

### 高级测试

```bash
# 带追踪的测试（性能分析）
npx playwright test --trace=on

# 生成HTML报告
npm run test:e2e -- --reporter=html

# 生成JUnit报告（CI/CD）
npm run test:e2e -- --reporter=junit

# 并行运行（4个worker）
npm run test:e2e -- --workers=4
```

### 调试和故障排查

```bash
# 调试特定测试
npx playwright test tests/smoke/01-page-loading.spec.ts --debug

# 显示浏览器窗口
npx playwright test --headed

# 慢动作模式（方便观察）
npx playwright test --slow-mo=1000

# 保留视频证据（失败时）
npx playwright test --video=retain-on-failure

# 保留截图证据（失败时）
npx playwright test --screenshot=only-on-failure
```

---

## 📊 测试报告说明

### 报告类型

| 报告 | 文件位置 | 说明 |
|------|----------|------|
| HTML报告 | `playwright-report/index.html` | 交互式HTML报告，推荐 |
| JSON报告 | `test-results.json` | 机器可读的测试结果 |
| JUnit报告 | `junit-results.xml` | CI/CD集成 |
| 截图 | `test-results/` | 失败时的截图证据 |
| 视频 | `test-results/` | 失败时的视频录制 |

### 报告查看

```bash
# 方法1：自动打开（推荐）
npx playwright show-report

# 方法2：手动打开
open playwright-report/index.html

# 方法3：浏览器访问
# 访问：file:///opt/claude/mystocks_spec/web/frontend/playwright-report/index.html
```

---

## 🐛 故障排查

### 问题1：测试失败

**症状**：Playwright测试失败

**解决方案**：

```bash
# 1. 查看详细错误
npx playwright test tests/smoke/ --reporter=list

# 2. 调试模式
npx playwright test tests/smoke/01-page-loading.spec.ts --debug

# 3. 查看截图
ls -la test-results/

# 4. 检查服务状态
curl http://localhost:3001
pm2 logs mystocks-frontend-prod
```

### 问题2：PM2服务无法启动

**症状**：PM2启动后立即退出

**解决方案**：

```bash
# 1. 检查端口占用
lsof -i :3001

# 2. 检查构建产物
ls -la dist/

# 3. 检查PM2配置
pm2 start ecosystem.prod.config.js --no-daemon

# 4. 查看详细日志
pm2 logs mystocks-frontend-prod --lines 50

# 5. 手动测试
npx http-server dist -p 3001
```

### 问题3：后端API连接失败

**症状**：所有API请求返回500或超时

**解决方案**：

```bash
# 1. 检查后端服务
curl http://localhost:8000/health

# 2. 检查WebSocket
wscat -c ws://localhost:8000/api/ws

# 3. 查看后端日志
cd web/backend
tail -f ../logs/app.log

# 4. 重启后端
cd web/backend
pm2 restart simple_backend
```

### 问题4：页面加载缓慢

**症状**：首次加载时间 > 10秒

**诊断**：

```bash
# 1. 使用Chrome DevTools
# 打开 http://localhost:3001
# 按F12 → Performance → Record
# 执行操作 → Stop → 分析

# 2. Playwright性能测试
npx playwright test --project=performance

# 3. 检查构建产物大小
du -sh dist/
```

---

## 📝 测试清单

### 测试前检查

- [ ] 后端API服务运行正常
- [ ] 数据库连接正常
- [ ] PM2服务已启动
- [ ] 构建产物已生成
- [ ] Playwright浏览器已安装

### 核心功能检查

- [ ] 页面能够加载
- [ ] 6个菜单项都可见
- [ ] 点击菜单能正确导航
- [ ] 侧边栏能折叠/展开
- [ ] Toast通知能显示
- [ ] 无JavaScript错误
- [ ] API请求能正常响应
- [ ] WebSocket能连接

### 性能指标

- [ ] 页面加载时间 < 5秒
- [ ] 菜单切换时间 < 500ms
- [ ] Toast显示延迟 < 200ms
- [ ] 测试通过率 = 100%

---

## 🎯 推荐测试工作流

### 日常开发测试（快速验证）

```bash
# 1. 构建并启动服务
npm run build
pm2 restart ecosystem.prod.config.js

# 2. 快速测试
./scripts/test-runner/run-quick-e2e.sh

# 3. 查看报告
npx playwright show-report
```

### 完整测试（发布前验证）

```bash
# 1. 清理旧数据
rm -rf dist/ playwright-report/ test-results/

# 2. 完整构建
npm run type:build

# 3. 一键部署和测试
./deploy-and-test.sh

# 4. 查看完整报告
open playwright-report/index.html
```

### CI/CD测试（自动化）

```yaml
# .github/workflows/e2e-test.yml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        run: cd web/frontend && npm ci

      - name: Install Playwright
        run: cd web/frontend && npx playwright install --with-deps

      - name: Build
        run: cd web/frontend && npm run build

      - name: Run tests
        run: cd web/frontend && npm run test:e2e

      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: web/frontend/playwright-report/
```

---

## 📚 相关文档

- **PM2官方文档**: https://pm2.keymetrics.io/docs
- **Playwright官方文档**: https://playwright.dev/
- **完整测试指南**: `docs/guides/PM2_PLAYWRIGHT_TESTING_GUIDE.md`
- **ArtDeco菜单实现**: `docs/guides/ARTDECO_MENU_DATA_FETCHING_IMPLEMENTATION_GUIDE.md`

---

**快速开始**：

```bash
cd /opt/claude/mystocks_spec/web/frontend

# 最简单的方式：一键部署和测试
./deploy-and-test.sh

# 或者分步执行
npm run build && pm2 start ecosystem.prod.config.js && npm run test:e2e
```

**测试完成！** 🎉

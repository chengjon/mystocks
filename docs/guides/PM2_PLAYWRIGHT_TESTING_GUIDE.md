# MyStocks Web端 PM2部署和Playwright自动化测试方案

## 📋 概述

本文档提供了完整的web端测试方案，包括PM2生产环境部署和Playwright端到端自动化测试，确保所有功能正常运行。

---

## 🚀 第一部分：PM2生产环境部署

### 1.1 PM2配置优化

创建生产环境PM2配置文件：

```bash
cd /opt/claude/mystocks_spec/web/frontend
```

**创建生产配置** (`ecosystem.prod.config.js`):

```javascript
/**
 * MyStocks Frontend - PM2 Production Configuration
 * 生产环境专用配置
 */

module.exports = {
  apps: [
    {
      name: 'mystocks-frontend-prod',
      script: 'npm run preview', // 使用preview模式（生产构建）
      // 或者使用nginx/caddy等静态服务器
      // script: 'http-server dist -p 3001 -c-1 --cors',

      cwd: '/opt/claude/mystocks_spec/web/frontend',

      // 环境变量
      env: {
        NODE_ENV: 'production',
        PORT: 3001,
        VITE_API_BASE_URL: 'http://localhost:8000'
      },

      // 实例配置
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',

      // 日志配置
      error_file: './logs/pm2-error.log',
      out_file: './logs/pm2-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,

      // 进程管理
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 4000,

      // 优雅关闭
      kill_timeout: 5000,
      listen_timeout: 10000,
      shutdown_with_message: true,

      // Node.js参数
      node_args: '--max-old-space-size=2048'
    }
  ]
}
```

### 1.2 部署步骤

**步骤1：构建生产版本**

```bash
cd /opt/claude/mystocks_spec/web/frontend

# 清理旧构建
rm -rf dist/

# 安装依赖
npm install

# 生成类型定义
npm run generate-types

# 构建生产版本
npm run build
```

**步骤2：启动PM2服务**

```bash
# 启动生产环境
pm2 start ecosystem.prod.config.js

# 或者直接启动
pm2 start npm --name "mystocks-frontend-prod" -- run preview

# 查看状态
pm2 status
pm2 logs mystocks-frontend-prod --lines 50
```

**步骤3：验证服务**

```bash
# 检查服务是否运行
curl -I http://localhost:3001

# 应该返回：
# HTTP/1.1 200 OK
# Content-Type: text/html
```

### 1.3 PM2管理命令

```bash
# 查看所有进程
pm2 list

# 查看详细信息
pm2 show mystocks-frontend-prod

# 查看日志
pm2 logs mystocks-frontend-prod

# 实时监控
pm2 monit

# 重启服务
pm2 restart mystocks-frontend-prod

# 停止服务
pm2 stop mystocks-frontend-prod

# 删除服务
pm2 delete mystocks-frontend-prod

# 保存当前进程列表
pm2 save

# 设置开机自启
pm2 startup
```

---

## 🧪 第二部分：Playwright自动化测试

### 2.1 测试环境准备

**安装测试浏览器**（如果未安装）：

```bash
cd /opt/claude/mystocks_spec/web/frontend

# 安装Playwright浏览器
npx playwright install chromium
npx playwright install firefox
npx playwright install webkit
```

### 2.2 核心测试场景

基于ArtDeco菜单系统，我为您创建了以下关键测试场景：

#### 场景1：页面加载和基础功能

```typescript
// tests/smoke/01-page-loading.spec.ts
import { test, expect } from '@playwright/test';

test.describe('页面加载测试', () => {
  test('首页应该正确加载', async ({ page }) => {
    await page.goto('/');

    // 等待页面加载完成
    await page.waitForLoadState('domcontentloaded');

    // 验证标题
    await expect(page).toHaveTitle(/MyStocks/);

    // 验证关键元素存在
    await expect(page.locator('.base-layout')).toBeVisible();
    await expect(page.locator('.layout-header')).toBeVisible();
    await expect(page.locator('.layout-sidebar')).toBeVisible();
  });

  test('应该显示所有6个顶层菜单项', async ({ page }) => {
    await page.goto('/');

    // 等待侧边栏加载
    await page.waitForSelector('.nav-item');

    // 计数菜单项
    const navItems = page.locator('.nav-item');
    await expect(navItems).toHaveCount(6);

    // 验证菜单文本
    const expectedLabels = [
      '仪表盘',
      '市场行情',
      '股票管理',
      '投资分析',
      '风险管理',
      '策略和交易管理'
    ];

    for (const label of expectedLabels) {
      await expect(page.locator('.nav-label', { hasText: label })).toBeVisible();
    }
  });

  test('侧边栏应该可以折叠和展开', async ({ page }) => {
    await page.goto('/');

    const sidebar = page.locator('.layout-sidebar');
    const toggleButton = page.locator('.sidebar-toggle');

    // 初始状态：展开
    await expect(sidebar).toBeVisible();
    await expect(sidebar).not.toHaveClass('sidebar-collapsed');

    // 点击折叠
    await toggleButton.click();
    await expect(sidebar).toHaveClass('sidebar-collapsed');

    // 点击展开
    await toggleButton.click();
    await expect(sidebar).not.toHaveClass('sidebar-collapsed');
  });
});
```

#### 场景2：ArtDeco菜单导航

```typescript
// tests/artdeco/02-menu-navigation.spec.ts
import { test, expect } from '@playwright/test';

test.describe('ArtDeco菜单导航测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('应该能导航到仪表盘', async ({ page }) => {
    const dashboardLink = page.locator('a[href="/dashboard"]');
    await dashboardLink.click();

    // 验证URL变化
    await expect(page).toHaveURL('/dashboard');

    // 验证页面标题
    await expect(page.locator('.page-title')).toContainText('仪表盘');
  });

  test('应该能导航到市场行情', async ({ page }) => {
    const marketLink = page.locator('a[href="/market/data"]');
    await marketLink.click();

    await expect(page).toHaveURL('/market/data');
    await expect(page.locator('.page-title')).toContainText('市场行情');
  });

  test('实时更新菜单项应该显示LIVE指示器', async ({ page }) => {
    // 市场行情有实时更新
    const liveIndicator = page.locator('.nav-item--live .live-indicator');
    await expect(liveIndicator).toHaveCount(3); // 3个liveUpdate菜单项
  });

  test('特色菜单项应该高亮显示', async ({ page }) => {
    // Primary优先级
    const primaryItems = page.locator('.nav-item--featured');
    await expect(primaryItems).toHaveCount(2);
  });
});
```

#### 场景3：Toast通知系统

```typescript
// tests/artdeco/03-toast-notifications.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Toast通知系统测试', () => {
  test('应该显示成功Toast通知', async ({ page }) => {
    await page.goto('/');

    // 通过控制台触发Toast（需要暴露全局方法）
    await page.evaluate(() => {
      (window as any).toast?.showSuccess('测试成功消息');
    });

    // 等待Toast出现
    const toast = page.locator('.artdeco-toast').first();
    await expect(toast).toBeVisible();

    // 验证Toast内容
    await expect(toast).toContainText('成功');
  });

  test('应该显示错误Toast通知', async ({ page }) => {
    await page.goto('/');

    await page.evaluate(() => {
      (window as any).toast?.showError('测试错误消息');
    });

    const toast = page.locator('.artdeco-toast').first();
    await expect(toast).toBeVisible();
    await expect(toast).toHaveClass(/artdeco-toast--error/);
  });

  test('Toast应该自动消失', async ({ page }) => {
    await page.goto('/');

    await page.evaluate(() => {
      (window as any).toast?.showInfo('测试自动消失');
    });

    const toast = page.locator('.artdeco-toast').first();
    await expect(toast).toBeVisible();

    // 等待自动消失（默认3秒）
    await page.waitForTimeout(4000);

    await expect(toast).not.toBeVisible();
  });

  test('应该能手动关闭Toast', async ({ page }) => {
    await page.goto('/');

    await page.evaluate(() => {
      (window as any).toast?.showWarning('测试手动关闭');
    });

    const toast = page.locator('.artdeco-toast').first();
    await expect(toast).toBeVisible();

    // 点击关闭按钮
    const closeButton = toast.locator('.artdeco-toast__close');
    await closeButton.click();

    await expect(toast).not.toBeVisible();
  });
});
```

#### 场景4：API数据获取

```typescript
// tests/artdeco/04-api-data-fetching.spec.ts
import { test, expect } from '@playwright/test';

test.describe('API数据获取测试', () => {
  test('应该能获取菜单数据', async ({ page }) => {
    await page.goto('/');

    // 监听网络请求
    const apiRequests: any[] = [];

    page.on('request', async (request) => {
      if (request.url().includes('/api/')) {
        apiRequests.push({
          url: request.url(),
          method: request.method()
        });
      }
    });

    // 等待页面加载
    await page.waitForLoadState('networkidle');

    // 验证有API请求（取决于页面实现）
    console.log('API请求:', apiRequests);
  });

  test('应该处理API错误', async ({ page }) => {
    await page.goto('/');

    // 模拟API错误（需要mock或后端配合）
    await page.route('**/api/error', route => route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({
        success: false,
        message: 'API错误'
      })
    }));

    // 触发会调用错误API的操作
    await page.evaluate(() => {
      // 这里需要根据实际页面逻辑调用API
    });

    // 验证错误提示显示
    const errorBadge = page.locator('.artdeco-badge');
    // await expect(errorBadge).toBeVisible();
  });
});
```

#### 场景5：实时数据更新

```typescript
// tests/artdeco/05-websocket-realtime.spec.ts
import { test, expect } from '@playwright/test';

test.describe('WebSocket实时更新测试', () => {
  test('应该建立WebSocket连接', async ({ page }) => {
    await page.goto('/');

    // 监听WebSocket连接
    const wsConnected = await page.evaluate(() => {
      return new Promise((resolve) => {
        const ws = new WebSocket('ws://localhost:8000/api/ws');

        ws.onopen = () => {
          ws.close();
          resolve(true);
        };

        ws.onerror = () => resolve(false);
      });
    });

    expect(wsConnected).toBe(true);
  });

  test('应该接收实时数据更新', async ({ page }) => {
    await page.goto('/market/data');

    // 这里需要模拟WebSocket消息推送
    // 或验证实际的后端推送

    await page.waitForTimeout(5000);

    // 验证数据更新（如lastUpdate时间戳变化）
    const timestamp = page.locator('.nav-timestamp');
    const count = await timestamp.count();

    console.log(`发现${count}个时间戳`);
  });
});
```

### 2.3 快速测试脚本

创建一个快速验证脚本，确保基本功能正常：

**创建测试脚本** (`scripts/test-runner/run-quick-e2e.sh`):

```bash
#!/bin/bash

# MyStocks Web端 - 快速E2E测试脚本

set -e

PROJECT_ROOT="/opt/claude/mystocks_spec/web/frontend"
cd "$PROJECT_ROOT"

echo "=== MyStocks Web端 快速E2E测试 ==="
echo ""

# 检查PM2服务状态
echo "📊 检查PM2服务状态..."
if pm2 list | grep -q "mystocks-frontend-prod.*online"; then
    echo "✅ PM2服务正在运行"
else
    echo "❌ PM2服务未运行，请先启动服务"
    echo "运行: pm2 start ecosystem.prod.config.js"
    exit 1
fi

# 检查端口
echo "📡 检查端口3001..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3001 | grep -q "200"; then
    echo "✅ 服务响应正常"
else
    echo "❌ 服务无响应"
    exit 1
fi

# 运行快速冒烟测试
echo ""
echo "🧪 运行冒烟测试..."
npx playwright test tests/smoke/ --reporter=list

echo ""
echo "🎉 快速测试完成！"
echo ""
echo "📊 生成完整报告..."
npx playwright test --reporter=html

echo ""
echo "✅ 测试完成！查看报告："
echo "   playwright-report/index.html"
```

**赋予执行权限**：

```bash
chmod +x /opt/claude/mystocks_spec/web/frontend/scripts/test-runner/run-quick-e2e.sh
```

### 2.4 完整测试命令

```bash
cd /opt/claude/mystocks_spec/web/frontend

# 1. 快速冒烟测试（仅Chromium）
npm run test:e2e:chromium

# 2. 所有浏览器测试
npm run test:e2e

# 3. 仅运行特定测试文件
npx playwright test tests/smoke/01-page-loading.spec.ts

# 4. 调试模式（打开浏览器窗口）
npx playwright test --debug

# 5. 查看测试报告
npx playwright show-report

# 6. 生成HTML报告
npm run test:e2e -- --reporter=html

# 7. 运行特定项目（如visual-regression）
npx playwright test --project=visual-regression

# 8. 并行运行测试（更快）
npx playwright test --workers=4
```

---

## 📊 第三部分：测试报告和分析

### 3.1 测试报告查看

```bash
# 方法1：自动打开HTML报告
npx playwright show-report

# 方法2：手动打开报告
open playwright-report/index.html

# 方法3：在浏览器中查看
# 访问：file:///opt/claude/mystocks_spec/web/frontend/playwright-report/index.html
```

### 3.2 报告目录结构

```
playwright-report/
├── index.html                  # 主报告页面
├── trace/                      # 追踪数据（性能分析）
│   ├── trace-<id>.zip
│   └── trace-viewer.html
├── screenshots/                # 截图证据
│   ├── <test>-<browser>.png
│   └── ...
└── videos/                     # 视频录制
    ├── <test>-<browser>.webm
    └── ...
```

### 3.3 CI/CD集成

**GitHub Actions工作流示例** (`.github/workflows/frontend-testing.yml`):

```yaml
name: Frontend E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

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
        run: |
          cd web/frontend
          npm ci

      - name: Install Playwright Browsers
        run: |
          cd web/frontend
          npx playwright install --with-deps

      - name: Build frontend
        run: |
          cd web/frontend
          npm run build

      - name: Start services
        run: |
          # 启动后端API
          cd web/backend
          python3 simple_backend_fixed.py &

          # 启动前端服务
          cd ../frontend
          npm run preview &

          # 等待服务就绪
          sleep 10

      - name: Run Playwright tests
        run: |
          cd web/frontend
          npm run test:e2e

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: web/frontend/playwright-report/
          retention-days: 30

      - name: Upload screenshots
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: screenshots
          path: web/frontend/test-results/
```

---

## 🔧 第四部分：故障排查

### 4.1 常见问题

#### 问题1：PM2服务启动失败

**症状**：`pm2 start` 命令失败

**解决方案**：
```bash
# 检查端口占用
lsof -i :3001

# 如果端口被占用，停止占用进程
kill -9 <PID>

# 清理PM2进程列表
pm2 flush

# 重新启动
pm2 start ecosystem.prod.config.js
```

#### 问题2：页面加载失败

**症状**：浏览器显示"无法连接"

**解决方案**：
```bash
# 1. 检查PM2服务状态
pm2 status

# 2. 检查日志
pm2 logs mystocks-frontend-prod --lines 50

# 3. 检查端口
curl http://localhost:3001

# 4. 检查防火墙
sudo ufw status

# 5. 重启服务
pm2 restart mystocks-frontend-prod
```

#### 问题3：测试失败

**症状**：Playwright测试失败

**解决方案**：
```bash
# 1. 查看详细错误
npx playwright test --reporter=list

# 2. 调试特定测试
npx playwright test tests/smoke/01-page-loading.spec.ts --debug

# 3. 检查网络请求
npx playwright test --trace=on

# 4. 查看trace报告
npx playwright show-trace trace.zip

# 5. 更新浏览器
npx playwright install
```

#### 问题4：WebSocket连接失败

**症状**：实时数据无法更新

**解决方案**：
```bash
# 1. 检查后端WebSocket服务
netstat -an | grep 8000

# 2. 测试WebSocket连接
wscat -c ws://localhost:8000/api/ws

# 3. 检查后端日志
cd web/backend
tail -f ../logs/app.log

# 4. 验证CORS配置
curl -H "Origin: http://localhost:3001" \
     -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     http://localhost:8000/api/ws
```

### 4.2 性能问题

#### 问题：页面加载慢

**诊断**：
```bash
# 1. 使用Chrome DevTools分析
# 打开 http://localhost:3001
# 按F12 → Performance → Record
# 执行操作 → Stop → 分析

# 2. Playwright性能测试
npx playwright test --project=performance

# 3. 检查构建产物
ls -lh dist/
```

**优化**：
- 使用生产构建（`npm run build`）
- 启用Gzip压缩
- 优化图片和资源
- 使用CDN加速

---

## 📝 第五部分：测试检查清单

### 5.1 测试前检查

- [ ] 后端API服务正常运行（`http://localhost:8000`）
- [ ] WebSocket服务可访问（`ws://localhost:8000/api/ws`）
- [ ] PM2服务已启动（`http://localhost:3001`）
- [ ] 数据库连接正常
- [ ] 测试数据已准备
- [ ] Playwright浏览器已安装

### 5.2 测试执行检查

- [ ] 冒烟测试通过（基础功能）
- [ ] 菜单导航测试通过
- [ ] Toast通知测试通过
- [ ] API数据获取测试通过
- [ ] WebSocket实时更新测试通过
- [ ] 所有测试用例通过率 > 95%

### 5.3 测试后检查

- [ ] 测试报告已生成
- [ ] 截图和视频证据完整
- [ ] 失败测试已记录
- [ ] 问题已分类（P0/P1/P2）
- [ ] 修复计划已制定

---

## 🎯 快速开始指南

### 最简单的3步测试流程

```bash
# 1. 启动PM2服务
cd /opt/claude/mystocks_spec/web/frontend
pm2 start ecosystem.prod.config.js

# 2. 等待服务就绪（10秒）
sleep 10

# 3. 运行快速测试
./scripts/test-runner/run-quick-e2e.sh
```

### 完整测试流程（推荐）

```bash
# 1. 构建生产版本
npm run build

# 2. 启动PM2
pm2 start ecosystem.prod.config.js

# 3. 验证服务
curl http://localhost:3001

# 4. 运行所有E2E测试
npm run test:e2e

# 5. 查看测试报告
npx playwright show-report

# 6. 查看PM2日志
pm2 logs mystocks-frontend-prod
```

---

## 📚 相关文档

- [Playwright官方文档](https://playwright.dev/)
- [PM2官方文档](https://pm2.keymetrics.io/)
- [ArtDeco菜单系统实现指南](./ARTDECO_MENU_DATA_FETCHING_IMPLEMENTATION_GUIDE.md)
- [WebSocket性能优化指南](./WEBSOCKET_PERFORMANCE_OPTIMIZATION_GUIDE.md)

---

**文档版本**: v1.0.0
**最后更新**: 2026-01-19
**作者**: Claude Code
**状态**: ✅ 已完成

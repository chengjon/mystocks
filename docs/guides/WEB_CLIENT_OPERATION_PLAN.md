# MyStocks Web端正常运行 - 后续建议

**文档版本**: v1.1
**创建日期**: 2026-01-20
**最后更新**: 2026-01-20
**作者**: MyStocks Development Team
**状态**: Approved
**相关文档**:
- 📊 [路由统一完成报告](../reports/ROUTE_UNIFICATION_ARTDECO_REPORT.md)
- 🧪 [E2E测试最终报告](../reports/E2E_TEST_FINAL_REPORT.md)
- 🎨 [ArtDeco集成测试计划](../reports/WEB_FRONTEND_ARTDECO_INTEGRATION_TEST_PLAN.md)
- 🔧 [CORS配置](../../web/backend/app/core/config.py)
- ⚙️ [PM2配置](../../web/frontend/ecosystem.config.js)

---

## 背景

您已成功统一路由结构并更新了冒烟测试，这是一个巨大的进展！当前E2E测试中剩余的4个失败均归因于**环境错误（CORS/WebSocket）**，这表明核心应用功能和渲染已基本正常。

为了实现Web端的正常运行，我们接下来需要专注于解决这些环境问题，确保前端能够与后端服务进行顺畅的通信。

---

## 🚀 快速问题诊断清单

**在执行详细步骤前，请先确认以下检查项**:

### 服务状态检查
- [ ] **前端服务运行** - 访问 `http://localhost:3001` 能看到页面
- [ ] **后端服务运行** - `curl http://localhost:8000/health` 返回200
- [ ] **PM2进程列表** - `pm2 list` 显示 `mystocks-frontend-prod` 为 online

### 配置验证
- [ ] **CORS配置** - 检查 `web/backend/app/core/config.py` 包含端口3001
- [ ] **WebSocket端点** - 检查 `web/backend/app/api/websocket.py` 存在（未注释）
- [ ] **环境变量** - `.env` 文件配置正确（后端数据库、JWT密钥等）

### 浏览器测试
- [ ] **浏览器控制台** - 打开 F12 → Console，无JavaScript错误
- [ ] **网络请求** - F12 → Network，检查API请求状态
- [ ] **CORS错误** - 控制台无 "Access blocked by CORS policy" 错误

### 自动化测试
- [ ] **DOM结构检查** - `node web/frontend/check-artdeco-dom.mjs`
- [ ] **API检查** - `node web/frontend/check-api.mjs`
- [ ] **E2E测试** - `npx playwright test tests/smoke/02-page-loading.spec.ts`

**如果以上所有项都确认✅，但问题仍存在，请继续阅读下文。**

---

## 🔍 已知问题和快速解决方案

### 问题1: CORS错误持续存在

**症状**:
```
浏览器控制台显示:
Access to XMLHttpRequest at 'http://localhost:8000/api/...'
from origin 'http://localhost:3001' has been blocked by CORS policy
```

**根本原因**: 后端CORS配置未包含前端端口，或后端服务未重启

**解决方案**:
```bash
# 1. 验证后端CORS配置
grep -A 5 "cors_origins_str" web/backend/app/core/config.py
# 应该包含: http://localhost:3001

# 2. 重启后端服务（使CORS配置生效）
pm2 restart all  # 如果使用PM2
# 或
uvicorn web.backend.app.main:app --reload --host 0.0.0.0 --port 8000

# 3. 清除浏览器缓存
# Chrome: Ctrl+Shift+Delete → 清除缓存
# 或使用无痕模式测试: Ctrl+Shift+N
```

**预防措施**:
- 修改CORS配置后，必须重启后端服务
- 开发时使用无痕模式避免缓存问题

---

### 问题2: WebSocket连接失败

**症状**:
```
浏览器控制台显示:
WebSocket connection failed: ws://localhost:8000/api/ws
```

**根本原因**:
1. WebSocket端点被注释（代码存在但未启用）
2. 后端服务未启动WebSocket支持
3. WebSocket URL配置错误

**解决方案**:
```bash
# 1. 检查WebSocket代码状态
grep -n "websocket" web/backend/app/main.py
# 如果被注释，需要取消注释

# 2. 检查WebSocket端点文件
ls -la web/backend/app/api/websocket.py
# 文件应该存在且未被注释

# 3. 验证WebSocket URL
# 在浏览器控制台执行:
new WebSocket('ws://localhost:8000/api/ws')

# 4. 检查后端日志
pm2 logs backend --lines 50
# 查找WebSocket相关错误信息
```

**临时解决方案**:
如果WebSocket不是核心功能，可以暂时禁用相关功能：
```javascript
// 在前端代码中添加WebSocket连接检查
if (typeof WebSocket === 'undefined') {
  console.warn('WebSocket not supported, using polling fallback');
}
```

---

### 问题3: 页面显示"Loading..."但不加载内容

**症状**:
- 页面标题正确，但内容区域只显示 "Loading..."
- 浏览器控制台无JavaScript错误
- Vue Devtools显示Vue实例已挂载

**根本原因**:
1. Vite构建时的循环依赖问题（已修复）
2. API请求超时或失败
3. Vue Router未正确匹配路由

**解决方案**:
```bash
# 1. 检查Vite构建配置
grep -A 10 "manualChunks" web/frontend/vite.config.ts
# 确认Element Plus已合并到vue-vendor chunk

# 2. 重新构建应用
cd web/frontend
npm run build:no-types

# 3. 重启前端服务
pm2 restart mystocks-frontend-prod

# 4. 检查路由配置
grep -n "path.*dashboard" web/frontend/src/router/index.ts
# 确认ArtDeco路由未被注释
```

**诊断工具**:
```bash
# 使用项目的诊断工具
node web/frontend/check-actual-content.mjs
node web/frontend/check-artdeco-dom.mjs
```

---

### 问题4: E2E测试超时

**症状**:
```
Test timeout: 30000ms exceeded
```

**根本原因**:
1. 页面加载时间超过30秒
2. 某些资源加载失败导致页面挂起
3. 选择器不匹配，等待元素超时

**解决方案**:
```bash
# 1. 增加测试超时时间
# 在测试文件中添加:
test.setTimeout(60000);  // 60秒

# 2. 使用调试模式运行测试
npx playwright test tests/smoke/02-page-loading.spec.ts --debug

# 3. 检查页面加载性能
# 在浏览器开发者工具中:
# F12 → Network → 查看"Loading"时间最长的资源

# 4. 简化测试用例
# 先测试核心功能，再逐步添加验证步骤
```

---

## 🚀 后续步骤建议

### 1. 解决剩余的E2E测试失败 (CORS/WebSocket) - **最高优先级** 🔴

这是当前Web端无法"正常运行"的直接原因。

#### 目标
确保前端能与所有后端服务（API和WebSocket）进行正常通信，消除所有CORS和WebSocket连接错误。

#### 当前状态

**后端服务运行情况**:
```bash
# ✅ 已验证的服务状态
前端服务: http://localhost:3001 (PM2: mystocks-frontend-prod)
后端API: http://localhost:8000 (FastAPI主服务)
后端健康检查: http://localhost:8000/health

# ⚠️ 待确认的服务
WebSocket服务: ws://localhost:8000/api/ws
# 代码位置: web/backend/app/api/websocket.py
# 状态: 代码存在但可能被注释
```

**CORS配置验证**:
```bash
# ✅ 后端CORS配置已包含端口3001
# 文件: web/backend/app/core/config.py
# 配置内容:
cors_origins_str: str = (
    "http://localhost:3000,http://localhost:3001,http://localhost:3002,"
    "http://localhost:3003,http://localhost:3004,http://localhost:3005,..."
)
```

#### 行动方案

**步骤1: 验证后端服务状态**

```bash
# 1.1 检查后端服务运行状态
pm2 list
# 应该看到: backend-* 或 mystocks-backend-* 服务为 online 状态

# 1.2 测试后端健康检查
curl http://localhost:8000/health
# 预期输出: {"status": "healthy"} 或类似JSON响应

# 1.3 检查后端日志（查找启动错误）
pm2 logs backend --lines 50 --nostream
# 或查看实时日志:
pm2 logs backend --lines 0
```

**步骤2: 审查后端CORS配置**

```bash
# 2.1 验证CORS配置包含前端端口
grep -A 10 "cors_origins_str" web/backend/app/core/config.py
# 应该包含: http://localhost:3001

# 2.2 如果配置不包含，需要添加并重启后端
# 编辑 web/backend/app/core/config.py
# 在 cors_origins_str 中添加: http://localhost:3001

# 2.3 重启后端服务使CORS配置生效
pm2 restart backend
# 或如果没有使用PM2:
pkill -f "uvicorn.*app.main"
uvicorn web.backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**FastAPI CORS配置示例** (已在项目中实现):
```python
# web/backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_str.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**步骤3: 验证WebSocket连接**

```bash
# 3.1 检查WebSocket端点文件
cat web/backend/app/api/websocket.py | head -20
# 应该看到WebSocket路由定义:
# @router.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):

# 3.2 检查main.py是否注册了WebSocket路由
grep -n "websocket" web/backend/app/main.py
# 应该看到:
# app.include_router(websocket_router, prefix="/api", tag="WebSocket")

# 3.3 在浏览器控制台测试WebSocket连接
# 打开 http://localhost:3001/#/dashboard
# 按F12打开控制台，执行:
new WebSocket('ws://localhost:8000/api/ws')
# 如果显示: WebSocket {url: "ws://localhost:8000/api/ws", readyState: 0}
# 说明连接尝试成功（readyState: 0 = CONNECTING）

# 3.4 检查WebSocket在Network面板
# F12 → Network → WS 标签
# 刷新页面，查看是否有 ws://localhost:8000/api/ws 连接
# 状态应该是: 101 Switching Protocols
```

**步骤4: 使用项目诊断工具（推荐）**

```bash
# 4.1 一键检查前端API连接
cd web/frontend
node check-api.mjs

# 4.2 检查DOM结构和CSS类
node check-artdeco-dom.mjs

# 4.3 检查菜单配置
node inspect-menu.mjs

# 4.4 运行CORS检查测试
npx playwright test tests/smoke/02-page-loading.spec.ts --reporter=list
```

**步骤5: 浏览器手动诊断（如自动化工具无法检测）**

```bash
# 5.1 在浏览器中打开前端
open http://localhost:3001/#/dashboard
# 或 Windows: start http://localhost:3001/#/dashboard

# 5.2 打开开发者工具 (F12)
# Console标签: 查找CORS错误、WebSocket错误
# Network标签:
#   - 筛选: "WS" 查看WebSocket连接
#   - 筛选: "XHR/Fetch" 查看API请求
#   - 点击失败的请求 → 查看"Headers" → "Response Headers"

# 5.3 常见错误模式
# CORS错误:
#   "Access to XMLHttpRequest blocked by CORS policy"
# WebSocket错误:
#   "WebSocket connection failed"
#   "Unexpected response code: 403/404"
```

#### 替代方案 - 自动化检测

**使用Playwright检测网络错误**:
```typescript
// tests/cors-websocket-check.spec.ts
import { test, expect } from '@playwright/test';

test('CORS和WebSocket错误自动检测', async ({ page }) => {
  const failedRequests: { url: string; error: string }[] = [];
  const wsErrors: string[] = [];

  // 监听请求失败
  page.on('requestfailed', request => {
    const failure = request.failure();
    if (failure) {
      failedRequests.push({
        url: request.url(),
        error: failure.errorText
      });
    }
  });

  // 监听WebSocket错误
  page.on('pageerror', error => {
    if (error.message.includes('WebSocket')) {
      wsErrors.push(error.message);
    }
  });

  // 导航到仪表板
  await page.goto('/#/dashboard');
  await page.waitForLoadState('networkidle');

  // 断言无CORS错误
  const corsErrors = failedRequests.filter(r =>
    r.error.includes('CORS') || r.error.includes('blocked')
  );
  expect(corsErrors.length).toBe(0);

  // 断言无WebSocket错误
  expect(wsErrors.length).toBe(0);

  // 输出诊断信息
  console.log('✅ 无CORS错误');
  console.log('✅ 无WebSocket错误');
  console.log(`✅ 总请求数: ${await page.evaluate(() => performance.getEntriesByType('resource').length)}`);
});
```

运行检测:
```bash
npx playwright test tests/cors-websocket-check.spec.ts --reporter=list
```

#### 预期成果
- ✅ 所有与后端通信相关的E2E测试通过
- ✅ 浏览器控制台无CORS错误
- ✅ WebSocket连接成功建立（状态: 101 Switching Protocols）
- ✅ 前端页面能够加载数据并接收实时更新
- ✅ 测试通过率从78%提升到95%+

### 2. 更新剩余的E2E测试文件 - **高优先级** 🟠

虽然冒烟测试已更新，但其他测试文件可能仍与ArtDeco优先架构不匹配。

#### 目标
使所有Playwright测试文件与ArtDeco优先路由结构和组件实现完全对齐，确保测试套件的全面性和可靠性。

#### 当前测试文件状态

**✅ 已更新的测试文件**:
- `tests/smoke/02-page-loading.spec.ts` - 冒烟测试（路由统一后已更新）

**⚠️ 需要检查的测试文件**:
```bash
# 搜索可能仍使用旧选择器的测试文件
cd web/frontend

# 搜索MainLayout引用
grep -r "MainLayout\|\.base-layout" tests/
# 搜索旧的菜单项
grep -r "Overview\|Watchlist\|Portfolio\|Activity" tests/
# 搜索旧的CSS选择器
grep -r "\.sidebar\|\.base-layout" tests/
```

**可能需要更新的测试文件清单**:
1. ⚠️ `tests/artdeco-integration-comprehensive.test.ts` - ArtDeco集成测试
2. ⚠️ `tests/comprehensive-e2e-validation.spec.ts` - 综合E2E验证
3. ⚠️ `tests/artdeco-dashboard.spec.ts` - ArtDeco仪表板测试
4. ⚠️ `tests/e2e/test-component-rendering.spec.ts` - 组件渲染测试

#### 行动方案

**步骤1: 识别需要更新的测试文件**

```bash
# 1.1 搜索所有使用旧选择器的测试
cd web/frontend
grep -r "MainLayout\|\.base-layout\|\.artdeco-sidebar" tests/ --include="*.ts" --include="*.js"

# 1.2 搜索旧的菜单项文本
grep -r "Overview.*Watchlist.*Portfolio" tests/

# 1.3 列出所有测试文件
find tests/ -name "*.spec.ts" -o -name "*.test.ts" | sort
```

**步骤2: 标准测试更新流程**

**2.1 CSS选择器更新映射**:
```typescript
// ❌ 旧选择器 (MainLayout)
const dashboard = page.locator('.base-layout');
const sidebar = page.locator('.sidebar');
const header = page.locator('.top-header');

// ✅ 新选择器 (ArtDecoLayout)
const dashboard = page.locator('.artdeco-dashboard');
const header = page.locator('.artdeco-header');
const sidebar = page.locator('.layout-sidebar');  // 注意: 不是 .artdeco-sidebar
```

**2.2 菜单项文本更新**:
```typescript
// ❌ 旧菜单 (4个英文菜单项)
const expectedMenus = [
  'Overview',
  'Watchlist',
  'Portfolio',
  'Activity'
];

// ✅ 新菜单 (7个中文顶层菜单)
const expectedMenus = [
  '仪表盘',      // Dashboard
  '市场行情',    // Market Data
  '股票管理',    // Stock Management
  '投资分析',    // Investment Analysis
  '风险管理',    // Risk Management
  '策略和交易管理', // Strategy & Trading
  '系统监控'     // System Monitoring
];
```

**2.3 路由更新**:
```typescript
// ❌ 旧路由 (hash路由)
await page.goto('/#/dashboard');
await page.goto('/#/dashboard/overview');

// ✅ 新路由 (仍使用hash，但路径简化)
await page.goto('/#/dashboard');
// 子路由根据ArtDeco结构更新
```

**2.4 标题验证更新**:
```typescript
// ❌ 旧标题
await expect(page).toHaveTitle(/Dashboard|MyStocks/);

// ✅ 新标题 (包含中文)
await expect(page).toHaveTitle(/MyStocks/);
// 或更精确的匹配:
await expect(page).toHaveTitle(/仪表盘.*MyStocks/);
```

**步骤3: 批量更新脚本（可选）**

创建批量更新脚本:
```bash
#!/bin/bash
# scripts/test-runner/batch-update-tests.sh

echo "开始批量更新E2E测试..."

# 替换CSS选择器
find tests/ -name "*.ts" -exec sed -i 's/\.base-layout/\.artdeco-dashboard/g' {} \;
find tests/ -name "*.ts" -exec sed -i 's/\.sidebar/\.layout-sidebar/g' {} \;

echo "✅ CSS选择器更新完成"
echo "⚠️  请手动检查并更新菜单项文本和其他业务逻辑"
```

**步骤4: 验证测试更新**

```bash
# 4.1 运行单个测试文件（调试模式）
npx playwright test tests/artdeco-integration-comprehensive.test.ts --debug

# 4.2 运行所有测试（仅显示通过/失败）
npx playwright test --reporter=list

# 4.3 生成测试报告
npx playwright test --reporter=html
# 报告位置: playwright-report/index.html
```

**步骤5: 视觉回归测试（可选但推荐）**

```typescript
// tests/visual/artdeco-visual.spec.ts
import { test, expect } from '@playwright/test';

test.describe('ArtDeco视觉回归测试', () => {
  test('仪表板页面快照', async ({ page }) => {
    await page.goto('/#/dashboard');
    await page.waitForLoadState('networkidle');

    // 截图对比
    await expect(page).toHaveScreenshot('dashboard.png', {
      maxDiffPixels: 100,  // 允许100像素差异
      animations: 'allowed'  // 允许动画差异
    });
  });

  test('菜单结构快照', async ({ page }) => {
    await page.goto('/#/dashboard');
    await page.waitForSelector('.nav-link');

    // DOM结构快照
    const sidebar = page.locator('.layout-sidebar');
    await expect(sidebar).toHaveScreenshot('sidebar.png', {
      maxDiffPixels: 50
    });
  });
});
```

运行视觉回归测试:
```bash
# 首次运行（生成基准快照）
npx playwright test tests/visual/artdeco-visual.spec.ts

# 更新快照
npx playwright test tests/visual/artdeco-visual.spec.ts --update-snapshots
```

#### 标准测试更新模板

创建测试更新模板文件:
```typescript
// tests/templates/artdeco-test-template.ts
/**
 * ArtDeco标准测试模板
 * 用于创建新的ArtDeco测试文件
 */

import { test, expect } from '@playwright/test';

test.describe('ArtDeco页面测试', () => {
  test.beforeEach(async ({ page }) => {
    // 每个测试前导航到仪表板
    await page.goto('/#/dashboard');
    await page.waitForLoadState('domcontentloaded');
  });

  test('应该显示ArtDeco布局', async ({ page }) => {
    // 验证主容器
    await expect(page.locator('.artdeco-dashboard')).toBeVisible();
    await expect(page.locator('.artdeco-header')).toBeVisible();

    // 验证侧边栏（使用 .layout-sidebar，不是 .artdeco-sidebar）
    await expect(page.locator('.layout-sidebar')).toBeVisible();
  });

  test('应该显示所有顶层菜单项', async ({ page }) => {
    const expectedMenus = [
      '仪表盘',
      '市场行情',
      '股票管理',
      '投资分析',
      '风险管理',
      '策略和交易管理',
      '系统监控'
    ];

    for (const menu of expectedMenus) {
      const element = page.locator(`.nav-link:has-text("${menu}")`);
      await expect(element).toBeVisible();
    }
  });

  test('页面标题应该正确', async ({ page }) => {
    await expect(page).toHaveTitle(/MyStocks/);
  });

  test('不应该有JavaScript错误', async ({ page }) => {
    const errors: string[] = [];

    page.on('pageerror', (error) => {
      errors.push(error.toString());
    });

    await page.waitForTimeout(2000);

    expect(errors.length).toBe(0);
  });
});
```

#### 预期成果
- ✅ 所有Playwright E2E测试与ArtDeco优先架构对齐
- ✅ 测试通过率稳定在95%以上（仅后端环境错误导致失败）
- ✅ 视觉回归测试确保ArtDecoUI一致性
- ✅ 测试套件提供可靠的自动化验证反馈
- ✅ 新测试可基于标准模板快速创建

### 3. 实现健壮的本地开发环境启动流程 - **中优先级** 🟡

#### 目标
提供一个简单、可靠的一键式脚本，方便开发者在本地启动完整的开发环境（前端和后端），降低新成员的上手成本。

#### 现有资源

**✅ 项目已有的脚本和配置**:
```bash
# PM2配置文件
web/frontend/ecosystem.config.js        # 前端PM2配置
web/backend/ecosystem.config.js          # 后端PM2配置
ecosystem.prod.config.js                  # 生产环境PM2配置

# 测试运行脚本
scripts/test-runner/start-environment.sh          # 环境启动脚本
scripts/test-runner/run-playwright-tests.sh       # Playwright测试脚本
scripts/test-runner/run-validation.sh             # 验证脚本

# 快速启动命令
run_platform.sh                            # 一键启动平台脚本
```

#### 行动方案

**方案A: 扩展现有脚本（推荐）**

基于现有的 `scripts/test-runner/start-environment.sh` 扩展:

```bash
#!/bin/bash
# scripts/dev/start-local-dev.sh
# MyStocks本地开发环境一键启动脚本

set -e  # 遇到错误立即退出

echo "🚀 MyStocks本地开发环境启动中..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 检查依赖
echo "📦 检查依赖..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js未安装${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 依赖检查通过${NC}"

# 2. 检查环境变量
echo "🔐 检查环境变量..."
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env文件不存在，从.example复制...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  请编辑.env文件配置数据库连接${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 环境变量配置存在${NC}"

# 3. 启动后端服务
echo "🔧 启动后端服务..."
cd web/backend

# 检查PM2是否运行
if ! pm2 list | grep -q "backend"; then
    echo "启动后端PM2服务..."
    pm2 start pm2_start.py --name mystocks-backend
else
    echo "后端服务已在运行，重启..."
    pm2 restart mystocks-backend
fi

# 等待后端服务就绪
echo "等待后端服务启动..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 后端服务就绪${NC}"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "等待后端服务... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}❌ 后端服务启动失败${NC}"
    pm2 logs mystocks-backend --lines 20
    exit 1
fi

cd ../..

# 4. 启动前端服务
echo "🎨 启动前端服务..."
cd web/frontend

# 检查PM2是否运行
if ! pm2 list | grep -q "mystocks-frontend-prod"; then
    echo "启动前端PM2服务..."
    pm2 start ecosystem.config.js --env production --only mystocks-frontend-prod
else
    echo "前端服务已在运行，重启..."
    pm2 restart mystocks-frontend-prod
fi

# 等待前端服务就绪
echo "等待前端服务启动..."
sleep 5

# 验证前端服务
if curl -s http://localhost:3001 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 前端服务就绪${NC}"
else
    echo -e "${RED}❌ 前端服务启动失败${NC}"
    pm2 logs mystocks-frontend-prod --lines 20
    exit 1
fi

cd ../..

# 5. 启动监控服务（可选）
if [ "$1" == "--with-monitoring" ]; then
    echo "📊 启动监控服务..."
    cd monitoring-stack
    docker-compose up -d
    cd ..
    echo -e "${GREEN}✅ 监控服务启动${NC}"
fi

# 6. 显示服务状态
echo ""
echo "═══════════════════════════════════════════════════"
echo -e "${GREEN}🎉 MyStocks开发环境启动成功！${NC}"
echo "═══════════════════════════════════════════════════"
echo ""
echo "📱 前端服务: http://localhost:3001"
echo "🔧 后端API:  http://localhost:8000"
echo "📚 API文档:  http://localhost:8000/docs"
echo ""
echo "📊 监控服务（如已启动）:"
echo "   Grafana:  http://localhost:3000 (admin/admin)"
echo "   Prometheus: http://localhost:9090"
echo ""
echo "🛠️  常用命令:"
echo "   查看日志: pm2 logs"
echo "   重启服务: pm2 restart all"
echo "   停止服务: pm2 stop all"
echo "   查看状态: pm2 list"
echo ""
echo "═══════════════════════════════════════════════════"
```

**使用方法**:
```bash
# 基础启动（仅前后端）
bash scripts/dev/start-local-dev.sh

# 完整启动（含监控）
bash scripts/dev/start-local-dev.sh --with-monitoring
```

**方案B: 开发模式启动（使用Vite dev server）**

如果需要热重载功能，创建开发模式脚本:

```bash
#!/bin/bash
# scripts/dev/start-dev-mode.sh
# MyStocks开发模式（前端热重载）

set -e

echo "🔥 MyStocks开发模式启动..."

# 1. 启动后端（PM2生产模式）
echo "启动后端服务..."
cd web/backend
pm2 restart mystocks-backend || pm2 start pm2_start.py --name mystocks-backend
cd ../..

# 2. 启动前端（Vite开发模式）
echo "启动前端开发模式（Vite HMR）..."
cd web/frontend

# 检查是否已有Vite进程
if lsof -Pi :3001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  端口3001已被占用，尝试停止现有进程...${NC}"
    # 询问用户是否继续
    read -p "是否停止现有进程并启动新的？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:3001 | xargs kill -9 2>/dev/null || true
    else
        echo "取消启动"
        exit 0
    fi
fi

# 启动Vite开发服务器
echo "启动Vite开发服务器（端口3001）..."
npm run dev -- --port 3001 &
VITE_PID=$!

# 等待Vite启动
echo "等待Vite服务启动..."
sleep 3

if curl -s http://localhost:3001 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Vite服务启动成功 (PID: $VITE_PID)${NC}"
else
    echo -e "${RED}❌ Vite服务启动失败${NC}"
    exit 1
fi

cd ../..

echo ""
echo "═══════════════════════════════════════════════════"
echo -e "${GREEN}🎉 开发模式启动成功！${NC}"
echo "═══════════════════════════════════════════════════"
echo ""
echo "📱 前端（HMR）: http://localhost:3001"
echo "🔧 后端API:    http://localhost:8000"
echo ""
echo "按Ctrl+C停止Vite开发服务器"
echo ""

# 捕获Ctrl+C信号
trap "echo '停止Vite服务...'; kill $VITE_PID 2>/dev/null; exit 0" INT

# 保持脚本运行
wait $VITE_PID
```

**方案C: 使用Docker Compose（团队协作）**

创建 `docker-compose.dev.yml`:

```yaml
version: '3.8'

services:
  # 后端服务
  backend:
    build:
      context: ./web/backend
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    volumes:
      - ./web/backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # 前端服务
  frontend:
    build:
      context: ./web/frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3001:3001"
    volumes:
      - ./web/frontend:/app
      - /app/node_modules
    command: npm run dev -- --host 0.0.0.0 --port 3001
    depends_on:
      - backend

  # PostgreSQL数据库（如果需要）
  postgres:
    image: postgres:17-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=mystocks
      - POSTGRES_USER=mystocks
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Redis（如果需要）
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

使用Docker Compose:
```bash
# 启动所有服务
docker-compose -f docker-compose.dev.yml up -d

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f

# 停止所有服务
docker-compose -f docker-compose.dev.yml down
```

#### 文档更新

**更新现有文档**（推荐，而非创建新文档）:

在 `docs/guides/B\351\241\279\347\233\276\346\216\245\345\205\245\346\214\47\345\215\227.md` 中添加"本地开发"部分:

```markdown
## 本地开发环境设置

### 快速启动

**方法1: 使用启动脚本（推荐）**
\`\`\`bash
# 生产模式启动（PM2）
bash scripts/dev/start-local-dev.sh

# 开发模式启动（Vite HMR）
bash scripts/dev/start-dev-mode.sh
\`\`\`

**方法2: 手动启动**
\`\`\`bash
# 后端
cd web/backend
pm2 start pm2_start.py --name mystocks-backend

# 前端（生产模式）
cd web/frontend
pm2 start ecosystem.config.js --env production

# 前端（开发模式）
npm run dev -- --port 3001
\`\`\`

**方法3: Docker Compose**
\`\`\`bash
docker-compose -f docker-compose.dev.yml up -d
\`\`\`

### 验证服务状态

\`\`\`bash
# 检查后端健康
curl http://localhost:8000/health

# 检查前端页面
curl http://localhost:3001

# 查看PM2状态
pm2 list
\`\`\`

### 常见问题

**问题1: 端口被占用**
\`\`\`bash
# 查找占用端口的进程
lsof -i :3001  # 前端
lsof -i :8000  # 后端

# 停止进程
kill -9 <PID>
\`\`\`

**问题2: 后端服务启动失败**
\`\`\`bash
# 查看后端日志
pm2 logs mystocks-backend --lines 50

# 检查环境变量
cat .env | grep DATABASE_URL
\`\`\`
```

#### 预期成果
- ✅ 开发者可以使用一个命令启动完整开发环境
- ✅ 新成员可以在5分钟内就绪开发环境
- ✅ 支持热重载（Vite HMR）提升开发效率
- ✅ 文档清晰，常见问题有明确解决方案
- ✅ 提供多种启动方式满足不同开发需求

### 4. 持续监控与调试 - **持续性任务** 🔵

#### 目标
确保Web端应用的长期稳定运行。

#### 现有监控资源

**项目已部署的LGTM监控栈**:
- ✅ **Prometheus**: 指标存储和查询 (http://localhost:9090)
- ✅ **Grafana**: 可视化仪表板 (http://localhost:3000)
- ✅ **Loki**: 日志聚合系统 (http://localhost:3100)
- ✅ **Tempo**: 分布式追踪系统 (http://localhost:3200)
- ✅ **Node Exporter**: 系统指标采集器

**配置文件位置**:
```
monitoring-stack/
├── docker-compose.yml              # 服务编排配置
├── .env.monitoring                 # 环境变量配置
├── config/
│   ├── prometheus.yml              # Prometheus配置
│   └── tempo-config.yaml           # Tempo配置
└── data/
    ├── prometheus/                 # Prometheus数据持久化
    ├── grafana/                    # Grafana数据持久化
    └── loki/                       # Loki数据持久化
```

#### 行动方案

**1. PM2日志监控**

```bash
# 1.1 实时查看所有日志
pm2 logs

# 1.2 查看特定服务日志
pm2 logs mystocks-frontend-prod
pm2 logs mystocks-backend

# 1.3 查看最近的错误日志
pm2 logs --err --lines 50 --nostream

# 1.4 清空旧日志
pm2 flush

# 1.5 导出日志到文件
pm2 logs --nostream > logs/pm2-$(date +%Y%m%d).log
```

**PM2日志级别监控**:
```bash
# 查看错误日志
pm2 logs --err

# 查看警告和错误
pm2 logs --err --warn

# 实时监控（tail模式）
pm2 logs --lines 0
```

**2. 浏览器开发者工具**

**Console标签（控制台）**:
```
功能: 查看JavaScript错误、警告、日志输出

检查项:
- ❌ 红色错误: 需要立即修复的JavaScript错误
- ⚠️  黄色警告: 可能导致问题的警告
- 🔵 蓝色信息: 一般日志信息

常见错误类型:
- ReferenceError: 变量未定义
- TypeError: 类型错误
- NetworkError: 网络请求失败
- CORS错误: 跨域请求被阻止
```

**Network标签（网络）**:
```
功能: 监控API请求、资源加载、WebSocket连接

检查项:
- 请求状态码: 200(成功), 404(未找到), 500(服务器错误)
- 请求时间: >3s的请求需要优化
- 失败的请求: 红色显示的请求
- CORS错误: "blocked by CORS policy"

筛选类型:
- XHR/Fetch: API请求
- WS: WebSocket连接
- Doc: 文档
- Script: JavaScript文件
- Stylesheet: CSS文件
```

**Performance标签（性能）**:
```
功能: 分析页面加载性能

关键指标:
- FCP (First Contentful Paint): 首次内容绘制 < 1.8s
- LCP (Largest Contentful Paint): 最大内容绘制 < 2.5s
- FID (First Input Delay): 首次输入延迟 < 100ms
- CLS (Cumulative Layout Shift): 累积布局偏移 < 0.1

诊断工具:
- Lighthouse: 综合性能分析
- Performance Profiler: JavaScript性能分析
- Memory Profiler: 内存使用分析
```

**3. 后端日志分析**

```bash
# 3.1 PM2后端日志
pm2 logs mystocks-backend --lines 100

# 3.2 如果后端使用systemd
journalctl -u mystocks-backend -f

# 3.3 Docker日志（如使用Docker）
docker logs mystocks-backend -f

# 3.4 日志分析命令
# 查找ERROR级别日志
pm2 logs mystocks-backend --nostream | grep ERROR

# 查找特定时间段的日志
pm2 logs mystocks-backend --nostream | grep "2026-01-20 10:"

# 统计错误类型
pm2 logs mystocks-backend --err --nostream | awk '{print $3}' | sort | uniq -c | sort -rn
```

**4. LGTM监控栈使用**

**Prometheus指标查询**:
```bash
# 访问Prometheus UI
open http://localhost:9090

# 常用查询
# 1. HTTP请求速率
rate(http_requests_total[5m])

# 2. 请求错误率
rate(http_requests_total{status=~"5.."}[5m])

# 3. 响应时间（P95）
histogram_quantile(0.95, http_request_duration_seconds)

# 4. PM2进程状态
pm2_process_up{instance="mystocks-frontend-prod"}
```

**Grafana仪表板**:
```bash
# 访问Grafana
open http://localhost:3000
# 默认用户名/密码: admin/admin

# 创建新的仪表板
1. 左侧菜单 → + → Dashboard
2. 添加面板
3. 选择数据源: Prometheus
4. 输入查询
5. 配置可视化（图表、仪表盘、表格等）
```

**推荐Grafana面板配置**:

**Web前端监控仪表板**:
```json
{
  "title": "MyStocks Frontend Monitoring",
  "panels": [
    {
      "title": "HTTP请求速率",
      "targets": [
        {
          "expr": "rate(http_requests_total{job=\"mystocks-frontend\"}[5m])"
        }
      ]
    },
    {
      "title": "响应时间P95",
      "targets": [
        {
          "expr": "histogram_quantile(0.95, http_request_duration_seconds)"
        }
      ]
    },
    {
      "title": "错误率",
      "targets": [
        {
          "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
        }
      ]
    }
  ]
}
```

**5. 日志聚合与分析（Loki）**

```bash
# 访问Loki
open http://localhost:3100

# LogQL查询示例
# 1. 查找所有错误日志
{job="mystocks-frontend"} |= "ERROR"

# 2. 查找特定时间段的日志
{job="mystocks-frontend"} |= "ERROR" |> "2026-01-20 10:"

# 3. 统计错误数量
count_over_time({job="mystocks-frontend"} |= "ERROR"[5m])

# 4. 查找WebSocket相关日志
{job="mystocks-frontend"} |= "WebSocket"
```

**6. 分布式追踪（Tempo）**

```bash
# 访问Tempo
open http://localhost:3200

# 查询追踪
# 1. 选择时间范围
# 2. 输入Trace ID（如果有）
# 3. 筛选标签: service="mystocks-frontend"
# 4. 查看调用链路和耗时
```

**7. 自动化监控脚本**

创建健康检查脚本:
```bash
#!/bin/bash
# scripts/dev/health-check.sh

echo "🔍 MyStocks服务健康检查..."

# 1. 检查前端服务
if curl -s http://localhost:3001 > /dev/null; then
    echo "✅ 前端服务正常"
else
    echo "❌ 前端服务异常"
    pm2 restart mystocks-frontend-prod
fi

# 2. 检查后端服务
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ 后端服务正常"
else
    echo "❌ 后端服务异常"
    pm2 restart mystocks-backend
fi

# 3. 检查PM2进程状态
pm2 list | grep -q "online.*mystocks-frontend-prod" || echo "❌ 前端PM2进程异常"
pm2 list | grep -q "online.*mystocks-backend" || echo "❌ 后端PM2进程异常"

# 4. 检查监控服务
if docker ps | grep -q "prometheus"; then
    echo "✅ Prometheus运行中"
else
    echo "⚠️  Prometheus未运行"
fi

if docker ps | grep -q "grafana"; then
    echo "✅ Grafana运行中"
else
    echo "⚠️  Grafana未运行"
fi

echo "健康检查完成"
```

**定期执行健康检查**:
```bash
# 添加到crontab（每小时执行一次）
crontab -e

# 添加以下行
0 * * * * /path/to/scripts/dev/health-check.sh >> /var/log/mystocks-health.log 2>&1
```

#### 预期成果
- ✅ 通过PM2日志持续监控前端服务状态
- ✅ 浏览器开发者工具实时捕获运行时错误
- ✅ 后端日志提供足够的诊断信息
- ✅ LGTM监控栈提供完整的可视化监控
- ✅ 自动化健康检查及时发现服务异常
- ✅ 问题和性能瓶颈可快速定位和解决

---

## 📚 相关文档

### 核心文档

**项目指南**:
- 📖 [项目接入指南](./B\351\241\279\347\233\276\346\216\245\345\205\245\346\214\47\345\215\227.md) - 项目快速接入指南
- 🔧 [TypeScript修复规范](../reports/TYPESCRIPT_FIX_BEST_PRACTICES.md) - TypeScript错误修复最佳实践
- 📋 [Web前端菜单结构重构](./ARTDECO_MENU_STRUCTURE_REFACTOR_PLAN.md) - ArtDeco菜单系统设计

**测试报告**:
- 📊 [路由统一完成报告](../reports/ROUTE_UNIFICATION_ARTDECO_REPORT.md) - ArtDecoLayout优先架构实施报告
- 🧪 [E2E测试最终报告](../reports/E2E_TEST_FINAL_REPORT.md) - 端到端测试完整报告
- 🎨 [ArtDeco集成测试计划](../reports/WEB_FRONTEND_ARTDECO_INTEGRATION_TEST_PLAN.md) - ArtDeco集成测试策略

**技术文档**:
- 🏗️ [系统架构总结](../api/ArtDeco_System_Architecture_Summary.md) - ArtDeco系统架构文档
- 🎨 [ArtDeco组件目录](../../web/frontend/ARTDECO_COMPONENTS_CATALOG.md) - 64个ArtDeco组件说明
- 📐 [ArtDeco设计展示V2](../api/ART_DECO_COMPONENT_SHOWCASE_V2.md) - ArtDeco设计系统展示

### 配置文件

**前端配置**:
- ⚙️ [PM2配置](../../web/frontend/ecosystem.config.js) - 前端PM2进程管理配置
- 🔨 [Vite配置](../../web/frontend/vite.config.ts) - 前端构建工具配置
- 📦 [NPM配置](../../web/frontend/package.json) - 前端依赖和脚本配置

**后端配置**:
- 🔧 [CORS配置](../../web/backend/app/core/config.py) - 后端跨域请求配置
- ⚙️ [主应用配置](../../web/backend/app/main.py) - FastAPI主应用配置
- 🔐 [环境变量示例](../../.env.example) - 环境变量配置模板

**监控配置**:
- 📊 [监控服务配置](../../monitoring-stack/docker-compose.yml) - LGTM监控栈配置
- 🎯 [Prometheus配置](../../monitoring-stack/config/prometheus.yml) - 指标采集配置
- ⏱️ [Tempo配置](../../monitoring-stack/config/tempo-config.yaml) - 追踪系统配置

### 外部资源

**Vue 3生态**:
- 📘 [Vue 3官方文档](https://vuejs.org/)
- 📘 [Vue Router文档](https://router.vuejs.org/)
- 📘 [Pinia文档](https://pinia.vuejs.org/)

**工具文档**:
- 📘 [Playwright文档](https://playwright.dev/)
- 📘 [PM2文档](https://pm2.keymetrics.io/)
- 📘 [Vite文档](https://vitejs.dev/)

**监控工具**:
- 📘 [Prometheus文档](https://prometheus.io/docs/)
- 📘 [Grafana文档](https://grafana.com/docs/)
- 📘 [Loki文档](https://grafana.com/docs/loki/latest/)

---

## 🎯 总结与行动计划

### 当前状态

✅ **已完成**:
- 路由结构统一到ArtDecoLayout优先架构
- 核心E2E测试已更新（测试通过率78%）
- Vite构建循环依赖问题已修复
- 应用成功渲染ArtDecoUI

⚠️ **待解决**:
- CORS/WebSocket连接错误（4个测试失败）
- 其他E2E测试文件可能需要更新
- 缺少标准化的开发环境启动流程

### 行动优先级

**🔴 P0 - 立即执行（本周内）**:
1. ✅ 使用快速检查清单诊断当前问题
2. 🔧 解决CORS配置问题（验证后端包含端口3001）
3. 🔧 解决WebSocket连接问题（验证或临时禁用）
4. ✅ 运行自动化检测脚本（Playwright网络错误检测）

**🟠 P1 - 高优先级（2周内）**:
1. 📝 更新所有E2E测试文件与ArtDeco架构对齐
2. 🧪 添加视觉回归测试确保UI一致性
3. 📚 创建标准测试更新模板

**🟡 P2 - 中优先级（1月内）**:
1. 🔨 实现一键启动脚本（基于现有脚本扩展）
2. 📖 更新项目接入指南（添加本地开发部分）
3. 🤖 考虑Docker Compose开发环境

**🔵 P3 - 持续性任务**:
1. 📊 定期检查PM2日志
2. 🔍 利用浏览器开发者工具调试
3. 📈 完善LGTM监控栈仪表板
4. 🤖 实施自动化健康检查

### 预期成果

**完成后**:
- ✅ Web端应用正常运行，无CORS/WebSocket错误
- ✅ 所有E2E测试通过率达到95%以上
- ✅ 开发者可在5分钟内启动本地开发环境
- ✅ 持续监控确保应用长期稳定运行
- ✅ 完整的文档和工具支持团队协作

---

## 🚀 快速开始

### 立即行动

如果您现在就想开始解决问题，请按以下顺序执行：

**步骤1: 快速诊断（5分钟）**
```bash
# 运行快速检查清单
bash -c 'curl -s http://localhost:3001 && echo "✅ 前端正常" || echo "❌ 前端异常"'
bash -c 'curl -s http://localhost:8000/health && echo "✅ 后端正常" || echo "❌ 后端异常"'
pm2 list
```

**步骤2: 验证CORS配置（2分钟）**
```bash
grep -A 10 "cors_origins_str" web/backend/app/core/config.py | grep "3001"
# 应该看到: http://localhost:3001
```

**步骤3: 检查WebSocket（3分钟）**
```bash
# 在浏览器控制台执行
new WebSocket('ws://localhost:8000/api/ws')
# 应该显示: WebSocket {url: "ws://localhost:8000/api/ws", readyState: 0/1}
```

**步骤4: 运行E2E测试（5分钟）**
```bash
cd web/frontend
npx playwright test tests/smoke/02-page-loading.spec.ts --reporter=list
```

**如果以上步骤都通过✅，恭喜！Web应用已正常运行！**

**如果仍有问题❌，请参考本文档的"已知问题和解决方案"部分。**

---

**文档维护**: 本文档应随着项目进展持续更新。每次解决问题后，请记录遇到的问题和解决方案，以供团队参考。

**反馈与改进**: 如果您发现本文档有任何不准确或需要改进的地方，请及时提出建议。
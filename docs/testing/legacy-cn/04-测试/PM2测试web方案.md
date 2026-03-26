我想再次测试web端，在PM2中运行web端，并使用playwright对web页面进行自动化测试，目的是确保开发的web页面功能可正常使用，你有什么好的建议？
你希望通过「PM2 稳定运行 web 端」+「Playwright 自动化测试」验证 MyStocks web 页面功能可用性，这是一套贴合生产环境的验证方案，既能保障 web 端持续稳定运行，又能通过自动化测试全面覆盖核心功能，避免人工测试的遗漏和低效。下面我将从环境准备、PM2 部署 web 端、Playwright 落地、测试用例设计、问题排查五个维度，给出可直接落地的完整建议，贴合 MyStocks 项目的实际场景。
一、 前置准备：保障测试环境一致性与项目完整性
在执行 PM2 部署和 Playwright 测试前，先完成前置检查，避免因环境问题或项目残留问题导致测试失效：
1. 项目层面：确保 web 端（前端）可正常构建、无残留问题
清理项目缓存与旧构建产物，避免历史残留干扰：
bash
运行
# 进入web前端项目目录（假设路径：web/frontend）
cd web/frontend

# 清理npm/yarn依赖缓存
npm cache clean --force

# 清理Vite构建缓存与旧产物（MyStocks是Vite项目）
rm -rf node_modules/.vite
rm -rf dist

# 重新安装依赖（确保依赖版本一致，无缺失）
npm install
本地先完成生产环境构建，验证构建无错误：
bash
运行
# 构建生产环境产物（Vite默认输出到dist目录）
npm run build

# 验证构建产物完整性（检查dist目录是否有index.html、assets文件夹）
ls -la dist
本地临时启动验证构建产物，确保页面无空白、核心功能可访问：
bash
运行
# 安装静态服务（推荐serve，轻量且贴合生产环境静态资源部署）
npm install -g serve

# 启动静态服务，访问构建产物
serve -s dist -p 3002

# 手动访问 http://localhost:3002，验证：
# 1. 页面无空白，核心DOM（导航栏、内容区域）正常显示
# 2. 无控制台报错（F12 Console）
# 3. 基础路由跳转正常（如Home→Dashboard）
2. 环境层面：确保 PM2 与 Playwright 环境就绪
验证 PM2 已安装且版本兼容（推荐 5.x 及以上版本）：
bash
运行
# 检查PM2版本
pm2 -v

# 未安装则执行安装
npm install -g pm2
提前安装 Playwright 依赖（避免后续测试时缺少浏览器驱动）：
bash
运行
# 进入web前端项目目录，安装Playwright作为项目开发依赖
cd web/frontend
npm install --save-dev playwright @playwright/test

# 安装Playwright所需的浏览器驱动（Chrome、Firefox、Safari）
npx playwright install --with-deps
确保端口不冲突（MyStocks web 端默认 3002）：
bash
运行
# 检查3002端口是否被占用
lsof -i:3002  # Mac/Linux
netstat -ano | findstr "3002"  # Windows

# 若被占用，终止对应进程（或修改PM2配置中的端口）
kill -9 <进程ID>  # Mac/Linux
二、 核心步骤 1：用 PM2 稳定运行 web 端（前端），贴合生产环境
MyStocks web 端是 Vite 构建的 Vue 项目，生产环境需部署静态构建产物（dist 目录），而非直接运行npm run dev（开发环境），PM2 配置需围绕静态服务展开，确保运行稳定、可监控、可自动重启。
1. 编写 PM2 配置文件（推荐，更易维护，优于命令行直接启动）
在 web 前端项目根目录（web/frontend）创建ecosystem.config.js，配置项贴合 MyStocks 场景：
javascript
运行
module.exports = {
  apps: [
    {
      // 1. 基础配置
      name: "mystocks-web", // 应用名称（PM2中显示，便于区分）
      script: "npx", // 启动脚本（使用npx调用serve）
      args: "serve -s dist -p 3002", // 传递给script的参数（启动静态服务，指定dist目录和端口3002）
      cwd: "./", // 执行目录（web前端项目根目录）
      env: {
        NODE_ENV: "production" // 生产环境变量
      },

      // 2. 稳定运行配置（保障高可用）
      instances: 1, // 实例数（前端静态服务无需多实例，1个足够）
      autorestart: true, // 应用崩溃时自动重启
      restart_delay: 3000, // 崩溃后延迟3秒重启（避免频繁重启）
      max_restarts: 10, // 1分钟内最大重启次数（防止无限重启）
      watch: false, // 关闭文件监听（前端静态产物已构建完成，无需监听）

      // 3. 日志配置（便于排查问题，关键！）
      log_date_format: "YYYY-MM-DD HH:mm:ss", // 日志时间格式
      out_file: "./logs/pm2-out.log", // 标准输出日志（访问日志等）
      error_file: "./logs/pm2-error.log", // 错误日志（崩溃、启动失败等）
      merge_logs: true, // 合并所有实例日志（单实例无影响，便于后续扩展）

      // 4. 资源限制配置（避免占用过多资源）
      max_memory_restart: "1G" // 内存占用超过1G时自动重启
    }
  ]
};
2. 初始化 PM2 日志目录，启动 web 端
bash
运行
# 进入web前端项目目录
cd web/frontend

# 创建日志目录（对应配置文件中的logs路径）
mkdir -p logs

# 用PM2启动web端（加载配置文件）
pm2 start ecosystem.config.js

# 验证启动状态（确保status为online）
pm2 status mystocks-web

# 可选：设置PM2开机自启（如需长期运行，避免服务器重启后应用停止）
pm2 startup
pm2 save
3. PM2 运行状态验证与日常操作
访问验证：打开浏览器访问http://localhost:3002，确保页面正常加载、无空白、核心功能可访问；
查看日志：若启动失败或页面异常，通过日志排查问题：
bash
运行
# 查看标准输出日志（实时更新）
pm2 logs mystocks-web --out

# 查看错误日志（实时更新）
pm2 logs mystocks-web --error

# 查看历史日志
cat ./logs/pm2-error.log
日常操作（后续测试中可能用到）：
bash
运行
# 重启web端（修改配置或重构后）
pm2 restart mystocks-web

# 停止web端
pm2 stop mystocks-web

# 删除web端应用（如需重新配置）
pm2 delete mystocks-web
三、 核心步骤 2：Playwright 自动化测试落地，覆盖 MyStocks 核心功能
Playwright 的核心价值是模拟真实用户操作，自动化验证页面功能可用性，针对 MyStocks 项目，需重点覆盖「页面加载、路由跳转、UI 交互、数据渲染、异常处理」五大场景，测试用例设计需贴合项目实际页面（Home、ArtDeco 市场数据分析中心、Dashboard 等）。
1. 初始化 Playwright 测试目录与配置
在 web 前端项目根目录，初始化 Playwright 测试结构（自动创建测试目录、配置文件）：
bash
运行
npx playwright init
优化 Playwright 配置文件（playwright.config.ts），贴合 MyStocks 测试场景：
typescript
运行
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  // 1. 测试用例目录（默认tests/，可自定义）
  testDir: './tests',

  // 2. 全局配置（保障测试稳定性）
  timeout: 30000, // 单个测试用例超时时间（30秒，适配数据加载场景）
  expect: {
    timeout: 5000 // 断言超时时间（5秒）
  },
  fullyParallel: true, // 并行执行测试用例（提升效率）
  forbidOnly: !!process.env.CI, // CI环境禁止单独运行用例
  retries: process.env.CI ? 2 : 0, // CI环境失败重试2次，本地不重试
  workers: process.env.CI ? 1 : undefined, // CI环境单进程，本地自动适配
  reporter: 'html', // 生成HTML测试报告（可视化展示结果，便于排查）

  // 3. 项目配置（核心：指向PM2运行的web端地址）
  use: {
    baseURL: 'http://localhost:3002', // 对应PM2启动的web端地址，避免硬编码
    actionTimeout: 10000, // 操作超时时间（10秒，如点击、输入）
    trace: 'on-first-retry', // 失败重试时记录追踪信息（便于排查）
    screenshot: 'only-on-failure', // 仅失败时截图（节省存储空间，关键！）
    video: 'retain-on-failure' // 仅失败时保留录屏（直观还原问题场景）
  },

  // 4. 浏览器配置（覆盖主流浏览器，确保兼容性）
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],

  // 5. 禁用内置web服务器（我们已用PM2运行web端，无需Playwright启动）
  webServer: undefined,
});
2. 设计核心测试用例（贴合 MyStocks，可直接落地）
在tests/目录下创建mystocks-web.spec.ts，编写覆盖核心功能的测试用例，重点验证「功能可用性」，避免过度细节化：
typescript
运行
import { test, expect } from '@playwright/test';

// 前置操作：每个测试用例执行前，访问首页并确保页面加载完成
test.beforeEach(async ({ page }) => {
  await page.goto('/'); // 基于配置中的baseURL，等价于访问http://localhost:3002
});

// 测试用例1：基础页面加载验证（核心，确保无空白、核心DOM可见）
test('首页正常加载，无空白，核心DOM元素可见', async ({ page }) => {
  // 验证页面标题（贴合MyStocks项目，可修改为实际页面标题）
  await expect(page).toHaveTitle(/MyStocks - 股票市场数据分析平台/);

  // 验证页面根容器#app存在且非空（避免页面空白）
  const appContainer = page.locator('#app');
  await expect(appContainer).toBeVisible();
  await expect(appContainer).not.toBeEmpty();

  // 验证核心导航元素可见（如首页、Dashboard、市场数据）
  await expect(page.locator('nav >> text=首页')).toBeVisible();
  await expect(page.locator('nav >> text=Dashboard总览')).toBeVisible();
  await expect(page.locator('nav >> text=ArtDeco市场数据分析中心')).toBeVisible();

  // 验证页面内容区域非空
  const contentArea = page.locator('.content');
  await expect(contentArea).toBeVisible();
  await expect(contentArea).not.toBeEmpty();
});

// 测试用例2：路由跳转正常（验证Vue路由功能可用）
test('路由跳转正常，可从首页跳转到Dashboard总览', async ({ page }) => {
  // 点击Dashboard导航链接，跳转到对应页面
  await page.click('nav >> text=Dashboard总览');

  // 验证跳转后URL正确（假设Dashboard路径为/dashboard）
  await expect(page).toHaveURL('/dashboard');

  // 验证Dashboard页面核心元素可见
  await expect(page.locator('h1 >> text=Dashboard总览')).toBeVisible();
  await expect(page.locator('.dashboard-statistics')).toBeVisible();
  await expect(page.locator('.market-trend-chart')).toBeVisible();
});

// 测试用例3：核心UI交互 - 股票代码查询输入框可用（贴合业务功能）
test('股票代码查询输入框可输入、提交按钮可点击', async ({ page }) => {
  // 跳转到市场数据页面（假设路径为/market）
  await page.click('nav >> text=ArtDeco市场数据分析中心');
  await expect(page).toHaveURL('/market');

  // 定位输入框和提交按钮
  const stockCodeInput = page.locator('input[name="stockCode"]');
  const queryButton = page.locator('button >> text=查询行情');

  // 验证输入框可输入
  await stockCodeInput.fill('600519');
  await expect(stockCodeInput).toHaveValue('600519');

  // 验证提交按钮可点击
  await expect(queryButton).toBeVisible();
  await expect(queryButton).toBeEnabled();

  // 模拟点击提交按钮（无需等待实际数据返回，仅验证交互可用）
  await queryButton.click();
});

// 测试用例4：验证后端API数据渲染（核心，确保前后端联动正常）
test('市场行情数据列表正常渲染，非空', async ({ page }) => {
  // 跳转到市场行情页面
  await page.click('nav >> text=ArtDeco市场行情中心');
  await expect(page).toHaveURL('/market/quote');

  // 等待数据列表加载（适配API请求延迟，最长等待10秒）
  const stockQuoteList = page.locator('.stock-quote-list');
  await expect(stockQuoteList).toBeVisible({ timeout: 10000 });
  await expect(stockQuoteList).not.toBeEmpty();

  // 验证列表中至少有1条数据（确保API数据正常返回并渲染）
  const stockItems = stockQuoteList.locator('.stock-item');
  await expect(stockItems).toHaveCountGreaterThan(0);
});

// 测试用例5：异常场景处理 - 访问不存在的路由，返回404页面（验证前端异常处理）
test('访问不存在的路由，显示404页面', async ({ page }) => {
  // 访问不存在的路由
  await page.goto('/non-existent-route');

  // 验证404页面核心元素可见
  await expect(page.locator('h1 >> text=404 - 页面不存在')).toBeVisible();
  await expect(page.locator('a >> text=返回首页')).toBeVisible();

  // 验证返回首页链接可点击
  await page.click('a >> text=返回首页');
  await expect(page).toHaveURL('/');
});
3. 关键测试技巧（贴合 MyStocks 项目，避免踩坑）
元素定位优先使用「文本」或「name 属性」：避免使用 XPath 或 CSS 选择器（如.el-button--primary），防止 UI 组件样式变化导致用例失效；
适配数据加载延迟：MyStocks 涉及后端 API 请求（行情数据、市场列表），需使用timeout参数或waitForResponse等待数据返回：
typescript
运行
// 等待特定API请求完成（如市场列表API）
await page.waitForResponse(response => 
  response.url().includes('/api/v1/market/list') && response.ok()
);
避免硬编码：页面标题、路由路径、API 路径可抽离为常量，便于后续维护：
typescript
运行
// 抽离常量
const CONSTANTS = {
  BASE_TITLE: 'MyStocks - 股票市场数据分析平台',
  ROUTES: {
    HOME: '/',
    DASHBOARD: '/dashboard',
    MARKET: '/market'
  },
  APIS: {
    MARKET_LIST: '/api/v1/market/list'
  }
};

// 测试用例中使用常量
await expect(page).toHaveTitle(CONSTANTS.BASE_TITLE);
四、 执行 Playwright 测试，查看结果与排查问题
1. 执行测试用例
bash
运行
# 进入web前端项目目录
cd web/frontend

# 运行所有测试用例（默认并行执行，生成HTML报告）
npx playwright test

# 可选：仅运行指定测试文件（如mystocks-web.spec.ts）
npx playwright test tests/mystocks-web.spec.ts

# 可选：调试模式运行（显示浏览器窗口，便于观察操作过程）
npx playwright test --headed

# 可选：仅运行单个测试用例（通过测试名称筛选）
npx playwright test -g "首页正常加载，无空白，核心DOM元素可见"
2. 查看测试报告
Playwright 会自动生成 HTML 格式的测试报告，位于playwright-report/目录，可通过浏览器打开查看详细结果：
bash
运行
# 打开HTML测试报告
npx playwright show-report
报告中会展示：
测试用例通过率、执行时间；
失败用例的截图、录屏、追踪信息；
每个用例的详细执行步骤，便于定位问题。
3. 常见问题排查（贴合 MyStocks 项目）
测试用例失败：「元素不可见」或「页面空白」：
排查步骤 1：查看 PM2 日志，确认 web 端是否正常运行，无崩溃；
排查步骤 2：手动访问http://localhost:3002 (注意可用端口)，确认页面是否正常加载，无控制台报错；
排查步骤 3：查看 Playwright 失败截图，确认是否为数据加载延迟导致，可增加超时时间。
测试用例失败：「API 请求 404」或「数据渲染为空」：
排查步骤 1：确认后端服务（FastAPI）是否正常运行，PM2 状态是否为 online；
排查步骤 2：查看后端 API 日志，确认是否返回正常数据（200 OK）；
排查步骤 3：在 Playwright 用例中添加waitForResponse，等待 API 请求完成。
浏览器启动失败：
排查步骤 1：重新安装 Playwright 浏览器驱动（npx playwright install --with-deps）；
排查步骤 2：确保无防火墙或安全软件阻止浏览器启动。
五、 后续优化：提升测试体系的可维护性与自动化程度
数据驱动测试：将股票代码、页面标题等测试数据抽离到 JSON 文件，实现 “一份数据，多份用例”，便于维护：
json
// tests/test-data.json
{
  "stockCodes": ["600519", "000001", "300750"],
  "pageTitles": {
    "home": "MyStocks - 股票市场数据分析平台",
    "dashboard": "Dashboard总览 - MyStocks"
  }
}
集成 CI/CD：将 PM2 部署与 Playwright 测试集成到 CI/CD 流程（如 GitHub Actions、GitLab CI），实现 “每次代码提交后自动构建、部署、测试”，提前发现问题；
定期运行测试：配置定时任务（如 crontab），每天定时运行 Playwright 测试，确保生产环境 web 端功能长期可用；
扩展测试覆盖范围：后续逐步覆盖更多场景（如用户登录、数据导出、图表交互），实现全功能自动化验证。
总结
本次验证的核心流程是「PM2 保障 web 端稳定运行（生产环境） + Playwright 模拟真实用户操作（自动化验证）」，关键要点如下：
PM2 部署需围绕生产环境静态构建产物，配置日志和自动重启，确保 web 端高可用；
Playwright 测试用例需覆盖核心功能场景（加载、跳转、交互、数据渲染），贴合 MyStocks 业务；
利用 Playwright 的截图、录屏、HTML 报告，快速排查测试失败问题；
后续通过数据驱动、CI/CD 集成，提升测试体系的可维护性与自动化程度。
按照这套方案执行，既能确保 MyStocks web 页面功能正常可用，又能建立一套长期可用的自动化验证体系，为后续项目迭代提供坚实保障！ 🚀

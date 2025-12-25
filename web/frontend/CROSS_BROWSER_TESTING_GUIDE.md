# 跨浏览器测试指南

## 概述

本文档提供 MyStocks 项目在多种桌面浏览器上进行端到端测试的指南。

**测试范围**: 仅限桌面端浏览器（不包括移动端和平板）

**支持浏览器**:
- ✅ Chromium/Chrome (已测试)
- ⏳ Firefox (待测试)
- ⏳ Safari (待测试)
- ⏳ Edge (待测试)

---

## 已测试浏览器

### Chromium/Chrome ✅

**版本**: Chromium (已安装)

**测试状态**: ✅ 通过

**测试命令**:
```bash
cd /opt/claude/mystocks_spec/web/frontend

# 使用 Playwright (默认使用 Chromium)
npx playwright test

# 指定使用 Chromium
npx playwright test --project=chromium

# 运行特定测试文件
npx playwright test tests/e2e/market-data.spec.ts
npx playwright test tests/e2e/strategy-management.spec.ts
```

**测试结果**:
- 市场数据模块: ✅ 通过
- 策略管理模块: ✅ 通过
- 桌面布局验证: ✅ 通过 (1920x1080, 1680x1050, 1440x900, 1366x768)

---

## 待测试浏览器

### Firefox

#### 安装 Firefox

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install firefox
```

**Linux (CentOS/RHEL)**:
```bash
sudo yum install firefox
```

**macOS**:
```bash
brew install --cask firefox
```

**Windows**:
从 https://www.mozilla.org/firefox/ 下载并安装

#### 安装 Playwright Firefox 浏览器

```bash
cd /opt/claude/mystocks_spec/web/frontend

# 安装 Playwright Firefox
npx playwright install firefox
```

#### 运行 Firefox 测试

```bash
# 运行所有 Firefox 测试
npx playwright test --project=firefox

# 运行特定测试
npx playwright test tests/e2e/market-data.spec.ts --project=firefox
npx playwright test tests/e2e/strategy-management.spec.ts --project=firefox
```

#### 预期测试时间

- 安装: ~5 分钟
- 运行测试: ~10-15 分钟

---

### Safari

#### 系统要求

**Safari 仅在 macOS 上可用**，无法在 Linux 或 Windows 上测试。

#### 安装 Safari 驱动

```bash
# 在 macOS 上
cd /opt/claude/mystocks_spec/web/frontend

# 安装 Playwright Safari
npx playwright install webkit

# 注意: Safari 需要 macOS 12 或更高版本
```

#### 启用 Safari 自动化

1. 打开 Safari
2. 菜单栏 → Safari → 偏好设置 → 高级
3. 勾选 "在菜单栏中显示开发菜单"
4. 开发者 → 允许远程自动化

#### 运行 Safari 测试

```bash
# 使用 WebKit (Safari 引擎)
npx playwright test --project=webkit

# 运行特定测试
npx playwright test tests/e2e/market-data.spec.ts --project=webkit
```

#### 预期测试时间

- 安装: ~3 分钟 (macOS)
- 运行测试: ~10-15 分钟

---

### Microsoft Edge

#### 安装 Edge

**Linux (Ubuntu/Debian)**:
```bash
# 下载 Microsoft Edge GPG key
curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg

# 安装
sudo install -o root -g root -m 644 microsoft.gpg /etc/apt/trusted.gpg.d/

# 添加 Edge 仓库
sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/edge stable main" > /etc/apt/sources.list.d/microsoft-edge.list'

sudo apt-get update
sudo apt-get install microsoft-edge-stable
```

**Windows**:
预装在 Windows 10/11 上

**macOS**:
```bash
brew install --cask edge
```

#### 安装 Playwright Edge 驱动

Edge 基于 Chromium，可以使用 Playwright 的 Chromium 通道：

```bash
cd /opt/claude/mystocks_spec/web/frontend

# Edge 已在 Playwright 中支持
npx playwright install msedge
```

#### 运行 Edge 测试

```bash
# 使用 Edge 通道
npx playwright test --project=msedge

# 运行特定测试
npx playwright test tests/e2e/market-data.spec.ts --project=msedge
```

#### 预期测试时间

- 安装: ~10 分钟
- 运行测试: ~10-15 分钟

---

## Playwright 配置

### playwright.config.ts

确保 `playwright.config.ts` 包含所有浏览器项目：

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',

  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3001',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

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
    {
      name: 'msedge',
      use: {
        ...devices['Desktop Edge'],
        channel: 'msedge',
      },
    },
  ],

  // Start local development server before running tests
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3001',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
```

---

## 测试场景清单

### 桌面端布局验证 (所有浏览器)

- [ ] Full HD (1920x1080)
- [ ] Widescreen (1680x1050)
- [ ] Laptop (1440x900)
- [ ] Small Laptop (1366x768)

### 市场数据模块测试

- [ ] 页面加载成功
- [ ] 显示市场统计数据
- [ ] 显示热门 ETF 列表
- [ ] 显示筹码比拼数据
- [ ] 显示龙虎榜数据
- [ ] API 失败时自动降级到 Mock 数据
- [ ] 刷新按钮功能正常
- [ ] 缓存机制工作正常

### 策略管理模块测试

- [ ] 页面加载成功
- [ ] 显示策略卡片列表
- [ ] 显示策略详情
- [ ] 创建策略对话框打开正常
- [ ] 表单验证正常
- [ ] 回测面板功能正常
- [ ] 策略操作（启动/停止/暂停）正常
- [ ] 错误处理正常

---

## 测试命令参考

### 运行所有浏览器测试

```bash
# 并行运行所有浏览器测试
npx playwright test

# 顺序运行所有浏览器测试
npx playwright test --workers=1
```

### 运行特定浏览器

```bash
# 仅 Chromium
npx playwright test --project=chromium

# 仅 Firefox
npx playwright test --project=firefox

# 仅 Safari (WebKit)
npx playwright test --project=webkit

# 仅 Edge
npx playwright test --project=msedge
```

### 运行特定测试文件

```bash
# 市场数据模块
npx playwright test tests/e2e/market-data.spec.ts

# 策略管理模块
npx playwright test tests/e2e/strategy-management.spec.ts
```

### 生成测试报告

```bash
# 生成 HTML 报告
npx playwright test --reporter=html

# 查看报告
npx playwright show-report
```

### 调试模式

```bash
# 调试模式 (打开浏览器窗口)
npx playwright test --debug

# UI 模式 (交互式测试)
npx playwright test --ui
```

---

## 常见问题排查

### Firefox 测试失败

**问题**: `BrowserType.launch: Executable doesn't exist`

**解决方案**:
```bash
# 确保 Firefox 已安装
firefox --version

# 重新安装 Playwright Firefox
npx playwright install firefox --force
```

### Safari 测试失败

**问题**: `Cannot connect to WebKit`

**解决方案**:
1. 确保在 macOS 上运行
2. 启用 Safari 远程自动化
3. 安装 Xcode 命令行工具: `xcode-select --install`

### Edge 测试失败

**问题**: `Edge not found`

**解决方案**:
```bash
# 检查 Edge 是否安装
microsoft-edge --version

# 如果未安装，按照上面的安装指南安装
```

---

## CI/CD 集成

### GitHub Actions 配置

创建 `.github/workflows/cross-browser-tests.yml`:

```yaml
name: Cross Browser Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest]
        browser: [chromium, firefox]
        include:
          - os: macos-latest
            browser: webkit
          - os: windows-latest
            browser: msedge

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright Browsers
        run: npx playwright install --with-deps ${{ matrix.browser }}

      - name: Run Playwright tests
        run: npx playwright test --project=${{ matrix.browser }}

      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report-${{ matrix.browser }}
          path: playwright-report/
          retention-days: 7
```

---

## 测试结果记录

### 当前测试状态 (2025-12-25)

| 浏览器 | 状态 | 测试日期 | 备注 |
|--------|------|----------|------|
| Chromium | ✅ 通过 | 2025-12-25 | 市场数据 + 策略管理模块 |
| Firefox | ⏳ 待测试 | - | 需要安装 Firefox |
| Safari | ⏳ 待测试 | - | 需要 macOS 环境 |
| Edge | ⏳ 待测试 | - | 需要安装 Edge |

### 测试覆盖率目标

- **浏览器覆盖率**: 100% (所有主流桌面浏览器)
- **分辨率覆盖率**: 100% (4种常见桌面分辨率)
- **功能覆盖率**: >90% (所有核心功能)

---

## 下一步行动

1. **短期 (1周内)**
   - ✅ 完成 Chromium 测试（已完成）
   - ⏳ 在 Firefox 上运行测试
   - ⏳ 在 Edge 上运行测试

2. **中期 (2-4周)**
   - 在 macOS 上运行 Safari 测试
   - 配置 GitHub Actions 自动化跨浏览器测试
   - 修复发现的跨浏览器兼容性问题

3. **长期**
   - 每次发布前进行完整的跨浏览器测试
   - 维护跨浏览器测试脚本
   - 优化测试执行时间

---

## 参考资料

- [Playwright 官方文档](https://playwright.dev/)
- [Playwright 浏览器支持](https://playwright.dev/docs/browsers)
- [跨浏览器测试最佳实践](https://playwright.dev/docs/best-practices)

---

**文档版本**: 1.0
**最后更新**: 2025-12-25
**维护者**: Claude Code (Sonnet 4.5)

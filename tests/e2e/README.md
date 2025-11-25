# MyStocks Web 端自动化测试指南

本文档详细介绍如何使用 Playwright 对 MyStocks Web 端进行自动化测试。

## 目录结构

```
tests/e2e/
├── login.spec.js          # 登录功能测试
├── README.md              # 本文档
```

## 前置条件

### 1. 安装依赖

```bash
# 在项目根目录运行
npm install @playwright/test --save-dev

# 或使用 pnpm
pnpm add -D @playwright/test
```

### 2. 启动服务

#### 启动后端服务

```bash
cd web/backend
python run_server.py
# 或
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

服务将运行在 `http://localhost:8000`

#### 启动前端开发服务

```bash
cd web/frontend
npm run dev
# 或
npm install  # 如果还没有安装依赖
npm run dev
```

服务将运行在 `http://localhost:3000`

## 测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 普通用户 | user | user123 |

## 运行测试

### 1. 运行所有测试

```bash
cd /opt/claude/mystocks_spec

# 使用标准 Playwright 配置
npx playwright test tests/e2e/login.spec.js

# 或使用专门的 Web 配置
npx playwright test --config=playwright.config.web.ts tests/e2e/login.spec.js
```

### 2. 运行特定浏览器的测试

```bash
# 仅在 Chrome 中运行
npx playwright test --project=chromium tests/e2e/login.spec.js

# 仅在 Firefox 中运行
npx playwright test --project=firefox tests/e2e/login.spec.js

# 仅在 Safari 中运行
npx playwright test --project=webkit tests/e2e/login.spec.js
```

### 3. 运行特定测试用例

```bash
# 运行包含 "登录成功" 的测试
npx playwright test -g "登录成功" tests/e2e/login.spec.js

# 运行第 2 个测试用例（管理员账号登录成功）
npx playwright test --project=chromium --grep "2. 管理员账号登录成功"
```

### 4. 调试模式运行

```bash
# 使用 Playwright Inspector 进行调试
npx playwright test --debug tests/e2e/login.spec.js

# 打开 Playwright Test for VSCode 扩展（推荐）
# 在 VSCode 中按 Ctrl+Shift+P，搜索 "Playwright: Run tests"
```

### 5. 查看测试报告

```bash
# 运行测试后，打开 HTML 报告
npx playwright show-report playwright-report

# 或直接打开报告文件
open playwright-report/index.html
```

### 6. 使用 UI 模式运行测试

```bash
# 使用交互式 UI 界面
npx playwright test --ui tests/e2e/login.spec.js
```

### 7. 生成测试报告

```bash
# 运行测试后会自动生成报告
npx playwright test tests/e2e/login.spec.js

# 查看报告
npx playwright show-report
```

## 测试内容

### login.spec.js 包含以下测试用例

#### 登录功能测试（8 个用例）

1. **登录页面加载** - 验证页面元素正确加载
2. **管理员登录成功** - 使用 admin 账号登录
3. **普通用户登录成功** - 使用 user 账号登录
4. **空用户名验证** - 验证用户名不能为空
5. **空密码验证** - 验证密码不能为空
6. **错误密码处理** - 验证错误密码的错误提示
7. **Enter 键提交** - 验证可以用 Enter 键提交表单
8. **加载状态显示** - 验证登录按钮显示加载状态

#### 登出功能测试（1 个用例）

9. **登出后清除数据** - 验证登出后清除存储数据并返回登录页面

#### 页面导航测试（3 个用例）

10. **显示仪表板** - 验证登录后显示仪表板
11. **页面刷新保持登录** - 验证刷新页面后仍保持登录状态

## 环境变量配置

### 本地开发

```bash
# .env.test (创建在 web/frontend 目录)
BASE_URL=http://localhost:3000
API_URL=http://localhost:8000
```

### CI/CD 环境

```bash
# 在 GitHub Actions 中设置
env:
  BASE_URL: http://localhost:3000
  CI: true
```

## 常见问题排查

### 1. 测试超时

**问题**: 测试超时 (Timeout)

**解决方案**:
- 确保前后端服务已启动
- 增加超时时间：修改 `playwright.config.web.ts` 中的 `timeout` 和 `expect.timeout`
- 检查网络连接是否正常

```typescript
// 修改超时时间
timeout: 120 * 1000,  // 改为 120 秒
expect: {
  timeout: 20 * 1000, // 改为 20 秒
},
```

### 2. 登录失败

**问题**: 登录时出现 401 或 403 错误

**解决方案**:
- 检查后端是否正在运行
- 验证测试账号是否正确（admin/admin123）
- 查看后端日志是否有错误信息
- 检查 CORS 配置是否正确

```bash
# 测试后端连接
curl http://localhost:8000/api/auth/login \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 3. 元素找不到

**问题**: 找不到期望的 DOM 元素

**解决方案**:
- 增加等待时间：`await page.waitForLoadState('networkidle')`
- 检查选择器是否正确（使用浏览器开发者工具验证）
- 使用 `--debug` 模式查看实际页面

```typescript
// 添加调试代码
await page.screenshot({ path: 'debug.png' });
console.log(await page.content()); // 打印 HTML
```

### 4. 视频/截图保存失败

**问题**: 报告中没有保存视频或截图

**解决方案**:
- 检查 `playwright-report` 目录是否存在
- 确保目录有写权限
- 在配置中启用视频/截图：

```typescript
use: {
  video: 'retain-on-failure',
  screenshot: 'only-on-failure',
}
```

## 集成 CI/CD

### GitHub Actions 示例

创建文件 `.github/workflows/e2e-tests.yml`:

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install backend dependencies
        run: |
          cd web/backend
          pip install -r requirements.txt

      - name: Install frontend dependencies
        run: |
          cd web/frontend
          npm install

      - name: Install Playwright browsers
        run: npx playwright install --with-deps

      - name: Run E2E tests
        run: |
          npx playwright test --config=playwright.config.web.ts tests/e2e/login.spec.js

      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 30
```

## 扩展测试

### 添加新的测试用例

1. 在 `login.spec.js` 中添加新测试：

```javascript
test('12. 新的测试用例', async ({ page }) => {
  // 测试代码
  await page.goto(`${BASE_URL}/login`);
  // ...
});
```

2. 运行测试验证：

```bash
npx playwright test -g "新的测试用例" tests/e2e/login.spec.js
```

### 创建页面对象模型（POM）

为了更好的代码组织，可以创建 POM：

```javascript
// tests/e2e/pages/LoginPage.js
export class LoginPage {
  constructor(page) {
    this.page = page;
    this.usernameInput = page.getByLabel(/用户名/);
    this.passwordInput = page.getByLabel(/密码/);
    this.loginButton = page.getByRole('button', { name: /登录/ });
  }

  async goto() {
    await this.page.goto('http://localhost:3000/login');
  }

  async login(username, password) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }
}
```

然后在测试中使用：

```javascript
import { LoginPage } from './pages/LoginPage';

test('使用 POM 的登录测试', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('admin', 'admin123');
});
```

## 更多信息

- [Playwright 官方文档](https://playwright.dev/)
- [Playwright API 参考](https://playwright.dev/docs/api/class-playwright)
- [Playwright 最佳实践](https://playwright.dev/docs/best-practices)

## 支持

如遇到问题，请：

1. 检查后端和前端是否正常运行
2. 查看测试日志和报告
3. 使用 `--debug` 模式进行调试
4. 查看浏览器控制台输出
5. 检查服务器日志

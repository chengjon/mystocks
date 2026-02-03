# MyStocks Web 端自动化测试 - 快速开始指南

## 概览

本项目使用 **Playwright** 进行自动化测试，包括登录流程、页面导航、表单验证等功能测试。

### 🎯 目标

- ✅ 自动化测试登录功能（成功、失败、验证）
- ✅ 测试页面导航和状态保持
- ✅ 验证表单输入和错误提示
- ✅ 支持多浏览器运行（Chrome、Firefox、Safari）
- ✅ 生成详细的测试报告

### 📁 文件结构

```
tests/
├── e2e/
│   ├── login.spec.js        # 登录相关的自动化测试（11 个测试用例）
│   └── README.md             # 详细文档
playwright.config.web.ts      # Playwright 配置
scripts/tests/
└── run-playwright-tests.sh    # 测试启动脚本
```

## 快速开始（5分钟）

### 1️⃣ 安装依赖

```bash
cd /opt/claude/mystocks_spec

# 安装 Playwright
npm install @playwright/test --save-dev

# 或如果项目已有 package.json
npm install
```

### 2️⃣ 启动服务（两个终端）

**终端 1 - 启动后端：**
```bash
cd /opt/claude/mystocks_spec/web/backend
python run_server.py
```

等待看到类似信息：
```
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**终端 2 - 启动前端：**
```bash
cd /opt/claude/mystocks_spec/web/frontend
npm run dev
```

等待看到类似信息：
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:3000/
```

### 3️⃣ 运行测试

**简单运行（推荐新手）：**
```bash
cd /opt/claude/mystocks_spec
npx playwright test tests/e2e/login.spec.js
```

**或使用启动脚本：**
```bash
chmod +x scripts/tests/run-playwright-tests.sh
./scripts/tests/run-playwright-tests.sh
```

### 4️⃣ 查看结果

```bash
# 打开 HTML 报告
npx playwright show-report playwright-report
```

## 常见用法

### 调试模式（推荐开发使用）

逐步执行测试，可以随时暂停和检查状态：

```bash
npx playwright test --debug tests/e2e/login.spec.js
```

### UI 模式（最佳体验）

交互式界面，实时查看测试执行：

```bash
./scripts/tests/run-playwright-tests.sh --ui
```

或直接使用 npm：
```bash
npx playwright test --ui --config=playwright.config.web.ts tests/e2e/login.spec.js
```

### 显示浏览器窗口

查看浏览器窗口进行测试（默认无头运行）：

```bash
./scripts/tests/run-playwright-tests.sh --headed
```

### 仅在特定浏览器运行

```bash
# Chrome
./scripts/tests/run-playwright-tests.sh --chrome

# Firefox
./scripts/tests/run-playwright-tests.sh --firefox

# Safari
./scripts/tests/run-playwright-tests.sh --webkit
```

## 测试账号

| 用户类型 | 用户名 | 密码 |
|---------|--------|------|
| 管理员 | admin | admin123 |
| 普通用户 | user | user123 |

## 使用启动脚本

```bash
chmod +x scripts/tests/run-playwright-tests.sh

# 查看帮助
./scripts/tests/run-playwright-tests.sh --help

# 运行所有测试
./scripts/tests/run-playwright-tests.sh

# UI 模式
./scripts/tests/run-playwright-tests.sh --ui

# 调试模式
./scripts/tests/run-playwright-tests.sh --debug

# 显示浏览器
./scripts/tests/run-playwright-tests.sh --headed

# 仅在 Chrome 运行
./scripts/tests/run-playwright-tests.sh --chrome

# 查看报告
./scripts/tests/run-playwright-tests.sh --report
```

## 测试内容概览

### 登录页面测试（login.spec.js）

总共 **11 个测试用例**：

#### 页面加载测试
- ✅ 登录页面正确加载

#### 成功登录测试
- ✅ 管理员账号登录成功
- ✅ 普通用户账号登录成功

#### 表单验证测试
- ✅ 空用户名显示错误
- ✅ 空密码显示错误
- ✅ 错误密码显示错误提示

#### 交互测试
- ✅ 使用 Enter 键提交表单
- ✅ 登录按钮显示加载状态

#### 登出测试
- ✅ 登出后清除存储数据

#### 页面导航测试
- ✅ 登录后显示仪表板
- ✅ 刷新页面后保持登录状态

## 测试报告

运行测试后，会自动生成：

- **HTML 报告**: `playwright-report/index.html` - 友好的图形界面
- **JSON 报告**: `test-results/results.json` - 机器可读的详细数据
- **JUnit 报告**: `test-results/junit.xml` - CI/CD 集成格式

```bash
# 打开 HTML 报告
npx playwright show-report playwright-report
```

## 常见问题排查

### Q: 测试超时怎么办？

A: 确保前后端都已启动，检查端口是否占用：

```bash
# 检查端口
lsof -i :3000   # 前端
lsof -i :8000   # 后端

# 如果被占用，杀死进程
kill -9 <PID>
```

### Q: 登录失败

A: 检查后端是否运行，尝试手动登录：

```bash
# 测试后端
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Q: 找不到元素

A: 使用调试模式查看实际 DOM：

```bash
npx playwright test --debug tests/e2e/login.spec.js
```

## 下一步

### 添加更多测试

编辑 `tests/e2e/login.spec.js`，添加新的测试用例：

```javascript
test('你的新测试', async ({ page }) => {
  // 测试代码
});
```

### 创建页面对象模型

组织代码更清晰（参考 `tests/e2e/README.md`）

### 集成 CI/CD

在 GitHub Actions 或其他 CI 平台运行自动测试

## 更多资源

- 📖 [详细文档](tests/e2e/README.md)
- 🔗 [Playwright 官方文档](https://playwright.dev/)
- 💡 [最佳实践](https://playwright.dev/docs/best-practices)

## 快速命令参考

```bash
# 安装依赖
npm install @playwright/test --save-dev

# 安装浏览器驱动
npx playwright install

# 运行所有测试
npx playwright test tests/e2e/login.spec.js

# 调试模式
npx playwright test --debug tests/e2e/login.spec.js

# UI 模式
npx playwright test --ui tests/e2e/login.spec.js

# 显示浏览器
npx playwright test --headed tests/e2e/login.spec.js

# 仅在 Chrome 运行
npx playwright test --project=chromium tests/e2e/login.spec.js

# 查看报告
npx playwright show-report playwright-report

# 特定测试
npx playwright test -g "管理员" tests/e2e/login.spec.js
```

---

祝你测试顺利！如有问题，查看 `tests/e2e/README.md` 获取更详细的帮助。 🚀

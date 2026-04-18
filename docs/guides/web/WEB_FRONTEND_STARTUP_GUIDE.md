# MyStocks Web 前端启动指南

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


本指南提供 MyStocks Web 项目（Vue 3 + Vite 前端 + FastAPI 后端）的启动和开发说明。

## 项目结构

```
/opt/claude/mystocks_spec/
├── web/
│   ├── frontend/              # Vue 3 + Vite + TypeScript 前端
│   │   ├── src/
│   │   ├── vite.config.mts
│   │   ├── package.json
│   │   ├── ecosystem.config.js        # 前端 PM2 配置
│   │   ├── .env                       # 当前激活的环境配置
│   │   ├── .env.real                  # 真实 API 模式
│   │   └── .env.mock                  # Mock 数据模式
│   ├── backend/               # FastAPI + Python 后端
│   │   ├── app/
│   │   ├── pm2_start.py              # 正确的 PM2 启动脚本
│   │   └── requirements.txt
│   └── ecosystem.dev.config.js       # 前后端联合开发配置
└── docs/
```

## 快速启动

### 方法 1：使用 npm 脚本（推荐用于开发）

**前端启动：**

```bash
cd /opt/claude/mystocks_spec/web/frontend

# 开发模式（使用当前 .env 配置）
npm run dev

# 使用 Mock 数据模式
npm run dev:mock

# 使用真实 API 模式
npm run dev:real

# 跳过类型生成直接启动（更快）
npm run dev:no-types
```

**后端启动：**

```bash
cd /opt/claude/mystocks_spec/web/backend

# 设置 PYTHONPATH 并启动
PYTHONPATH=/opt/claude/mystocks_spec:/opt/claude/mystocks_spec/web/backend \
python -m uvicorn app.main:app --host 0.0.0.0 --port 8020 --reload
```

### 方法 2：使用 PM2（推荐用于持久运行）

**前端：**

```bash
cd /opt/claude/mystocks_spec/web/frontend
pm2 start ecosystem.config.js
pm2 logs mystocks-frontend
```

**后端（正确方式）：**

```bash
cd /opt/claude/mystocks_spec/web/backend
pm2 start pm2_start.py --name mystocks-backend --interpreter python3
pm2 logs mystocks-backend
```

**前后端联合启动：**

```bash
cd /opt/claude/mystocks_spec/web
pm2 start ecosystem.dev.config.js
pm2 logs
```

**PM2 管理命令：**

```bash
pm2 list                    # 查看所有进程
pm2 stop mystocks-frontend  # 停止前端
pm2 stop mystocks-backend   # 停止后端
pm2 restart all             # 重启所有
pm2 delete all              # 删除所有进程
```

### 方法 3：手动启动（用于调试）

**前端：**

```bash
cd /opt/claude/mystocks_spec/web/frontend
npm install                 # 首次运行需要安装依赖
npx motia generate-types    # 生成类型（可选）
npx vite                    # 启动 Vite 开发服务器
```

**后端：**

```bash
cd /opt/claude/mystocks_spec/web/backend
pip install -r requirements.txt  # 首次运行需要安装依赖

# 方式 1：使用 uvicorn 直接启动
PYTHONPATH=/opt/claude/mystocks_spec:/opt/claude/mystocks_spec/web/backend \
python -m uvicorn app.main:app --host 0.0.0.0 --port 8020 --reload

# 方式 2：使用 Python 模块方式
cd /opt/claude/mystocks_spec
PYTHONPATH=/opt/claude/mystocks_spec:/opt/claude/mystocks_spec/web/backend \
python -m web.backend.app.main
```

## 端口配置

### 当前端口使用情况

- **前端开发服务器**：端口 3020（由 `.env` 中 `FRONTEND_PORT` 控制）
- **后端 API 服务器**：端口 8020（由 `.env` 中 `BACKEND_PORT` 控制）

### 端口配置说明

端口统一通过项目根目录 `.env` 管理（`ecosystem.test.config.js` 和 `config/pm2.config.js` 均从 `.env` 读取）：

```
FRONTEND_PORT=3020
FRONTEND_BACKUP_PORT=3021
BACKEND_PORT=8020
BACKEND_BACKUP_PORT=8021
```

允许范围（CLAUDE.md 项目规则）：前端 3020-3029，后端 8020-8029。

### Vite 代理配置

前端开发服务器配置了 API 代理：

```typescript
// vite.config.mts
proxy: {
  '/api': {
    target: 'http://localhost:8020',
    changeOrigin: true
  }
}
```

所有 `/api` 开头的请求会被代理到后端服务器。

## 环境配置

### 环境文件说明

- **`.env`**：当前激活的配置（默认与 `.env.real` 相同）
- **`.env.real`**：真实 API 模式配置
  ```
  VITE_API_BASE_URL=http://localhost:8020
  VITE_APP_MODE=real
  ```
- **`.env.mock`**：Mock 数据模式配置
  ```
  VITE_API_BASE_URL=http://localhost:8020
  VITE_APP_MODE=mock
  ```

### 切换环境

```bash
# 切换到 Mock 模式
npm run dev:mock

# 切换到真实 API 模式
npm run dev:real

# 或手动复制
cp .env.mock .env  # 使用 Mock 数据
cp .env.real .env  # 使用真实 API
```

## 登录凭据

开发环境测试账号：

- **管理员**：`admin` / `admin123`
- **普通用户**：`user` / `user123`

## 构建和部署

### 开发构建

```bash
cd /opt/claude/mystocks_spec/web/frontend

# 完整构建（包含类型检查）
npm run build

# 快速构建（跳过类型生成）
npm run build:no-types

# 预览构建结果
npm run preview
```

### 生产部署

```bash
# 构建生产版本
npm run build

# 使用 PM2 启动生产服务器
pm2 start start.sh --name mystocks-prod
```

## 测试

### E2E 测试

```bash
cd /opt/claude/mystocks_spec/web/frontend

# 运行所有 E2E 测试（推荐入口）
npm run test:e2e

# 运行特定测试文件（补充场景：单文件测试）
npx playwright test tests/comprehensive-all-pages.spec.ts --project=chromium --reporter=list

# 以 UI 模式运行测试（补充场景：UI模式）
npx playwright test --ui
```

## 常见问题排查

### 1. 前端无法启动

**问题**：端口被占用

```bash
# 检查端口占用
lsof -i :3020

# 终止占用进程
kill -9 <PID>

# 或使用 PM2 清理
pm2 delete all
```

**问题**：依赖缺失

```bash
cd /opt/claude/mystocks_spec/web/frontend
rm -rf node_modules package-lock.json
npm install
```

### 2. 后端无法启动

**问题**：ImportError 或模块找不到

**原因**：PYTHONPATH 未正确设置

**解决方案**：

```bash
# ❌ 错误方式（会导致 ImportError）
pm2 start web/backend/app/main.py --interpreter python3

# ✅ 正确方式 1：使用 pm2_start.py
cd /opt/claude/mystocks_spec/web/backend
pm2 start pm2_start.py --name mystocks-backend --interpreter python3

# ✅ 正确方式 2：手动设置 PYTHONPATH
cd /opt/claude/mystocks_spec/web/backend
PYTHONPATH=/opt/claude/mystocks_spec:/opt/claude/mystocks_spec/web/backend \
python -m uvicorn app.main:app --host 0.0.0.0 --port 8020 --reload
```

### 3. API 请求失败

**检查后端是否运行：**

```bash
curl http://localhost:8020/health
```

**检查 Vite 代理配置：**

确保 `vite.config.mts` 中的代理目标正确：

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8020',
    changeOrigin: true
  }
}
```

**检查环境变量：**

```bash
cat /opt/claude/mystocks_spec/web/frontend/.env
# 确认 VITE_API_BASE_URL=http://localhost:8020
```

### 4. PM2 进程频繁重启

**查看日志：**

```bash
pm2 logs mystocks-backend --lines 50
```

**常见原因：**

- Python 模块导入错误（PYTHONPATH 问题）
- 端口被占用
- 依赖包缺失

**解决方案：**

```bash
# 停止并删除问题进程
pm2 delete mystocks-backend

# 使用正确的启动方式重新启动
cd /opt/claude/mystocks_spec/web/backend
pm2 start pm2_start.py --name mystocks-backend --interpreter python3
```

### 5. 类型生成失败

```bash
cd /opt/claude/mystocks_spec/web/frontend

# 手动生成类型
npx motia generate-types

# 如果失败，跳过类型生成直接启动
npm run dev:no-types
```

### 6. 构建失败

**清理缓存重新构建：**

```bash
cd /opt/claude/mystocks_spec/web/frontend
rm -rf dist node_modules/.vite
npm run build
```

**跳过类型检查：**

```bash
npm run build:no-types
```

### 7. 页面白屏或组件加载失败

**问题**：浏览器控制台报 `Failed to fetch dynamically imported module`

**原因**：组件导入路径错误或 Vite 缓存未更新

**解决方案**：

```bash
cd /opt/claude/mystocks_spec/web/frontend

# 清理 Vite 缓存
rm -rf node_modules/.vite

# 重启前端服务
pm2 restart mystocks-frontend
```

### 8. CORS 错误

**问题**：控制台报 `Access to XMLHttpRequest ... blocked by CORS policy`

**原因**：后端未允许当前前端域名访问

**解决方案**：

1. 检查后端 `app/main.py` 中的 CORS 配置
2. 确保已添加 `allow_origins=["*"]`（开发环境）
3. 重启后端服务：`pm2 restart mystocks-backend`

### 9. 缺少依赖包

**问题**：构建时报错 `Rollup failed to resolve import`

**解决方案**：

```bash
cd /opt/claude/mystocks_spec/web/frontend

# 安装缺失的依赖
npm install @ant-design/icons-vue

# 重新构建
npm run build
```

## 开发工具

### Vite 开发服务器特性

- **热模块替换（HMR）**：代码修改后自动刷新
- **快速冷启动**：使用 ESM 原生支持
- **优化的构建**：基于 Rollup 的生产构建

### Vue DevTools

推荐安装 Vue DevTools 浏览器扩展以便调试：

- [Chrome](https://chrome.google.com/webstore/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd)
- [Firefox](https://addons.mozilla.org/en-US/firefox/addon/vue-js-devtools/)

### API 文档

后端启动后可访问：

- **Swagger UI**：http://localhost:8020/docs
- **ReDoc**：http://localhost:8020/redoc
- **健康检查**：http://localhost:8020/health

## 辅助工具

### 浏览器环境管理

使用 `scripts/ensure_browsers.sh` 在运行浏览器测试前确保环境一致：

```bash
# 清理旧版本 + 检查驱动对齐
bash scripts/ensure_browsers.sh

# 清理 + 自动安装缺失驱动
bash scripts/ensure_browsers.sh --fix

# 列出所有可用浏览器及驱动版本
bash scripts/ensure_browsers.sh --list
```

### Playwright CLI 测试

使用 `scripts/run_playwright_cli_tests.sh` 运行交互式路由测试：

```bash
# 快速测试（P0 + P1 路由）
bash scripts/run_playwright_cli_tests.sh --quick

# 冒烟测试（P0-P3）
bash scripts/run_playwright_cli_tests.sh --smoke

# 全量测试（所有路由）
bash scripts/run_playwright_cli_tests.sh --full
```

测试前需确保 PM2 服务已启动（前端 :3020，后端 :8020）。

## 当前已知问题

### 1. ~~端口配置不一致~~ (已解决)

端口已统一通过 `.env` 管理，`config/pm2.config.js` 从 `.env` 读取端口配置。

### 2. 后端 PYTHONPATH 问题

直接使用 `pm2 start app/main.py` 会导致 ImportError，因为 Python 无法找到项目模块。

**当前解决方案**：

使用 `config/pm2.config.js`（推荐）或 `pm2_start.py` 启动脚本，它们会正确设置 PYTHONPATH。

### 3. PM2 后端进程频繁重启

如果使用错误的启动命令，后端会因为 ImportError 而不断重启。

**解决方案**：

使用统一的 PM2 配置：`pm2 start config/pm2.config.js`。

### 4. ~~PM2 健康检查端口不匹配~~ (已解决)

`config/pm2.config.js` 从 `.env` 读取端口，健康检查 URL 与实际端口一致。

## 相关文档

- **PM2 统一配置**：`config/pm2.config.js`
- **浏览器管理脚本**：`scripts/ensure_browsers.sh`
- **Playwright CLI 测试**：`scripts/run_playwright_cli_tests.sh`
- **测试指南**：`docs/guides/chrome-devtools/mystocks-chromedevtools-testing-guide.md`
- **修复报告**：`docs/reports/FRONTEND_JS_SYNTAX_FIX_REPORT.md`
- **测试报告**：`docs/reports/CHROME_DEVTOOLS_TESTING_REPORT_*.md`

---

**文档版本**：v3.0
**最后更新**：2026-04-18
**项目路径**：`/opt/claude/mystocks_spec`

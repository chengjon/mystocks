# MyStocks Web 前端启动指南

本指南提供 MyStocks Web 项目（Vue 3 + Vite 前端 + FastAPI 后端）的启动和开发说明。

## 项目结构

```
/opt/claude/mystocks_spec/
├── web/
│   ├── frontend/              # Vue 3 + Vite + TypeScript 前端
│   │   ├── src/
│   │   ├── vite.config.ts
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
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
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
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 方式 2：使用 Python 模块方式
cd /opt/claude/mystocks_spec
PYTHONPATH=/opt/claude/mystocks_spec:/opt/claude/mystocks_spec/web/backend \
python -m web.backend.app.main
```

## 端口配置

### 当前端口使用情况

- **前端开发服务器**：端口 3020（实际运行）
- **后端 API 服务器**：端口 8000（实际运行）

### 端口配置说明

项目中存在多个端口配置来源，目前状态较为混乱：

1. **vite.config.ts**：使用 `findAvailablePort(3000, 3009)` 自动查找可用端口
2. **ecosystem.config.js**：设置 `PORT=3020`（但 Vite 会忽略此环境变量）
3. **ecosystem.dev.config.js**：设置 `PORT=3001`
4. **CLAUDE.md 项目规则**：前端 3020-3029，后端 8020-8029

**推荐的标准配置：**

- 开发环境前端：3020-3029 范围内
- 开发环境后端：8000（当前实际使用）
- 生产环境：根据部署环境配置

### Vite 代理配置

前端开发服务器配置了 API 代理：

```typescript
// vite.config.ts
proxy: {
  '/api': {
    target: 'http://localhost:8000',
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
  VITE_API_BASE_URL=http://localhost:8000
  VITE_APP_MODE=real
  ```
- **`.env.mock`**：Mock 数据模式配置
  ```
  VITE_API_BASE_URL=http://localhost:8000
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

# 运行所有 E2E 测试
npm run test:e2e

# 运行特定测试文件
npx playwright test tests/comprehensive-all-pages.spec.ts --project=chromium --reporter=list

# 以 UI 模式运行测试
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
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. API 请求失败

**检查后端是否运行：**

```bash
curl http://localhost:8000/health
```

**检查 Vite 代理配置：**

确保 `vite.config.ts` 中的代理目标正确：

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true
  }
}
```

**检查环境变量：**

```bash
cat /opt/claude/mystocks_spec/web/frontend/.env
# 确认 VITE_API_BASE_URL=http://localhost:8000
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

- **Swagger UI**：http://localhost:8000/docs
- **ReDoc**：http://localhost:8000/redoc
- **健康检查**：http://localhost:8000/health

## 当前已知问题

### 1. 端口配置不一致

**问题描述**：

项目中存在多个端口配置来源，导致配置不一致：

- `vite.config.ts` 使用 `findAvailablePort(3000, 3009)`
- `ecosystem.config.js` 设置 `PORT=3020`
- `ecosystem.dev.config.js` 设置 `PORT=3001`
- `CLAUDE.md` 规定前端使用 3020-3029

**当前状态**：

前端实际运行在 3020 端口（可能是因为 3000-3009 被占用）

**建议解决方案**：

统一配置为 3020-3029 范围，修改 `vite.config.ts`：

```typescript
server: {
  port: await findAvailablePort(3020, 3029),
  // ...
}
```

### 2. 后端 PYTHONPATH 问题

**问题描述**：

直接使用 `pm2 start app/main.py` 会导致 ImportError，因为 Python 无法找到项目模块。

**当前解决方案**：

必须使用 `pm2_start.py` 启动脚本，它会正确设置 PYTHONPATH。

**建议改进**：

在项目根目录添加 `setup.py` 或使用 Poetry 管理依赖，使项目成为可安装的 Python 包。

### 3. PM2 后端进程频繁重启

**当前状态**：

如果使用错误的启动命令，后端会因为 ImportError 而不断重启（已观察到 468 次重启）。

**解决方案**：

严格按照本指南的"方法 2"使用 `pm2_start.py` 启动后端。

### 4. PM2 健康检查端口不匹配

**问题描述**：

`ecosystem.config.js` 中的健康检查 URL 可能配置为 3002，但前端实际运行在 3020。

**影响**：

PM2 健康检查失败，可能触发不必要的重启。

**解决方案**：

更新 `ecosystem.config.js` 中的 `health_check.url` 为实际运行端口：

```javascript
health_check: {
  url: 'http://localhost:3020',
  timeout: 5000,
  retries: 3,
  interval: 10000
}
```

## 相关文档

- **测试指南**：`docs/guides/mystocks-chromedevtools-testing-guide.md`
- **修复报告**：`docs/reports/FRONTEND_JS_SYNTAX_FIX_REPORT.md`
- **测试报告**：`docs/reports/CHROME_DEVTOOLS_TESTING_REPORT_*.md`

---

**文档版本**：v2.0
**最后更新**：2025-02-12
**项目路径**：`/opt/claude/mystocks_spec`

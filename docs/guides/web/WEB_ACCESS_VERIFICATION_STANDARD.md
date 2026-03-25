# Web 端"正常访问"验证标准

**版本**: v2.0
**创建日期**: 2026-02-14
**更新日期**: 2026-02-14
**状态**: 强制执行

---

## 1. 概述

本文档定义了 MyStocks Web 端"正常访问"的严格验证标准。任何声称"服务正常运行"或"可以正常访问"的判断，必须基于本文档定义的完整验证流程。

### 1.1 为什么需要这个标准？

**历史教训**：
- 仅检查 HTTP 200 无法发现前端运行时错误
- 仅检查后端健康无法发现页面白屏问题
- 未进行端到端测试会导致用户实际使用时才发现问题
- Mock 模式下全绿不等于真实模式下正常

**错误示例**（禁止）：
```
❌ "服务正常，HTTP 200"
❌ "后端健康检查通过，可以访问"
❌ "前端已启动在 3020 端口"
```

**正确示例**（必须）：
```
✅ "全量路由测试通过 (Passed: N/N)，无白屏，无控制台错误"
✅ "登录功能已验证，Dashboard 数据正常显示"
✅ "数据源: REAL (Connected to localhost:8020)"
```

---

## 2. 验证标准（七要素）

**"正常访问" = 以下七要素全部通过**

| # | 要素 | 验证方法 | 动态通过标准 |
|---|------|---------|-------------|
| 1 | **接口业务成功** | `curl /health` | code=0/200 且 延迟<500ms |
| 2 | **页面无崩溃** | Playwright 测试 | 无 WHITE_SCREEN |
| 3 | **无编译错误** | Vite 控制台 | 无 VITE_ERROR |
| 4 | **无运行时错误** | Console | 无 PAGE_ERRORS |
| 5 | **全量路由覆盖** | 动态扫描 | 通过率 100% (Passed/Total) |
| 6 | **Mock/Real 一致性** | 环境变量检查 | 当前模式与 .env 配置一致 |
| 7 | **首屏加载耗时** | Playwright | 首屏 < 3s，超时视为失败 |

### 2.1 一键验证命令

```bash
# 开发者只需运行一句命令
npm run verify:web-access

# 或完整路径
cd /opt/claude/mystocks_spec/web/frontend && npm run verify:web-access
```

**输出**：直接打印 Markdown 格式报告，并根据结果返回 exit code 0 或 1（便于 CI 阻断）。

### 2.2 详细验证步骤

#### 步骤 1：服务启动验证

```bash
# 检查端口
lsof -i :8020 -i :3020

# 后端健康检查（含延迟检测）
curl -w "\nLatency: %{time_total}s\n" http://localhost:8020/health
# 期望: {"success":true,"code":200,"data":{"status":"healthy"}}
# 延迟: < 0.5s
```

#### 步骤 2：数据源模式验证

```bash
# 检查当前数据源模式
cat /opt/claude/mystocks_spec/web/frontend/.env | grep VITE_APP_MODE
# 期望: VITE_APP_MODE=real (或 mock)

# 验证后端连接（仅 Real 模式）
curl http://localhost:8020/api/market/overview 2>/dev/null | head -c 200
# 期望: 返回有效 JSON，非错误响应
```

#### 步骤 3：全量路由测试（核心）

```bash
# 运行动态路由验证脚本
cd /opt/claude/mystocks_spec
node scripts/dev/test_all_pages.mjs

# 脚本会自动：
# 1. 读取 router 配置动态计算路由总数
# 2. 逐个访问并验证页面状态
# 3. 输出 Markdown 格式报告
# 4. 返回正确的 exit code
```

#### 步骤 4：性能验证

```bash
# 首屏加载耗时测试（集成在 test_all_pages.mjs 中）
# 阈值: 3 秒
# 超时页面会被标记为 TIMEOUT_FAILURE
```

### 2.3 通过标准

**服务正常运行** 的判断标准：

```
✅ Passed: N/N (100%)
✅ Failed: 0/N
✅ Data Source: REAL/MOCK (consistent with .env)
✅ Avg Load Time: < 3s
```

**部分可用** 的判断标准（需要明确告知用户）：

```
⚠️ Passed: X/N (X% < 100%)
⚠️ Failed: Y/N
⚠️ 以下页面不可用: [列表]
⚠️ 建议修复后再使用
```

**服务异常** 的判断标准：

```
❌ Passed: < 70%
❌ 主要错误: [错误类型]
❌ 建议修复后再使用
```

---

## 3. 动态路由发现机制

验证脚本不再硬编码页面数量，而是动态发现：

```javascript
// scripts/dev/test_all_pages.mjs 中的路由发现逻辑
import { readFileSync } from 'fs';

// 方案 A: 解析 router 配置
const routerConfig = readFileSync('./web/frontend/src/router/index.ts', 'utf-8');
const routes = parseRoutesFromConfig(routerConfig);

// 方案 B: 扫描 views 目录
const viewFiles = glob.sync('./web/frontend/src/views/**/*.vue');
const routes = viewFiles.map(file => pathToRoute(file));

console.log(`动态发现 ${routes.length} 个路由`);
```

---

## 4. 常见错误类型

### 4.1 WHITE_SCREEN（白屏）

**原因**：
- Vue 组件加载失败
- 路由守卫错误
- Store 未初始化

**检查方法**：
```bash
curl -s http://localhost:3020/login | grep -o '<div id="app">.*</div>'
```

### 4.2 VITE_ERROR（编译错误）

**原因**：
- Vue 模板语法错误（如重复的 `:key`）
- 导入路径错误
- TypeScript 类型错误

**检查方法**：
```bash
curl -s "http://localhost:3020/src/views/SomeComponent.vue" | head -10
# 如果返回 HTML 错误页面，说明有编译错误
```

### 4.3 CONSOLE_ERRORS（控制台错误）

**常见类型**：
- `TypeError: Cannot read properties of undefined`
- `ReferenceError: X is not defined`
- `Failed to fetch dynamically imported module`

### 4.4 TIMEOUT_FAILURE（超时失败）

**原因**：
- 页面加载过慢（> 3s）
- 网络延迟
- 资源过大

---

## 5. 验证报告模板

每次验证后，脚本自动输出以下格式的报告：

```markdown
## Web 端访问验证报告

**验证时间**: YYYY-MM-DD HH:MM
**前端端口**: 3020
**后端端口**: 8000
**数据源**: REAL (Connected to localhost:8020)

### 服务状态
- 后端健康检查: ✅ (延迟: 0.12s)
- 前端编译状态: ✅

### 页面测试结果
- 总路由数: N (动态发现)
- 通过: X/N (X%)
- 失败: Y/N
- 平均加载时间: X.XXs

### 失败页面详情
| 页面 | 问题类型 | 错误信息 | 加载时间 |
|------|---------|---------|---------|
| /login | WHITE_SCREEN | Store 未初始化 | 0.5s |

### 结论
[✅ 服务正常 / ⚠️ 部分可用 / ❌ 服务异常]
```

---

## 6. CI/CD 集成

### GitHub Actions 示例

```yaml
name: Web Access Verification

on:
  pull_request:
    paths:
      - 'web/frontend/**'
  workflow_dispatch:

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '24'

      - name: Install dependencies
        run: |
          cd web/frontend
          npm ci

      - name: Start services
        run: |
          # 启动后端
          cd web/backend
          pip install -r requirements.txt
          PYTHONPATH=../.. uvicorn app.main:app --port 8020 &

          # 启动前端
          cd ../frontend
          npm run dev -- --port 3020 &

          # 等待服务就绪
          sleep 30

      - name: Run verification
        run: |
          cd web/frontend
          npm run verify:web-access

      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: verification-report
          path: scripts/dev/page_test_results.json
```

---

## 7. 相关文档

- [前端启动指南](./web/WEB_FRONTEND_STARTUP_GUIDE.md)
- [前端 JS 语法修复报告](../reports/FRONTEND_JS_SYNTAX_FIX_REPORT.md)
- [Chrome DevTools 测试指南](./chrome-devtools/mystocks-chromedevtools-testing-guide.md)

---

## 8. 修订历史

| 版本 | 日期 | 修改内容 |
|------|------|---------|
| v1.0 | 2026-02-14 | 初始版本，定义六要素验证标准 |
| v2.0 | 2026-02-14 | 新增：动态路由发现、Mock/Real 验证、性能维度、一键命令、CI 集成 |

---

**重要提醒**：

> 在声称"服务正常"或"可以访问"之前，必须运行完整的验证测试。
> 任何低于 100% 通过率的情况，都需要明确告知用户哪些页面不可用。
> 必须明确当前使用的数据源模式（MOCK/REAL）。

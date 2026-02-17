# MyStocks 前端白屏故障诊断报告 (Diagnostic Report)

**日期**: 2026-02-17  
**报告人**: Gemini CLI Agent  
**环境信息**:
- **OS**: Linux (WSL2)
- **Node.js**: v24.7.0 (Current Stable)
- **Frontend Stack**: Vue 3 + Vite 5 + TypeScript
- **Entrypoint**: `web/frontend/src/main-standard.ts`

---

## 1. 核心症状 (Symptoms)
- **现象**: 浏览器访问 `http://localhost:3000` 出现 **白屏**。
- **Playwright**: 自动化测试报错 `Error: page.goto: net::ERR_CONNECTION_RESET at http://localhost:3000/`。
- **Curl 探测**: `curl -v http://localhost:3000` 显示 `Recv failure: Connection reset by peer`。这意味着 TCP 握手完成后，服务端在发送数据前强制断开了连接。

## 2. 已排除的常规故障 (Ruled Out)

| 检查项 | 诊断动作 | 结果 |
| :--- | :--- | :--- |
| **端口冲突** | 使用 `lsof -i :3000` 和 `kill -9` 彻底清理残留进程。 | ✅ 确认端口纯净，仅由当前 PM2 进程监听。 |
| **入口文件引用** | 检查 `index.html`，发现引用了不存在的 `main-standard.ts` (误报) / `main.ts`。 | ✅ 已修正为指向真实的 `main-standard.ts` (极简启动入口)。 |
| **Vite 配置语法** | PM2 日志曾报 `Expected ")" but found ";"`。 | ✅ 已修复 `vite.config.ts` 中的语法错误。 |
| **插件崩溃** | 日志显示 `vite-plugin-pwa` 在 Node 24 下校验 Schema 失败。 | ✅ 已在配置中禁用 PWA 插件。 |
| **代理配置** | 检查 `server.proxy` 是否缺失导致 API 请求失败。 | ✅ 已恢复 `/api` -> `localhost:8000` 的反向代理。 |

## 3. 根因假设 (Hypothesis)

**Node.js v24.7.0 与 Vite/Esbuild 的底层兼容性问题。**

尽管 Vite 开发服务器（Dev Server）的 Node 进程在 PM2 中显示为 `online`，但在处理 HTTP 请求时——特别是涉及到 `esbuild` 进行实时转译（JIT Compilation）的环节——底层的 C++ 绑定或网络栈可能发生了段错误（Segmentation Fault）或未捕获异常，导致 Socket 被操作系统立即关闭（RST）。

这种情况在极新的 Node 版本（如 v24）运行较旧或未适配的二进制依赖（如 `@esbuild/linux-x64`）时较为常见。

## 4. 尝试过的方案与结果

1.  **清理重启**: `pm2 kill` + `rm -rf node_modules/.vite` + `npm run dev`。
    *   **结果**: 失败，依然 `CONNECTION_RESET`。
2.  **简化配置**: 移除所有 Vite 插件（PWA, Visualizer），仅保留 Vue。
    *   **结果**: 失败，现象依旧。
3.  **切换入口**: 将入口从复杂的 `main.js` 切回无依赖的 `main-standard.ts`。
    *   **结果**: 失败，证明问题不在业务代码，而在构建工具层。

## 5. 建议的下一步 (Next Steps)

1.  **环境降级**: 强烈建议将 Node.js 降级至 **LTS 版本 (v18 或 v20)**。这是解决此类二进制兼容性问题最直接的方法。
2.  **构建模式 (Build Mode)**: 尝试 `npm run build` 生成静态文件，然后使用 `npm run preview` 运行。这可以绕过 `esbuild` 的实时编译，验证代码本身是否健康。
3.  **Docker 化**: 如果本地环境难以修复，建议将前端放入 Docker 容器（基于 Node 18 镜像）运行。

---
**附录**: 关键日志片段
```
error when starting dev server:
Error: Build failed with 1 error:
vite.config.ts:215:3: ERROR: Expected ")" but found ";"
...
(修复后)
The CJS build of Vite's Node API is deprecated.
...
curl: (56) Recv failure: Connection reset by peer
```

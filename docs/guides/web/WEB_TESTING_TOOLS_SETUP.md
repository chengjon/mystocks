# MyStocks 网络与测试工具集配置

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


本文档定义当前 Web 验证环境的标准拓扑，并补充 API 管理相关的最小核对动作。本文档已在 `2026-04-24` 重新核对。

---

## 1. 端口与访问分配
| 服务 | 地址 | 访问角色 |
| :--- | :--- | :--- |
| **Frontend** | `http://localhost:3020` | 开发与 E2E 测试入口 |
| **Backend** | `http://localhost:8020` | REST API / Health 探针 |
| **Redis** | `127.0.0.1:6379` | 热点数据中转 / 跨系统桥接 |
| **OpenAPI** | `http://localhost:8020/openapi.json` | 运行时契约校验 |

## 2. 自动化工具链

### 2.1 Playwright (Primary)
- **用途**: 标准 Web E2E 主线；负责导航一致性校验、跨浏览器验证、视觉回归与 axe smoke。
- **配置**: `playwright.config.js`（标准 E2E）/ `playwright.config.ts`（legacy 专项脚本）。

### 2.2 Vitest + Vue Test Utils (Primary Unit/Integration)
- **用途**: 组件单测、组合式函数测试、MSW 驱动的前端 API 集成测试。
- **配置**: `vitest.config.mts` + `vitest.setup.ts`。

### 2.3 Lighthouse CI / MSW / axe (Supporting)
- **MSW**: Vitest 网络层 Mock。
- **axe**: Playwright 可访问性 smoke。
- **Lighthouse CI**: 隔离 `mock build + preview:lighthouse` 的性能门禁。

### 2.4 Cypress / Puppeteer (Legacy)
- **状态**: 不再作为标准 Web 测试主线，仅允许保留在归档脚本或历史文档中，不再新增依赖和用例。

### 2.5 lnav (Observability)
- **命令**: `lnav /root/.pm2/logs/mystocks-backend-error.log`。

## 3. API 核对推荐命令

```bash
curl -s http://localhost:8020/health | python -m json.tool
curl -s http://localhost:8020/api/health/detailed | python -m json.tool
python scripts/generate_openapi.py --output /tmp/mystocks_openapi_current.json
```

用途：

- 第一条确认后端主健康探针
- 第二条确认详细健康输出
- 第三条确认当前运行时契约可成功导出

## 4. REAL DATA 暖机逻辑
在执行 E2E 测试前，系统必须预留至少 **15s** 的暖机时间，用于：
1. Vite 依赖预构建。
2. 后端单例初始化与数据库连接探测。
3. Redis 信号握手。

## 5. 当前注意事项

- 前端相对请求路径通常通过 `apiClient` 的 `baseURL=/api` 拼接为最终 HTTP 路径，核对文档时要区分“前端相对路径”和“后端真实路径”
- API 可用性验证必须回到 OpenAPI 或真实请求结果，不能复用旧的静态统计值

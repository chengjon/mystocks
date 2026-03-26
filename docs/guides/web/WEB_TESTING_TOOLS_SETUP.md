# MyStocks 网络与测试工具集配置 (v1.1.0)

本文档定义了自动化验证环境的标准拓扑。

---

## 1. 端口与访问分配 (Port Allocation)
| 服务 | 地址 | 访问角色 |
| :--- | :--- | :--- |
| **Frontend** | `http://localhost:3020` | 开发与 E2E 测试入口 |
| **Backend** | `http://localhost:8020` | REST API / Health 探针 |
| **Redis** | `127.0.0.1:6379` | 热点数据中转 / 跨系统桥接 |

## 2. 自动化工具链 (Toolchain)
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

---

## 3. REAL DATA 暖机逻辑
在执行 E2E 测试前，系统必须预留至少 **15s** 的暖机时间，用于：
1. Vite 依赖预构建。
2. 后端单例初始化与数据库连接探测。
3. Redis 信号握手。

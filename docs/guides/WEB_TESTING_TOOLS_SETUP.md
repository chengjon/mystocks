# MyStocks 网络与测试工具集配置 (v1.1.0)

本文档定义了自动化验证环境的标准拓扑。

---

## 1. 端口与访问分配 (Port Allocation)
| 服务 | 地址 | 访问角色 |
| :--- | :--- | :--- |
| **Frontend** | `http://localhost:3001` | 开发与 E2E 测试入口 |
| **Backend** | `http://localhost:8000` | REST API / Health 探针 |
| **Redis** | `127.0.0.1:6379` | 热点数据中转 / 跨系统桥接 |

## 2. 自动化工具链 (Toolchain)
### 2.1 Playwright (Primary)
- **用途**: 导航一致性校验、视觉回归。
- **配置**: `playwright.config.ts` (Viewport: 1920x1080)。

### 2.2 Cypress (Compatible)
- **兼容性提示**: 系统支持 Cypress 挂载。如需执行单元组件测试（Component Testing），可复用 Playwright 的 BASE_URL。

### 2.3 lnav (Observability)
- **命令**: `lnav /root/.pm2/logs/mystocks-backend-error.log`。

---

## 3. REAL DATA 暖机逻辑
在执行 E2E 测试前，系统必须预留至少 **15s** 的暖机时间，用于：
1. Vite 依赖预构建。
2. 后端单例初始化与数据库连接探测。
3. Redis 信号握手。

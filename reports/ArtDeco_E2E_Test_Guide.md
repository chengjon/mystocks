# MyStocks ArtDeco 3.1 导航一致性测试与架构治理指南

本指南旨在详细记录 ArtDeco 3.1 架构升级后的导航一致性治理工作，并提供一套可复现的自动化测试闭环流程。

---

## 一、 本次治理工作汇总 (Work Summary)

### 1. 核心架构修复
*   **路由引擎复位**：修复了 [web/frontend/src/App.vue](../web/frontend/src/App.vue) 中硬编码直接渲染组件导致路由系统失效的致命错误。
*   **路径语义化对齐**：在 [web/frontend/src/router/index.ts](../web/frontend/src/router/index.ts) 中为“交易管理”域添加了路由别名（Alias），解决了菜单配置（`/trading`）与路由物理实现（`/strategy` 或 `/stocks`）脱节的问题。

### 2. 后端稳定性加固
*   **消除导入死循环**：修复了 `main.py` 中因引用不存在的中间件导致的后端不断崩溃重启。
*   **单例模式治理**：校准了 [get_market_data_service.py](../web/backend/app/services/market_data_service/get_market_data_service.py) 和 [data_source_factory.py](../web/backend/app/services/data_source_factory/data_source_factory.py) 中的全局变量初始化，彻底消除了 API 请求中的 500 NameError 异常。

---

## 二、 宝贵经验与架构洞察 (Lessons Learned)

1.  **“所见非所得”的假象**：如果 `App.vue` 存在硬编码，无论 URL 如何变化，页面内容都不会真正切换。**经验**：升级 UI 架构后，首要验证 `<router-view />` 的纯净度。
2.  **观测工具的价值**：通过 `pm2 list` 观察重启次数（↺）和 `lnav` 实时追踪错误栈，是定位“隐形死循环”的最快手段。
3.  **导航联动不仅是路由**：菜单 Label（中文）与组件标题（英文）的一致性决定了测试的断言成效。**经验**：测试用例的断言必须基于“源码采样”而非“假设”。
4.  **应对异步与动画**：Vue Transition 动画会导致 DOM 在瞬间存在两份拷贝。**经验**：在 E2E 测试中，路由跳转后引入 1-2 秒的“暖机时间”能显著降低测试抖动。

---

## 三、 操作指南 (Step-by-Step Guide)

### 1. 环境准备
*   安装前端依赖：`cd web/frontend && npm install`
*   安装浏览器内核：`npx playwright install chromium`
*   安装后端依赖：`cd web/backend && pip install -r requirements.txt`

### 2. 配置校准
*   **Mock 模式**：确保 [web/backend/.env](../web/backend/.env) 中的 `USE_MOCK_DATA=true` 以提高测试稳定性。
*   **分辨率设置**：确保 [playwright.config.ts](playwright.config.ts) 中 viewport 宽度至少为 1920，防止侧边栏被响应式隐藏。

### 3. 运行测试
执行一键自动化脚本：
```bash
./scripts/run_e2e_pm2.sh
```
该脚本会自动完成：进程清理 -> 服务拉起 -> 端口探测 -> 暖机 -> 执行断言 -> 自动清理。

### 4. 调试与排查
*   **查看错误截图**：测试失败后，查看 `test-results/` 下生成的 `.png` 文件。
*   **实时追踪**：使用 `lnav` 查看后端错误日志：
    `lnav /root/.pm2/logs/mystocks-backend-error.log`
*   **交互调试**：运行 `npx playwright test tests/navigation-consistency.spec.ts --debug`

---

## 四、 关联文件索引

| 类别 | 文件路径 | 说明 |
| :--- | :--- | :--- |
| **测试脚本** | [tests/navigation-consistency.spec.ts](tests/navigation-consistency.spec.ts) | 核心 8 大业务域测试逻辑 |
| **执行入口** | [scripts/run_e2e_pm2.sh](scripts/run_e2e_pm2.sh) | 自动化闭环执行 shell 脚本 |
| **测试配置** | [playwright.config.ts](playwright.config.ts) | 浏览器环境与分辨率配置 |
| **进程管理** | [ecosystem.test.config.js](ecosystem.test.config.js) | 前后端服务 PM2 启动参数 |
| **路由定义** | [web/frontend/src/router/index.ts](../web/frontend/src/router/index.ts) | 包含所有别名与映射的路由源 |

---
**交付人**：Gemini CLI Agent  
**交付状态**：100% 通过验证 | 架构缺陷已修复 | 闭环流程已就绪

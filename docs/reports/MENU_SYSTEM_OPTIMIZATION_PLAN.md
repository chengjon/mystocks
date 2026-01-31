# MyStocks 菜单系统优化方案 (ArtDeco 2.0)

## 1. 概述
本方案旨在解决当前菜单系统路由碎片化、图标不专业、功能域模糊及数据耦合等问题。通过参考 `docs/api/ARTDECO_TRADING_CENTER_DESIGN.md`，我们将构建一个以“功能树”为核心、符合 ArtDeco 金色主题美学的专业量化交易导航系统。

## 2. 核心架构重组 (Functional Tree)

我们将现有的散乱路由重新划分为 5 大顶级域，严格遵守 3 层嵌套深度。

| 一级功能域 (Domains) | 核心路径 | 职责范围 |
| :--- | :--- | :--- |
| **🎯 市场总览 (Market)** | `/market/*` | 实时行情、指数、排行、行业概念分析、龙虎榜 |
| **💼 交易管理 (Trading)** | `/trading/*` | 交易信号、历史订单、持仓监控、绩效归因 |
| **🧠 策略中心 (Strategy)** | `/strategy/*` | 策略创建/配置、回测分析 (GPU加速)、参数优化 |
| **🛡️ 风险控制 (Risk)** | `/risk/*` | 风险概览、趋势分析、公告监控、告警中心 |
| **⚙️ 系统管理 (System)** | `/system/*` | 运维监控、数据导入导出、系统安全性设置 |

## 3. 关键组件与视觉升级

### 3.1 废弃图标 Emoji，引入几何图标系统
- **操作**：清理 `MenuConfig.enhanced.ts` 中的 Emoji。
- **实现**：使用 `src/components/artdeco/core/ArtDecoIcon.vue` 映射文档定义的 50+ 个 SVG 图标（如 `Chart`, `Bolt`, `Flask`, `Shield`）。
- **色彩**：统一使用 `--artdeco-gold-primary` (#D4AF37) 作为激活态颜色。

### 3.2 实现 ArtDecoFunctionTree 组件
- **组件位置**：`src/components/layout/ArtDecoFunctionTree.vue`。
- **特性**：
  - **3级结构支持**：支持折叠/展开动画。
  - **装饰元素**：添加金色几何边框 (`artdeco-geometric-border`) 和角点装饰。
  - **搜索过滤**：内置快速搜索功能，定位 40 个子菜单节点。

## 4. 路由与配置优化 (Router & Config)

### 4.1 路由层级扁平化
修改 `/opt/claude/mystocks_spec/web/frontend/src/router/index.ts`，将分散的 `/analysis`、`/stocks` 等根路由合并到 `/strategy` 或 `/trading` 下，保持 URL 与业务逻辑树一致。

### 4.2 API 解耦逻辑
从 `MenuItem` 接口中移除 `apiEndpoint` 等敏感字段。
- **新模式**：菜单项仅保留 `businessKey`（如 `market.realtime`）。
- **解析层**：由 `src/services/api/NavigationProvider.ts` 根据 `businessKey` 动态返回对应的 API 端点和 WebSocket 频道，实现 UI 与 API 的彻底解耦。

## 5. 跨端策略清理
根据 `CLAUDE.md` 规范，执行以下清理动作：
- **CSS 清理**：移除 `ArtDecoLayoutEnhanced.vue` 和 `ResponsiveSidebar.vue` 中所有 `@media (max-width: 768px)` 的媒体查询。
- **布局固定**：锁定侧边栏最小宽度为 280px，不再支持移动端自动折叠。

## 6. 实施路线图 (Phases)

1.  **Phase 1 (清理)**：移除旧版 Layout 文件及路由中的冗余 meta 信息，统一国际化 Key。
2.  **Phase 2 (重构)**：更新 `MenuConfig.enhanced.ts` 结构，完成 5 大域的逻辑合并。
3.  **Phase 3 (组件)**：开发 `ArtDecoFunctionTree` 并替换现有的 `NestedMenu`。
4.  **Phase 4 (对齐)**：完成所有 21 个 Vue 页面与新菜单节点的绑定及面包屑导航更新。

---
**核准状态**: 待执行
**最后更新**: 2026-01-24

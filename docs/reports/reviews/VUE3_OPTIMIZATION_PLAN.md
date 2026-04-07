# Vue 3 前端代码审查与优化方案

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


## 1. 概述
本次审查覆盖了 `web/frontend` 项目的核心架构、组件实现及配置。项目整体架构成熟，采用了 Vue 3 + TypeScript + Pinia + Vite 的现代技术栈。

## 2. 关键改进点 (Prioritized)

### [High] 统一菜单配置源 (Single Source of Truth)
**现状**: 项目中同时存在 `MenuConfig.ts` 和 `MenuConfig.enhanced.ts`，且多处代码引用 `enhanced` 版本。这导致了配置分裂和潜在的维护风险。
**方案**:
1.  确认 `MenuConfig.ts` 为最新、最完整的配置。
2.  将 `MenuConfig.enhanced.ts` 的内容（如果有的独特部分）合并入 `MenuConfig.ts`。
3.  全局替换 `import ... from '@/layouts/MenuConfig.enhanced'` 为 `import ... from '@/layouts/MenuConfig'`。
4.  删除 `MenuConfig.enhanced.ts`。

### [Medium] 侧边栏路由联动 (Sidebar Sync)
**现状**: `ArtDecoCollapsibleSidebar.vue` 仅在 `onMounted` 时根据当前路由展开菜单。如果用户通过点击面包屑或浏览器前进后退切换路由，侧边栏展开状态不会同步更新。
**方案**:
-   在 `setup` 中添加 `watch` 监听 `route.path`，触发展开逻辑。

```typescript
watch(
  () => router.currentRoute.value.path,
  (newPath) => {
    // 遍历菜单，如果 newPath 在某个子菜单中，展开该父菜单
    // 复用 initializeExpandedMenus 的逻辑
  }
)
```

### [Low] 图标按需加载优化
**现状**: `main-standard.ts` 循环注册了所有 `@element-plus/icons-vue`。
**方案**:
-   移除全局注册。
-   使用 `unplugin-vue-components` 的自动导入功能（已配置），或在需要的组件中显式导入特定图标。

### [Low] 现代化类型定义
**现状**: 使用 `shims-vue.d.ts`。
**方案**:
-   重命名为 `vite-env.d.ts`。
-   添加 `/// <reference types="vite/client" />` 以获得 `import.meta.env` 的正确类型提示。

## 3. 代码风格与规范

-   **Component**: 保持 `<script setup>` 风格。
-   **Store**: 保持 `defineStore(id, () => { ... })` Setup Store 风格。
-   **Style**: 保持 SCSS + CSS Variables (Design Tokens) 风格。

## 4. 执行计划

1.  **Refactor Menu**: 执行菜单配置合并与替换。
2.  **Enhance Sidebar**: 添加路由监听。
3.  **Cleanup**: 清理未使用的文件和全局注册。

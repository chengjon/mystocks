# ArtDeco v3/v3.1 Governance Baseline - Master Index

This document is the authoritative entry point for ArtDeco v3/v3.1 governance in the MyStocks project.

## 0. 本文档的职责

`ARTDECO_MASTER_INDEX.md` 负责的是“完整目录和定位”，不是新手上手摘要。

它主要回答：

1. 当前有哪些 ArtDeco 核心文档
2. 每份文档属于什么类别
3. 你该按什么标签去找文档

如果你是第一次接手，不要先从这里开始通读，先看：

- `ARTDECO_START_HERE.md`

然后再回到这里按标签和场景查完整目录。

## 1. 标签说明 (Reading Tags)

为减少后续接手成本，本文档给每份核心文档加上阅读标签：

- `[必读]`: 第一次接手必须先读
- `[样式真值]`: 样式、token、布局规则的事实源
- `[组件]`: 组件目录、组件开发、组件选型
- `[页面]`: 页面骨架、页面构图、页面治理
- `[架构]`: 架构口径、布局壳层、Container-Tab 体系
- `[验证]`: 测试、门禁、验证路径
- `[历史基准]`: 历史上仍有参考价值，但不是当前唯一事实源

## 1.1 优先阅读顺序

如果你是第一次接手，建议先按下面顺序读：

1. `[必读]` [ArtDeco Start Here](./ARTDECO_START_HERE.md)
2. `[样式真值]` [ArtDeco SCSS Governance Baseline](./ARTDECO_SCSS_GOVERNANCE_BASELINE.md)
3. `[架构]` [ArtDeco Fintech Unified Spec](./ARTDECO_FINTECH_UNIFIED_SPEC.md)
4. `[页面]` [ArtDeco Fintech Page Composition Audit](./ARTDECO_FINTECH_PAGE_COMPOSITION_AUDIT.md)
5. `[组件]` [ArtDeco Component Development Guide](./ARTDECO_COMPONENT_GUIDE.md)
6. `[组件]` [ArtDeco Components Catalog](../../../web/frontend/ARTDECO_COMPONENTS_CATALOG.md)

## 1.2 按任务查找

如果你不是通读，而是要马上执行任务，直接按这里找：

- 改 token / spacing / color / glow / 字体
  看 `[样式真值]` 文档
- 改页面骨架 / tabs shell / hero / layout
  看 `[页面]` 和 `[架构]` 文档
- 新增组件 / 判断组件放哪里
  看 `[组件]` 文档
- 跑验证 / 查门禁
  看 `[验证]` 文档
- 查历史背景 / 版本基准
  看 `[历史基准]` 文档

## 2. 核心设计规范 (Core Specifications)

*   **[必读][架构][样式真值] Start Here**: [ArtDeco Start Here](./ARTDECO_START_HERE.md)
    *   One-page entry document for later AI / developers: source of truth, architecture, rules, workflow, verification, and doc map.
*   **[样式真值] Design Tokens**: `web/frontend/src/styles/artdeco-tokens.scss`
    *   Primary source of truth for colors (#D4AF37), spacing, and typography (Cinzel/Barlow/JetBrains Mono).
*   **[必读][样式真值] SCSS Governance Baseline**: [ArtDeco SCSS Governance Baseline](./ARTDECO_SCSS_GOVERNANCE_BASELINE.md)
    *   Active source of truth for SCSS layering, token usage, grid usage, compatibility boundaries, and new-code rules.
*   **[必读][架构] ArtDeco Fintech Unified Spec**: [ArtDeco Fintech Unified Spec](./ARTDECO_FINTECH_UNIFIED_SPEC.md)
    *   Defines how the project inherits the original ArtDeco style and where the current fintech-oriented evolution is intentional.
*   **[架构][验证] Implementation Audit**: [ArtDeco Fintech Implementation Audit](./ARTDECO_FINTECH_IMPLEMENTATION_AUDIT.md)
    *   Tracks what has already been implemented in the active ArtDeco/Fintech runtime chain and what remains in compatibility layers.
*   **[页面][验证] Page Composition Audit**: [ArtDeco Fintech Page Composition Audit](./ARTDECO_FINTECH_PAGE_COMPOSITION_AUDIT.md)
    *   Tracks page-level ArtDeco inheritance quality, first-wave remediation results, and the next consistency priorities.
*   **[架构][历史基准] System Architecture**: [ArtDeco System Architecture Summary](../../api/ArtDeco_System_Architecture_Summary.md)
    *   Overview of the active Container-Tab hybrid architecture and base asset boundaries.
*   **[架构][历史基准] V3.1 Design Spec**: [ArtDeco Trading Center Optimized V3.1](../../api/ARTDECO_TRADING_CENTER_OPTIMIZED_V3.1.md)
    *   The latest specification for the Trading Center and V3 upgrades.
*   **[组件][历史基准] Component Catalog**: [ArtDeco Components Catalog](../../../web/frontend/ARTDECO_COMPONENTS_CATALOG.md)
    *   Governance baseline for 80+ components and Base/Domain boundaries.

## 3. 实施与指南 (Implementation & Guides)

*   **[历史基准] V3.0 Complete Summary**: [ArtDeco V3.0 Complete Summary](../../reports/ARTDECO_V3_COMPLETE_SUMMARY.md)
    *   Comprehensive summary of the V3.0 design system upgrade.
*   **[历史基准] 历史/归档**: [ArtDeco v2.0 Final Completion Report](../../reports/ARTDECO_V2_FINAL_COMPLETION_REPORT.md)
    *   Historical archive reference only, not active governance baseline.
*   **[必读][组件] Component Guide**: [ArtDeco Component Development Guide](./ARTDECO_COMPONENT_GUIDE.md)
    *   Coding standards and patterns for creating new ArtDeco components.
*   **[样式真值] Grid System**: [ArtDeco Grid Quick Reference](./ARTDECO_GRID_QUICK_REFERENCE.md)
    *   Usage guide for the responsive grid layout system (`artdeco-grid.scss`).
*   **[页面][架构] API Mapping**: [ArtDeco Menu API Mapping](./ARTDECO_MENU_API_MAPPING.md)
    *   Defines the relationship between menu items and backend API endpoints.

## 4. 页面开发与测试 (Page Development & Testing)

*   **[页面] UI/UX Functionality**: [ArtDeco UI/UX Functionality Guide](./ARTDECO_UI_UX_FUNCTIONALITY_GUIDE.md)
    *   Detailed breakdown of UI features and page-specific implementations.
*   **[验证] Integration Test Plan**: [Web Frontend ArtDeco Integration Test Plan](../../reports/WEB_FRONTEND_ARTDECO_INTEGRATION_TEST_PLAN.md)
    *   Verification strategy for components and visual consistency.

## 5. 视觉参考 (Visual References)

*   **[历史基准] Component Showcase**: [ArtDeco Component Showcase V2.md](./ART_DECO_COMPONENT_SHOWCASE_V2.md)
    *   Visual guide to component variants and rendering.
*   **[历史基准] Visual Optimization**: [ArtDeco Visual Optimization Completion Report](../../reports/ARTDECO_VISUAL_OPTIMIZATION_COMPLETION_REPORT.md)
    *   Recent updates to button heights, card ratios, and spacing.

---
**Maintenance**: All new ArtDeco documentation must be indexed here. Active guidance must stay aligned to the ArtDeco v3/v3.1 Governance Baseline. Obsolete documents are moved to `archive/docs/artdeco/`.

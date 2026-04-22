# ArtDeco V3 Complete Summary

> **历史总结说明**:
> 本文件是阶段性总结、报告、状态、修复记录、验证结果或交付回执，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内统计值、完成状态、结论、验证结果和修复结论如未重新复核，应视为历史快照，不得直接当作当前事实。


本文件不再充当“逐阶段施工日志”，而是作为两类信息的汇总基线：

1. **历史基线**：V3 初始升级给项目带来的长期有效资产。
2. **当前口径**：2026-04-01 时点 ArtDeco 文档与运行时的对齐结论。
3. **优化增量**：2026-04-19 时点在原 ArtDeco 基础上叠加的设计契约增强与运行闭环结论。

## 1. 本文档的角色

当前要理解 ArtDeco V3 / V3.1，建议这样使用本文件：

- 先看 [ARTDECO_MASTER_INDEX](/opt/claude/mystocks_spec/docs/guides/web/ARTDECO_MASTER_INDEX.md)
- 再看 [ARTDECO_FINTECH_UNIFIED_SPEC](/opt/claude/mystocks_spec/docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md)
- 需要历史背景时，再回到本文件

如果本文件与源码或活跃治理文档冲突，以 **源码 + 活跃治理文档** 为准。

## 2. 截至 2026-04-19 的当前基线

| 维度 | 当前基线 |
|------|----------|
| 设计身份 | `Original ArtDeco + A 股金融语义 + 高密度量化工作台` |
| 设计契约增强 | `DESIGN.md` 引入数据优先动效、金融 glow、紧凑密度、交易面板单主按钮、组件状态机 token |
| 主字体 | `Cinzel` / `Barlow` / `JetBrains Mono` |
| 金融颜色 | A 股强制 `红涨绿跌` |
| 间距体系 | `13` 个编号级别：`1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32` |
| Reusable assets | `73` 个 `src/components/artdeco/**` Vue 组件 |
| Page-level assets | `89` 个 `views/artdeco-pages/**` Vue 页面/块/模板 |
| Shared runtime bridge | `src/composables/useHeaderSummary.ts` |
| 运行时模式 | 模板化工作台、直接 Tab 容器、功能树驱动总控容器并存 |
| Layout 摘要模式 | Dashboard 摘要由 `useHeaderSummary -> ArtDecoLayoutEnhanced` 统一承载 |
| 路由真相 | 主业务路由以 `router/index.ts` + `views/<domain>/*.vue` 为主，保留少量 ArtDeco 例外入口 |
| 规范入口 | `ARTDECO_MASTER_INDEX` + `ARTDECO_FINTECH_UNIFIED_SPEC` + `DESIGN.md` |
| 运行验证基线 | `PM2 backend/frontend online` + stable E2E `10/10` 通过 |

## 3. 哪些 V3 资产仍然有效

以下 V3 产物仍然是当前体系的有效基础：

- 黑金品牌主色与高对比视觉语言
- `Cinzel + Barlow + JetBrains Mono` 字体组合
- ArtDeco 令牌主链
- A 股语义色
- 交易 / 风险 / 策略工作台的页面壳层思路
- 图表与数据密集页面的终端化表达方式

## 4. 自 V3 初始上线后，当前口径发生了什么变化

### 4.1 文档体系完成重组

当前活跃入口已经明确为：

- `docs/guides/web/ARTDECO_START_HERE.md`
- `docs/guides/web/ARTDECO_MASTER_INDEX.md`
- `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md`
- `DESIGN.md`
- `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md`
- `docs/api/ArtDeco_System_Architecture_Summary.md`
- `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`

### 4.1.1 兼容入口继续保留 / 补齐

以下兼容路径仍保留，用于兼容缺少 `web/` 子目录或历史命名的旧引用：

- `docs/guides/ARTDECO_MASTER_INDEX.md`
- `docs/guides/ARTDECO_FINTECH_UNIFIED_SPEC.md`
- `docs/guides/ARTDECO_COMPONENT_GUIDE.md`
- `docs/api/ARTDECO_SYSTEM_ARCHITECTURE_SUMMARY.md`

### 4.2 运行时不再是单一理想模型

当前实际运行时并非“所有页面都由单一 pageConfig + tabs 模式生成”，而是三类模式共存：

- 模板化工作台
- 直接 Tab 容器
- 功能树驱动总控容器

同时，当前还必须补充一条现实：

- 活跃业务路由已大量迁至 `views/<domain>/*.vue`
- `artdeco-pages/**` 当前同时承担工作台、模板页、域块和兼容包装层

### 4.3 组件治理不再只看“Base vs Domain”二分法

当前仓库必须同时区分：

- `src/components/artdeco/**` 的 reusable assets
- `views/artdeco-pages/components/` 的页面系统内部共享片段
- `views/artdeco-pages/*-tabs/` 的域内工作台块
- `views/<domain>/*.vue` 的 canonical routed pages

### 4.4 设计契约完成增强

在不放弃原 ArtDeco DNA 的前提下，当前设计契约新增了以下长期规则：

- 数据优先动效：价格变化采用短暂颜色闪烁
- 金融 glow 语义：盈利/亏损使用边界明确的专属 glow
- 紧凑密度模式：数据密集视图采用 4px 基线下的 compact / micro-density
- 混合过渡：数据操作 200ms，装饰反馈 400ms
- 交易面板单主按钮：降低误触和视觉竞争
- 组件状态机：`--ad-*` token 统一 default / hover / focus / error / disabled
- 共享头部摘要：Dashboard 指标提升到 Layout 级统一 header
- 品牌 chrome 收敛：header 默认 logo 文本清空，sidebar 品牌框边线移除

这些规则的当前真值位于根目录 `DESIGN.md`，不再散落在阶段报告里。

### 4.5 当前运行闭环已经补齐

截至 2026-04-19，ArtDeco 前端链路已补齐一轮实际运行验证：

- `npm run type-check`
- `npm run build:no-types`
- `PLAYWRIGHT_EXTERNAL_FRONTEND=1 npm run test:e2e:stable`
- `chromium`
- `10 passed / 0 failed / 0 skipped`
- `mystocks-backend` 与 `mystocks-frontend` 均由 PM2 在线承载

## 5. 作为“交易中心深度优化最终验收依据”时应看什么

如果后续围绕 Trading Center 或相关 ArtDeco 工作台做深度优化，本文件可作为历史基线，但验收应以以下清单为准：

1. 不破坏当前 ArtDeco 主 token 链。
2. 不新增硬编码视觉值。
3. 不把页面块错误提升为 base/core 组件。
4. 尊重当前三种运行时承载模式的边界。
5. 类型检查、服务状态、E2E 结果按实际执行结果报告，禁止复用历史固定文案。

## 6. 建议保留的里程碑时间线

| 日期 | 里程碑 |
|------|--------|
| 2026-01 | ArtDeco V3 初始升级完成，建立黑金视觉、字体与图表主题基础 |
| 2026-03 | 页面治理与样式治理文档开始成体系收敛 |
| 2026-04-01 | 文档入口、统一规格、组件目录、运行时摘要重新对齐当前代码结构 |
| 2026-04-18 | 将根级 `DESIGN.md` 并入活跃链路，补齐路由真相与 ArtDeco 工作台边界说明 |
| 2026-04-19 | 将状态机 token、共享头部摘要、品牌 chrome 收敛、稳定 E2E 运行闭环写入当前基线 |

## 7. 结论

ArtDeco V3 的价值仍然成立，但它现在更适合被理解为：

- 一个已经沉淀出稳定视觉语言的历史升级成果
- 一个需要通过统一规格和目录治理持续维持的一线工作台体系

因此，本文件的定位是 **历史基线**，而不是新的唯一事实源。

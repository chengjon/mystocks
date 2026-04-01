# ArtDeco Master Index

本文件是 MyStocks 项目 ArtDeco 文档体系的唯一总目录，负责回答三件事：

1. 当前哪些文档是活跃治理文档。
2. 每份文档的职责边界是什么。
3. 遇到具体任务时应该先读哪一份。

> 2026-04-01 文档治理刷新
>
> - 修正旧链路中的失效路径与缺失入口。
> - 补齐 `ARTDECO_FINTECH_UNIFIED_SPEC.md`。
> - 为历史上缺少 `web/` 子目录的两条常用路径提供兼容入口。

## 1. 文档分层

### 1.1 活跃治理文档

| 标签 | 文档 | 职责 |
|------|------|------|
| `[必读]` | [ARTDECO_START_HERE](./ARTDECO_START_HERE.md) | 单页上手入口，给第一次接手的人最短阅读路径 |
| `[必读][架构]` | [ARTDECO_FINTECH_UNIFIED_SPEC](./ARTDECO_FINTECH_UNIFIED_SPEC.md) | 当前 ArtDeco Fintech 的统一规格：设计身份、目录边界、运行时承载模式 |
| `[必读][样式真值]` | [ARTDECO_SCSS_GOVERNANCE_BASELINE](./ARTDECO_SCSS_GOVERNANCE_BASELINE.md) | 令牌、Grid、兼容层、样式导入规范的事实源 |
| `[必读][组件]` | [ARTDECO_COMPONENT_GUIDE](./ARTDECO_COMPONENT_GUIDE.md) | 组件目录治理、`*-tabs` 铁律、放置决策树 |
| `[组件][目录]` | [ARTDECO_COMPONENTS_CATALOG](../../../web/frontend/ARTDECO_COMPONENTS_CATALOG.md) | 当前组件全景目录，覆盖 reusable assets 与 page-level workbench blocks |
| `[页面][模板]` | [ARTDECO_PAGE_TEMPLATE_GUIDE](./ARTDECO_PAGE_TEMPLATE_GUIDE.md) | 模板化工作台页面的承载方式 |
| `[页面][验证]` | [ARTDECO_FINTECH_PAGE_COMPOSITION_AUDIT](./ARTDECO_FINTECH_PAGE_COMPOSITION_AUDIT.md) | 页面骨架、一致性与工作台化收敛的审计记录 |
| `[验证]` | [ARTDECO_FINTECH_IMPLEMENTATION_AUDIT](./ARTDECO_FINTECH_IMPLEMENTATION_AUDIT.md) | 活跃实现与统一规格的对账文档 |

### 1.2 运行时与历史基准文档

| 标签 | 文档 | 职责 |
|------|------|------|
| `[架构][运行时摘要]` | [ArtDeco_System_Architecture_Summary](../../api/ArtDeco_System_Architecture_Summary.md) | 从 Vue 路由、容器模式、组件边界角度总结当前运行时 |
| `[历史基准]` | [ARTDECO_V3_COMPLETE_SUMMARY](../../reports/ARTDECO_V3_COMPLETE_SUMMARY.md) | V3 升级过程与后续治理刷新之间的历史基准 |

### 1.3 兼容入口

以下两个入口保留是为了兼容历史报告、审核记录和外部引用；真实内容仍在 `docs/guides/web/`：

| 兼容路径 | 指向 |
|----------|------|
| [docs/guides/ARTDECO_MASTER_INDEX.md](/opt/claude/mystocks_spec/docs/guides/ARTDECO_MASTER_INDEX.md) | `docs/guides/web/ARTDECO_MASTER_INDEX.md` |
| [docs/guides/ARTDECO_COMPONENT_GUIDE.md](/opt/claude/mystocks_spec/docs/guides/ARTDECO_COMPONENT_GUIDE.md) | `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md` |

## 2. 推荐阅读顺序

如果你是第一次接手 ArtDeco：

1. [ARTDECO_START_HERE](./ARTDECO_START_HERE.md)
2. [ARTDECO_FINTECH_UNIFIED_SPEC](./ARTDECO_FINTECH_UNIFIED_SPEC.md)
3. [ARTDECO_SCSS_GOVERNANCE_BASELINE](./ARTDECO_SCSS_GOVERNANCE_BASELINE.md)
4. [ARTDECO_COMPONENT_GUIDE](./ARTDECO_COMPONENT_GUIDE.md)
5. [ArtDeco_System_Architecture_Summary](../../api/ArtDeco_System_Architecture_Summary.md)
6. [ARTDECO_COMPONENTS_CATALOG](../../../web/frontend/ARTDECO_COMPONENTS_CATALOG.md)

## 3. 按任务找文档

| 任务 | 优先文档 |
|------|----------|
| 判断当前 ArtDeco 到底是什么 | `ARTDECO_START_HERE.md` |
| 判断“现在该按什么规则实现” | `ARTDECO_FINTECH_UNIFIED_SPEC.md` |
| 改 token / 字体 / 间距 / glow / Grid | `ARTDECO_SCSS_GOVERNANCE_BASELINE.md` |
| 判断组件放哪里 | `ARTDECO_COMPONENT_GUIDE.md` |
| 查现有组件与页面块存量 | `web/frontend/ARTDECO_COMPONENTS_CATALOG.md` |
| 理解页面模板与工作台壳层 | `ARTDECO_PAGE_TEMPLATE_GUIDE.md` |
| 理解当前运行时架构 | `ArtDeco_System_Architecture_Summary.md` |
| 查历史基线与升级背景 | `ARTDECO_V3_COMPLETE_SUMMARY.md` |
| 查实现/页面是否已治理到位 | `ARTDECO_FINTECH_IMPLEMENTATION_AUDIT.md` / `ARTDECO_FINTECH_PAGE_COMPOSITION_AUDIT.md` |

## 4. 当前目录口径

当前 ArtDeco 文档体系按三层理解：

1. **治理层**
   `START_HERE`、`UNIFIED_SPEC`、`SCSS_GOVERNANCE_BASELINE`、`COMPONENT_GUIDE`
2. **运行时与目录层**
   `COMPONENTS_CATALOG`、`System_Architecture_Summary`、`PAGE_TEMPLATE_GUIDE`
3. **验证与历史层**
   `FINTECH_IMPLEMENTATION_AUDIT`、`FINTECH_PAGE_COMPOSITION_AUDIT`、`V3_COMPLETE_SUMMARY`

## 5. 不再作为当前唯一事实源的文档

以下文档仍可保留为历史参考，但不应作为新实现的直接规范：

- `ART_DECO_COMPONENT_SHOWCASE*.md`
- `mystocks-artdeco-available-components.md`
- 各类早期 ArtDeco 设计展示、阶段报告、迁移笔记

判断原则：

- 能决定“现在怎么写”的，只能是活跃治理文档和源码。
- 历史文档用来理解背景，不用来覆盖当前真值。

## 6. 维护规则

- 新增 ArtDeco 文档时，必须先判断它属于治理层、运行时层还是历史层，再回填到本索引。
- 如果文档职责变了，先改本索引，再改文档正文。
- 如果文档路径变了，必须保留兼容入口或同步修正所有上游引用。
- 当 `web/frontend/src/styles/artdeco-tokens.scss`、`web/frontend/src/views/artdeco-pages/**`、`web/frontend/src/components/artdeco/**` 的结构发生变化时，至少同步更新：
  - 本索引
  - `ARTDECO_FINTECH_UNIFIED_SPEC.md`
  - `ARTDECO_COMPONENTS_CATALOG.md`
  - `ArtDeco_System_Architecture_Summary.md`

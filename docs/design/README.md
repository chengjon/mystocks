# MyStocks 设计资料目录

**定位**: 设计规范、设计工具说明、HTML 原型样例、分阶段优化方案  
**状态**: 特殊保留目录  
**最后更新**: 2026-03-23

---

## 目录说明

`docs/design/` 当前不是普通的指南目录，也不适合直接并入单一目标家族。它同时承载：

- 设计规范文档
- Figma / Pixso / Sketch 工具说明
- HTML 样例与原型资源
- Web 设计更新方案与阶段性技术指南
- 设计相关静态资源（如 `design-tokens.json`、自动化脚本）

因此本目录当前按“特殊保留目录”管理，后续若要继续分流，应按子类分别处理，而不是整目录机械迁移。

---

## 当前结构

```text
docs/design/
├── README.md
├── INDEX.md
├── 20251121-spec优化建议.md
├── ARTDECO_CONVERSION_OPTIMIZATION_PROPOSAL.md
├── AUTOMATION_GUIDE.md
├── COMPONENT_LIBRARY_SPECIFICATION.md
├── FIGMA_QUICK_START.md
├── MYSTOCKS_DESIGN_SPECIFICATION.md
├── PIXSO_IMPORT_GUIDE.md
├── SKETCH_MANUAL_GUIDE.md
├── design-tokens.json
├── figma-automation-script.js
├── grok_advice.md
├── html_sample/
├── new/
└── update/
```

---

## 推荐阅读顺序

### 了解总体设计规范

1. [MYSTOCKS_DESIGN_SPECIFICATION.md](./MYSTOCKS_DESIGN_SPECIFICATION.md)
2. [COMPONENT_LIBRARY_SPECIFICATION.md](./COMPONENT_LIBRARY_SPECIFICATION.md)
3. [20251121-spec优化建议.md](./20251121-spec优化建议.md)

### 使用设计工具与导入流程

1. [FIGMA_QUICK_START.md](./FIGMA_QUICK_START.md)
2. [PIXSO_IMPORT_GUIDE.md](./PIXSO_IMPORT_GUIDE.md)
3. [AUTOMATION_GUIDE.md](./AUTOMATION_GUIDE.md)
4. [SKETCH_MANUAL_GUIDE.md](./SKETCH_MANUAL_GUIDE.md)

### 查看页面原型与分阶段方案

1. [new/index.md](./new/index.md)
2. [html_sample/README.md](./html_sample/README.md)
3. [update/执行摘要_四阶段优化方案.md](./update/执行摘要_四阶段优化方案.md)

---

## 子目录定位

### `new/`

承载较新的页面级设计稿与页面说明，包括仪表盘、行情中心、选股池、回测、交易台、风险中心等。

入口：

- [new/index.md](./new/index.md)

### `html_sample/`

承载 HTML 原型、样例页面和打包示例，适合作为视觉参考和快速比对资源。

入口：

- [html_sample/README.md](./html_sample/README.md)

### `update/`

承载面向实施的阶段性设计/优化方案，主要是 Web 功能优化的执行摘要与技术实施指南。

入口：

- [update/执行摘要_四阶段优化方案.md](./update/执行摘要_四阶段优化方案.md)

---

## 设计资料与其他家族的关系

- 若文档主要描述系统架构决策，应优先放入 `docs/architecture/`
- 若文档主要作为长期参考资料，应优先放入 `docs/references/`
- 若文档主要是阶段性执行计划或批次安排，应优先放入 `docs/plans/`
- 若内容为设计资产、原型样例、设计工具说明，则当前保留在 `docs/design/`

---

## 维护说明

在继续整理本目录之前，建议先按以下四类做子级盘点：

1. 设计规范类 Markdown
2. 工具说明类 Markdown
3. HTML / JSON / JS 设计资产
4. 分阶段更新方案

只有完成这层拆分后，才适合进一步迁移。

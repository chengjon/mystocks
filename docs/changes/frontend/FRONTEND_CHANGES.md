# Frontend Changes Index

> 前端手工测试与 UI 修改的入口文档。记录工作流规范，索引链接到具体主题文档。

**目录**: `docs/changes/frontend/`
**入口**: 本文件
**起始日期**: 2026-04-19

---

## 工作流规范

每次修改必须遵循以下流程：

### 1. 修改要求

由用户在手工测试过程中提出，描述要修改的页面、元素和期望效果。

### 2. AI 修改方式

AI 接收要求后，定位文件、确定修改范围、执行最小变更。

### 3. 修改后审核

每个修改点必须附带以下元数据块：

```
【修改要求】用户提出的具体需求
【AI 修改方式】AI 采取了什么方法、改了哪些文件的哪些位置
【回归风险点】改了会影响哪些其他页面/组件
【回归检查项】必须检查哪几个地方验证没坏
【后端是否受影响】是/否，影响点是什么
```

### 4. 外部评审响应

如收到外部评审意见（Findings），需逐条分析并记录结论：
- 是否为本次修改引入的回归
- 是否为预存问题
- 具体影响范围与证据

---

## 修改记录索引

| 日期 | 主题 | 文档 |
|------|------|------|
| 2026-04-19 | Dashboard 首行 Header 平移与样式调整 | [20260419-dashboard-header.md](./frontend_changes/20260419-dashboard-header.md) |

---

## 涉及文件范围（累计）

所有修改涉及的文件汇总（去重）：

| 文件 | 首次修改日期 |
|------|-------------|
| `src/components/artdeco/trading/ArtDecoCollapsibleSidebar.vue` | 2026-04-19 |
| `src/composables/useHeaderSummary.ts` | 2026-04-19 |
| `src/views/artdeco-pages/composables/useArtDecoDashboard.ts` | 2026-04-19 |
| `src/layouts/ArtDecoLayoutEnhanced.vue` | 2026-04-19 |
| `src/components/artdeco/core/ArtDecoHeader.vue` | 2026-04-19 |
| `src/views/artdeco-pages/ArtDecoDashboard.vue` | 2026-04-19 |

文件路径相对于 `web/frontend/`。

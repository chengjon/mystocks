# PIXSO MCP（pixso-desktop）工具总览 — 9 个工具

本文件整理并简要介绍用于 pixso-desktop MCP 的 9 个工具。每个工具均可针对指定节点（通过 itemId）或当前选中节点执行相关操作。若工具支持从页面 URL 提取 itemId，示例 URL：

> https://any-host/app/design/:fileName?item-id=1:2 -> itemId = `1:2`

## 快速索引

1. getCode — 生成 UI 代码
2. getImage — 生成节点图片
3. getNodeDSL — 生成节点 DSL
4. getVariants — 获取节点的 variants
5. getVariableSets — 获取所有变量集
6. getVariables — 获取某变量集下的所有变量
7. getExportImage — 导出节点图片（带导出设置）
8. getLocalStyles — 获取本地样式
9. getRemoteStyles — 获取远程样式

---

## 工具详解

### 1. getCode
- Full name: `mcp__pixso-desktop__getCode`
- 描述：为指定节点或当前选中节点生成 UI 代码。可用于前端框架适配与开发者导出。
- 常见用法：传入 `itemId` 指定节点；若省略则使用当前选中项；也可传入页面 URL，从中提取 `itemId`。
- 参数：
	- `itemId` (string) — 节点 ID，例如 `"123:456"`。
	- `clientFrameworks` (string) — 逗号分隔的目标框架列表，例如 `arkui,flutter,html`。用于埋点/日志，不确定时可填 `html`。

### 2. getImage
- Full name: `mcp__pixso-desktop__getImage`
- 描述：为指定节点或当前选中节点生成位图（PNG 等）。
- 参数：
	- `itemId` (string) — 节点 ID，如 `"123:456"`。
	- `clientFrameworks` (string) — 可选，参见 `getCode`。

### 3. getNodeDSL
- Full name: `mcp__pixso-desktop__getNodeDSL`
- 描述：生成节点对应的 DSL（结构化描述），用于分析或再处理。
- 参数：
	- `itemId` (string) — 节点 ID，如 `"123:456"`。
	- `clientFrameworks` (string) — 可选，参见 `getCode`。

### 4. getVariants
- Full name: `mcp__pixso-desktop__getVariants`
- 描述：获取节点的 variants（变体），常用于组件库或多状态展示。
- 参数：
	- `itemId` (string) — 节点 ID，如 `"123:456"`。

### 5. getVariableSets
- Full name: `mcp__pixso-desktop__getVariableSets`
- 描述：获取当前文档或项目中所有的变量集合（variable sets），用于主题或配置管理。
- 参数：无（按实现可能返回列表）。

### 6. getVariables
- Full name: `mcp__pixso-desktop__getVariables`
- 描述：获取指定变量集合下的所有变量。
- 参数：
	- `variableSetId` (string) — 变量集合 ID，例如 `"123:456"`。

### 7. getExportImage
- Full name: `mcp__pixso-desktop__getExportImage`
- 描述：按导出设置导出节点图片（用于截图、资源导出等）。与 `getImage` 类似，但支持更丰富的导出参数。
- 参数：
	- `itemId` (string) — 节点 ID，如 `"123:456"`。
	- `exportSettings` (object, required) — 导出配置，例如尺寸、格式、背景等。

### 8. getLocalStyles
- Full name: `mcp__pixso-desktop__getLocalStyles`
- 描述：获取当前文档或页面中定义的本地样式（颜色、文字样式、效果等）。
- 参数：无（按实现返回样式集合）。

### 9. getRemoteStyles
- Full name: `mcp__pixso-desktop__getRemoteStyles`
- 描述：获取远程样式库中的样式（如共享样式、设计系统样式）。
- 参数：无（按实现返回样式集合）。

---

## 使用提示

- 当传入 URL 时，工具会尝试从 URL 中解析 `item-id` 参数并作为 `itemId` 使用。
- 对于 `clientFrameworks`，该字段主要用于日志和适配提示，不会影响核心数据；不确定时建议使用 `html`。
- `getExportImage` 的 `exportSettings` 通常必需，请参考具体实现（例如：宽度、高度、缩放、背景、格式）。




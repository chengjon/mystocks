# Sketch 手动创建指南

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


> 如果您有 macOS 系统和 Sketch 软件，可按此指南手动创建设计文件

## 前提条件

- ✅ macOS 系统
- ✅ Sketch 软件（付费，约 $99/年）
- ✅ 已阅读 `MYSTOCKS_DESIGN_SPECIFICATION.md` 和 `COMPONENT_LIBRARY_SPECIFICATION.md`

---

## 步骤 1: 创建新文档

1. 打开 Sketch
2. File → New (Cmd+N)
3. 命名: "MyStocks Web Design"
4. 保存位置: `/opt/claude/mystocks_spec/docs/design/MyStocks.sketch`

---

## 步骤 2: 设置文档颜色

### 2.1 打开颜色管理

```
View → Show Components
→ 左侧面板 → Colors
→ 点击 "+" 添加新颜色
```

### 2.2 添加主色调

从 `design-tokens.json` 中复制颜色值:

| 颜色名称 | Hex | 用途 |
|---------|-----|------|
| Primary/Blue | #409EFF | 主品牌色 |
| Success/Green | #67C23A | 成功、上涨 |
| Danger/Red | #F56C6C | 错误、下跌 |
| Warning/Orange | #E6A23C | 警告 |
| Info/Gray | #909399 | 信息 |

**操作**:
```
1. 点击颜色 → 输入 Hex 值 #409EFF
2. 命名: "Primary/Blue"
3. 点击 "Create Color Variable"
4. 重复以上步骤添加所有颜色
```

### 2.3 添加金融专用色

| 颜色名称 | Hex | 用途 |
|---------|-----|------|
| Financial/Up-Limit | #FF3333 | 涨停红 |
| Financial/Up | #F56C6C | 上涨红 |
| Financial/Flat | #909399 | 平盘灰 |
| Financial/Down | #67C23A | 下跌绿 |
| Financial/Down-Limit | #00CC00 | 跌停绿 |

### 2.4 添加背景色

| 颜色名称 | Hex | 用途 |
|---------|-----|------|
| Background/Page | #F5F7FA | 页面底色 |
| Background/Card | #FFFFFF | 卡片背景 |
| Background/Table-Stripe | #FAFAFA | 表格斑马纹 |
| Background/Hover | #F5F7FA | 悬停背景 |
| Background/Selected | #ECF5FF | 选中背景 |

---

## 步骤 3: 设置文本样式

### 3.1 打开文本样式管理

```
View → Show Components
→ 左侧面板 → Text Styles
→ 点击 "+" 添加新样式
```

### 3.2 创建标题样式

从 `design-tokens.json` 的 `fontSize` 和 `lineHeight` 中获取值:

**Heading/XL**:
```
1. 创建文本框 (T键)
2. 字体: PingFang SC / Microsoft YaHei
3. 字号: 28px
4. 行高: 36px
5. 字重: Semibold (600)
6. 颜色: Text/Primary (#303133)
7. 右侧面板 → Appearance → Create Text Style
8. 命名: "Heading/XL"
```

**需要创建的文本样式**:

| 样式名称 | 字号 | 行高 | 字重 | 颜色 |
|---------|------|------|------|------|
| Heading/XL | 28px | 36px | 600 | #303133 |
| Heading/L | 24px | 32px | 600 | #303133 |
| Heading/M | 20px | 28px | 500 | #303133 |
| Heading/S | 18px | 26px | 500 | #303133 |
| Body/Regular | 14px | 22px | 400 | #606266 |
| Body/Secondary | 14px | 22px | 400 | #909399 |
| Caption | 13px | 20px | 400 | #909399 |
| Small | 12px | 18px | 400 | #C0C4CC |

### 3.3 创建数字样式（等宽字体）

**Number/Large**:
```
1. 字体: SF Mono / Monaco / Consolas
2. 字号: 32px
3. 行高: 40px
4. 字重: 500
5. 命名: "Number/Large"
```

| 样式名称 | 字号 | 行高 | 字重 | 字体 |
|---------|------|------|------|------|
| Number/Large | 32px | 40px | 500 | Monospace |
| Number/Medium | 20px | 28px | 500 | Monospace |
| Number/Small | 14px | 22px | 400 | Monospace |

---

## 步骤 4: 创建按钮组件

### 4.1 创建基础按钮

参考 `COMPONENT_LIBRARY_SPECIFICATION.md` 的 MyButton 规范:

```
1. 创建矩形 (R键)
   - 宽度: 自动 (Auto)
   - 高度: 32px (Default size)
   - 填充: Primary/Blue (#409EFF)
   - 圆角: 4px (来自 design-tokens.json borderRadius.default)

2. 添加文本
   - 文本: "按钮文字"
   - 样式: Body/Regular
   - 颜色: White (#FFFFFF)
   - 内边距: 12px 20px (来自 design-tokens.json component.button.padding.default)

3. 选中矩形和文本
   - Layer → Create Symbol (Cmd+Y)
   - 命名: "Button/Primary/Default"
```

### 4.2 创建按钮变体

**尺寸变体** (来自 design-tokens.json):

| 尺寸 | 高度 | 内边距 |
|------|------|--------|
| Large | 40px | 20px 15px |
| Default | 32px | 12px 20px |
| Small | 28px | 9px 15px |

**类型变体**:

| 类型 | 背景色 | 文本色 | 边框 |
|------|--------|--------|------|
| Primary | #409EFF | #FFFFFF | 无 |
| Success | #67C23A | #FFFFFF | 无 |
| Warning | #E6A23C | #FFFFFF | 无 |
| Danger | #F56C6C | #FFFFFF | 无 |
| Info | #909399 | #FFFFFF | 无 |
| Default | #FFFFFF | #606266 | 1px #DCDFE6 |

**创建 Symbol 变体**:
```
1. 复制基础按钮 5 次
2. 修改每个副本的颜色
3. 全选所有按钮
4. Layer → Create Symbol
5. 在 Symbol 面板中右键 → "Organize Symbols"
6. 创建文件夹: Button/Primary, Button/Success, etc.
```

---

## 步骤 5: 创建  组件

参考 `COMPONENT_LIBRARY_SPECIFICATION.md` 的  规范:

### 5.1 基础结构

```
1. 创建文本框: "12.34"
   - 字体: Number/Small (14px, Monospace)
   - 颜色: Financial/Up (#F56C6C)

2. 添加图标 (可选)
   - 使用 Sketch 内置图标或 SF Symbols
   - 三角形向上 ▲ (上涨)
   - 三角形向下 ▼ (下跌)
   - 横线 — (平盘)

3. 添加涨跌幅文本 (可选): "(+2.50%)"
   - 字体: Caption (12px)
   - 颜色: 与主数值相同
   - 透明度: 80%

4. 组合成组
   - 水平排列: 图标 - 数值 - 涨跌幅
   - 间距: 4px (来自 design-tokens.json spacing.xs)

5. 创建 Symbol
   - 命名: "/Up/Default"
```

### 5.2 创建涨跌变体

| 变体 | 颜色 | 图标 |
|------|------|------|
| Up | #F56C6C (红) | ▲ |
| Down | #67C23A (绿) | ▼ |
| Flat | #909399 (灰) | — |

### 5.3 创建尺寸变体

| 尺寸 | 数值字号 | 涨跌幅字号 |
|------|---------|-----------|
| Large | 20px | 14px |
| Default | 14px | 12px |
| Small | 12px | 11px |

---

## 步骤 6: 创建 StockCard 组件

参考 `COMPONENT_LIBRARY_SPECIFICATION.md` 的 StockCard 规范:

### 6.1 卡片容器

```
1. 创建矩形
   - 宽度: 360px
   - 高度: 自动 (Auto)
   - 填充: Background/Card (#FFFFFF)
   - 圆角: 8px (来自 design-tokens.json borderRadius.medium)
   - 阴影: 0 2px 4px rgba(0,0,0,0.05)
   - 内边距: 16px (来自 design-tokens.json spacing.lg)
```

### 6.2 内容结构

```
卡片内容 (从上到下):

1. Header (股票信息 + 标签)
   ├─ 左侧
   │  ├─ 股票代码: "000001" (Heading/M, #303133)
   │  └─ 股票名称: "平安银行" (Body/Regular, #606266)
   └─ 右侧
      └─ 标签: "银行" "蓝筹" (el-tag small)

2. Price (当前价格)
   └─  组件
      ├─ size: large
      ├─ show-icon: true
      └─ show-change: true

3. Metrics (指标网格)
   ├─ 涨跌额:
   ├─ 成交量: "123.45万"
   └─ 换手率: "1.23%"

4. Actions (操作按钮)
   ├─ 自选按钮 (Button/Default/Small + Star图标)
   └─ 详情按钮 (Button/Primary/Small)
```

### 6.3 布局间距

```
- Header 下边距: 12px (spacing.md)
- Price 下边距: 12px
- Metrics 上边距: 12px (分隔线)
- Metrics 列间距: 12px
- Actions 上边距: 12px (分隔线)
- Actions 按钮间距: 8px (spacing.sm)
```

### 6.4 创建 Symbol

```
1. 全选卡片所有元素
2. Layer → Create Symbol (Cmd+Y)
3. 命名: "StockCard/Default"
4. 设置可编辑属性:
   - 股票代码 (text override)
   - 股票名称 (text override)
   - 当前价格 (text override)
   - 涨跌幅 (text override)
   - 成交量 (text override)
   - 换手率 (text override)
```

---

## 步骤 7: 创建表格组件

参考 `MYSTOCKS_DESIGN_SPECIFICATION.md` 的表格规范:

### 7.1 表格头部

```
1. 创建矩形
   - 宽度: 1200px
   - 高度: 48px (来自 design-tokens.json component.table.row-height.default)
   - 填充: Background/Table-Stripe (#FAFAFA)
   - 边框底部: 1px solid #DCDFE6

2. 添加列标题文本
   | 股票代码 | 股票名称 | 当前价 | 涨跌幅 | 成交量 | 操作 |

   - 字体: Body/Regular (14px, #606266)
   - 字重: Medium (500)
   - 水平对齐: 左对齐 (数值列右对齐)
   - 内边距: 12px (spacing.md)
```

### 7.2 表格行

```
1. 创建普通行
   - 高度: 48px
   - 填充: #FFFFFF
   - 边框底部: 1px solid #E4E7ED

2. 创建斑马纹行
   - 高度: 48px
   - 填充: #FAFAFA
   - 边框底部: 1px solid #E4E7ED

3. 创建悬停行
   - 高度: 48px
   - 填充: #F5F7FA (Background/Hover)
   - 边框底部: 1px solid #E4E7ED

4. 创建选中行
   - 高度: 48px
   - 填充: #ECF5FF (Background/Selected)
   - 边框底部: 1px solid #409EFF
```

### 7.3 单元格内容

```
- 文本单元格: Body/Regular, #606266
- 数值单元格: 使用  组件
- 操作单元格: Button/Text/Small
- 单元格内边距: 12px
```

### 7.4 组合成 Symbol

```
1. 组合表格头 + 5行示例数据
2. Layer → Create Symbol
3. 命名: "Table/Stock/Default"
```

---

## 步骤 8: 创建完整页面模板

参考 `MYSTOCKS_DESIGN_SPECIFICATION.md` 的页面模板:

### 8.1 仪表盘页面

```
1. 创建 Artboard
   - 名称: "Dashboard"
   - 尺寸: 1920 x 1080

2. 布局结构:
   ┌────────────────────────────────────────┐
   │ Header (60px)                          │
   ├────────┬───────────────────────────────┤
   │ Sidebar│ Main Content                  │
   │ (200px)│ ┌─────────────────────────┐  │
   │        │ │ Stats Cards (4列)       │  │
   │        │ └─────────────────────────┘  │
   │        │ ┌─────────────────────────┐  │
   │        │ │ Charts (2/3 + 1/3)      │  │
   │        │ └─────────────────────────┘  │
   │        │ ┌─────────────────────────┐  │
   │        │ │ Stock Table             │  │
   │        │ └─────────────────────────┘  │
   └────────┴───────────────────────────────┘

3. 使用已创建的组件:
   - Header: 使用 el-header 组件
   - Sidebar: 使用 el-menu 组件
   - Stats Cards: 使用 StockCard 组件
   - Table: 使用 Table/Stock 组件
```

### 8.2 数据列表页

```
1. 创建 Artboard
   - 名称: "Stock List"
   - 尺寸: 1920 x 1080

2. 布局结构:
   - 页面标题 + 面包屑 (60px)
   - 查询表单卡片 (80px)
   - 数据表格卡片 (Auto)
   - 分页器 (40px)

3. 间距:
   - 外边距: 20px (spacing.xl)
   - 卡片间距: 20px
   - 内边距: 16px (spacing.lg)
```

---

## 步骤 9: 导出 Sketch 文件

### 9.1 组织图层

```
1. 整理 Pages:
   - 📁 Colors & Styles (颜色和样式定义)
   - 📁 Components (所有组件 Symbols)
   - 📁 Pages (页面模板)

2. 整理 Symbols:
   Button/
   ├─ Primary/
   │  ├─ Large
   │  ├─ Default
   │  └─ Small
   ├─ Success/
   └─ ...

   /
   ├─ Up/
   ├─ Down/
   └─ Flat/

   StockCard/
   └─ Default

   Table/
   └─ Stock/
```

### 9.2 保存文件

```
1. File → Save (Cmd+S)
2. 文件名: "MyStocks_Design_v1.0.sketch"
3. 保存路径: /opt/claude/mystocks_spec/docs/design/
```

### 9.3 导出为 Pixso 兼容格式

```
1. File → Export → Export...
2. 选择导出选项:
   - Format: Sketch (.sketch)
   - Include: All pages, symbols, and color variables
   - Version: Latest Sketch format

3. 点击 "Export"
```

---

## 步骤 10: 导入到 Pixso

### 10.1 登录 Pixso

```
1. 访问: https://pixso.cn
2. 登录账号
3. 进入工作台
```

### 10.2 导入 Sketch 文件

```
1. 点击 "导入" 按钮
2. 选择 "从本地导入"
3. 文件类型: Sketch (.sketch)
4. 选择文件: MyStocks_Design_v1.0.sketch
5. 点击 "开始导入"
6. 等待导入完成（约 2-5 分钟）
```

### 10.3 验证导入结果

检查以下内容是否正确导入:

- ✅ 颜色样式 (所有颜色变量)
- ✅ 文本样式 (所有字体样式)
- ✅ 组件库 (Buttons, , StockCard, Table)
- ✅ 页面模板 (Dashboard, Stock List)
- ✅ 图层结构 (文件夹组织)

---

## 常见问题

### Q1: Sketch 文件太大怎么办？

**A**: 优化建议:
- 删除未使用的 Symbols
- 压缩图片资源
- 使用 Sketch 插件: "Sketch Cleaner"

### Q2: 导入 Pixso 后样式丢失？

**A**: 可能原因:
- 字体缺失 → 在 Pixso 中重新设置字体
- 颜色变量未转换 → 手动重新创建颜色样式
- 组件嵌套过深 → 简化组件层级

### Q3: 无法安装 Sketch 怎么办？

**A**: 使用 Figma 替代方案:
- Figma 完全免费
- 与 Pixso 100% 兼容
- 跨平台支持
- 参见: `PIXSO_IMPORT_GUIDE.md`

---

## 参考文档

- `MYSTOCKS_DESIGN_SPECIFICATION.md` - 完整设计规范
- `COMPONENT_LIBRARY_SPECIFICATION.md` - 组件库详细定义
- `design-tokens.json` - 设计 Token 数据
- `PIXSO_IMPORT_GUIDE.md` - Pixso 导入通用指南

---

**预计完成时间**: 4-6 小时（取决于设计经验）
**技能要求**: 熟悉 Sketch 软件基本操作
**推荐难度**: ⭐⭐⭐☆☆ (中等)

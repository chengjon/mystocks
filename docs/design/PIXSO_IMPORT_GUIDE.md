# Pixso 设计导入完整指南

**文档版本**: v1.0
**创建日期**: 2025-11-09
**适用范围**: MyStocks Web 设计方案导入 Pixso

---

## 📋 目录

1. [Pixso 支持的导入格式](#1-pixso-支持的导入格式)
2. [推荐导入方案](#2-推荐导入方案)
3. [使用 Figma 创建设计并导入](#3-使用-figma-创建设计并导入)
4. [使用 Sketch 创建设计并导入](#4-使用-sketch-创建设计并导入)
5. [直接在 Pixso 中创建设计](#5-直接在-pixso-中创建设计)
6. [设计 Token 的应用](#6-设计-token-的应用)
7. [常见问题](#7-常见问题)

---

## 1. Pixso 支持的导入格式

根据 [Pixso 官方文档](https://pixso.cn/help/guide/8/1660225022876517),Pixso 支持以下文件格式导入:

### 1.1 设计工具文件

| 格式 | 工具 | 支持版本 | 推荐度 | 说明 |
|------|------|---------|--------|------|
| **.fig** | Figma | 所有版本 | ⭐⭐⭐⭐⭐ | **最佳选择**,100%兼容性 |
| **.sketch** | Sketch | 43+ | ⭐⭐⭐⭐ | Mac端设计工具,兼容性好 |
| **.xd** | Adobe XD | CC 2018+ | ⭐⭐⭐ | Adobe设计工具 |
| **.psd** | Photoshop | CC+ | ⭐⭐ | 转换为图层,部分功能丢失 |
| **.ai** | Illustrator | CC+ | ⭐⭐ | 矢量图形,部分功能丢失 |

### 1.2 图片格式

| 格式 | 说明 | 推荐使用场景 |
|------|------|-------------|
| PNG | 支持透明背景 | 图标、UI元素 |
| JPG | 不支持透明 | 照片、背景图 |
| SVG | 矢量图形 | 图标、Logo |
| GIF | 动画 | 不推荐 (不支持动画) |

### 1.3 不支持的格式

❌ **编程生成的文件**:
- JSON (设计Token)
- HTML/CSS
- React/Vue 组件
- 代码生成的 UI

---

## 2. 推荐导入方案

### 方案对比

| 方案 | 工具链 | 难度 | 时间成本 | 推荐指数 |
|------|--------|------|---------|---------|
| **A. Figma → Pixso** | Figma (Web) → 导出.fig → Pixso导入 | ⭐ | 快 (1小时) | ⭐⭐⭐⭐⭐ |
| **B. Sketch → Pixso** | Sketch (Mac) → 导出.sketch → Pixso导入 | ⭐⭐ | 中 (2小时) | ⭐⭐⭐⭐ |
| **C. 直接在Pixso创建** | Pixso (Web) | ⭐ | 慢 (4小时) | ⭐⭐⭐ |
| **D. Pixso插件** | Figma Plugin → Pixso同步 | ⭐ | 极快 (10分钟) | ⭐⭐⭐⭐⭐ |

### 最佳推荐: **方案 A (Figma → Pixso)**

**理由**:
1. ✅ **免费**: Figma 免费版功能完整
2. ✅ **跨平台**: Web端,无需安装
3. ✅ **兼容性**: .fig 格式100%兼容Pixso
4. ✅ **生态丰富**: Element Plus 有现成的 Figma 组件库

---

## 3. 使用 Figma 创建设计并导入

### 3.1 准备工作

#### 3.1.1 注册 Figma 账号

1. 访问 https://www.figma.com
2. 点击 "Sign up" 注册账号
3. 选择免费版 (Free Plan) - 足够使用

#### 3.1.2 安装 Element Plus Figma 组件库

1. 在 Figma 中打开 Community
2. 搜索 "Element Plus UI Kit"
3. 点击 "Duplicate" 复制到你的账号

**推荐资源**:
- **Element Plus UI Kit**: https://www.figma.com/community/file/[搜索: Element Plus]
- **Ant Design**: https://www.figma.com/community/file/831698976089873405
- **通用Dashboard模板**: 搜索 "Admin Dashboard Template"

### 3.2 创建 MyStocks 设计文件

#### 步骤 1: 新建 Figma 文件

```
1. 点击 "New design file"
2. 命名为: "MyStocks Web Design"
3. 设置画板尺寸: 1920 x 1080 (桌面端)
```

#### 步骤 2: 导入设计 Token

1. 安装 Figma 插件: **Tokens Studio**
   - 菜单 → Plugins → Browse plugins → 搜索 "Tokens Studio"

2. 导入 `design-tokens.json` 文件
   ```
   Plugins → Tokens Studio → Load from file → 选择 design-tokens.json
   ```

3. 应用 Token 到设计系统
   ```
   Tokens Studio → Apply to styles
   ```

#### 步骤 3: 创建基础组件库

**基于设计规范文档** (`MYSTOCKS_DESIGN_SPECIFICATION.md`):

##### 3.1 颜色样式

```
1. 选中任意矩形
2. 填充颜色: #409EFF
3. 右侧面板 → 颜色选择器 → 点击 "Style" 图标
4. 点击 "+" 创建新样式
5. 命名: "Primary/Blue"
6. 重复以上步骤创建所有颜色
```

**需要创建的颜色样式**:
- Primary/Blue (#409EFF)
- Success/Green (#67C23A)
- Danger/Red (#F56C6C)
- Warning/Orange (#E6A23C)
- Info/Gray (#909399)
- Financial/Up (#F56C6C)
- Financial/Down (#67C23A)
- Background/Page (#F5F7FA)
- Text/Primary (#303133)

##### 3.2 文本样式

```
1. 创建文本框 (T键)
2. 设置字体: PingFang SC (Mac) / Microsoft YaHei (Win)
3. 字号: 28px, 行高: 36px, 字重: Semibold (600)
4. 右侧面板 → Text → Style → "+"
5. 命名: "Heading/XL"
```

**需要创建的文本样式**:
- Heading/XL (28px/36px/600)
- Heading/L (24px/32px/600)
- Heading/M (20px/28px/500)
- Body/Regular (14px/22px/400)
- Caption (13px/20px/400)

##### 3.3 组件创建

###### 按钮组件

```
1. 创建矩形: 宽200px, 高32px
2. 填充: Primary Blue (#409EFF)
3. 圆角: 4px
4. 添加文字: "按钮文本"
5. 选中矩形+文字
6. 右键 → Create component (或 Cmd+Option+K)
7. 命名: "Button/Primary/Default"
```

**变体 (Variants)**:
- 创建 4 个状态: Default, Hover, Active, Disabled
- 创建 3 个尺寸: Large (40px), Default (32px), Small (28px)
- 创建 5 个类型: Primary, Success, Warning, Danger, Text

###### 卡片组件

```
1. 创建矩形: 宽600px, 高400px
2. 填充: White (#FFFFFF)
3. 圆角: 8px
4. 阴影: 0 2px 4px rgba(0,0,0,0.05)
5. 创建组件: "Card/Default"
```

###### 表格组件

```
1. 创建表格头部: 48px高, 背景 #F5F7FA
2. 创建表格行: 48px高, 背景 #FFFFFF
3. 创建斑马纹行: 48px高, 背景 #FAFAFA
4. 组合成组件: "Table/Default"
```

#### 步骤 4: 创建页面设计

##### 4.1 仪表盘页面

**基于** `WEB_PAGE_STRUCTURE_GUIDE.md` 第2节:

```
1. 创建新 Frame (F键): 1920 x 1080
2. 命名: "Page-Dashboard"
3. 布局结构:
   - Header (60px高)
   - Sidebar (200px宽)
   - Main Content (Auto Layout)
     - Stats Row (4个卡片)
     - Charts Row (市场热度 + 资金流向)
     - Table Section (板块表现)
```

**组件使用**:
- 使用创建好的 Card 组件
- 使用 Button 组件
- 使用 Table 组件
- 应用颜色和文本样式

##### 4.2 TDX行情页面

```
1. 创建新 Frame: "Page-TDX-Market"
2. 指数监控面板 (顶部)
3. 左侧: 实时行情卡片 (8列宽)
4. 右侧: K线图卡片 (16列宽)
```

##### 4.3 其他页面

按照 `WEB_PAGE_STRUCTURE_GUIDE.md` 依次创建:
- 登录页
- 股票管理
- 市场数据模块 (5个子页面)

### 3.3 导出 Figma 文件

#### 方法 1: 直接导出 .fig 文件 (推荐)

```
1. 点击 Figma 顶部菜单: File
2. 选择 "Save as .fig"
3. 保存到本地: "MyStocks-Design-v1.0.fig"
```

#### 方法 2: 使用 Figma 导出功能

```
1. 选中要导出的页面/组件
2. 右侧面板 → Export → "+"
3. 格式选择: PDF (矢量) 或 PNG (位图)
4. 点击 "Export [名称]"
```

### 3.4 导入到 Pixso

#### 步骤:

```
1. 登录 Pixso: https://pixso.cn
2. 点击 "导入文件"
3. 选择 "从本地导入"
4. 上传 MyStocks-Design-v1.0.fig
5. 等待导入完成 (通常 < 1分钟)
6. 打开设计文件
```

#### 验证导入结果:

- ✅ 颜色样式完整
- ✅ 文本样式保留
- ✅ 组件结构正确
- ✅ 图层命名一致
- ✅ Auto Layout 正常

---

## 4. 使用 Sketch 创建设计并导入

### 4.1 Sketch 安装 (仅 Mac)

1. 下载 Sketch: https://www.sketch.com/downloads/
2. 安装试用版 (30天免费)
3. 打开 Sketch

### 4.2 安装 Element Plus Sketch 库

```
1. Sketch → Preferences → Libraries
2. 点击 "Add Library..."
3. 搜索并添加: "Element Plus UI Kit"
```

### 4.3 创建设计 (流程类似 Figma)

1. 创建新文件: File → New
2. 创建 Artboard: Insert → Artboard (A键)
3. 尺寸: 1920 x 1080
4. 应用设计 Token (使用插件: Sketch Tokens)

### 4.4 导出 .sketch 文件

```
1. File → Save As...
2. 保存为: MyStocks-Design-v1.0.sketch
3. 确保保存为 Sketch 43+ 格式
```

### 4.5 导入到 Pixso

```
1. Pixso → 导入文件 → 从本地导入
2. 上传 .sketch 文件
3. 导入完成
```

---

## 5. 直接在 Pixso 中创建设计

### 5.1 优势

- ✅ 无需安装额外工具
- ✅ 实时协作
- ✅ 云端同步

### 5.2 步骤

#### 5.2.1 创建新文件

```
1. Pixso 首页 → 新建文件
2. 选择 "从模板创建" 或 "空白文件"
3. 命名: "MyStocks Web Design"
```

#### 5.2.2 应用设计 Token

**手动创建颜色库**:

```
1. 创建矩形 (R键)
2. 填充: #409EFF
3. 右侧面板 → 颜色 → "创建颜色样式"
4. 命名: "Primary/Blue"
```

**手动创建文本样式**:

```
1. 创建文本 (T键)
2. 字体: PingFang SC / 思源黑体
3. 字号: 28px, 行高: 36px
4. 右侧面板 → 文本 → "创建文本样式"
5. 命名: "Heading/XL"
```

#### 5.2.3 创建组件

**基于** `MYSTOCKS_DESIGN_SPECIFICATION.md` 第5节:

1. 按钮组件
2. 输入框组件
3. 表格组件
4. 卡片组件

#### 5.2.4 创建页面

**基于** `WEB_PAGE_STRUCTURE_GUIDE.md`:

1. 仪表盘
2. TDX行情
3. 市场数据模块
4. 股票管理

---

## 6. 设计 Token 的应用

### 6.1 Figma 中使用 Token

**插件: Tokens Studio for Figma**

```
1. 安装插件: Plugins → Browse → "Tokens Studio"
2. 导入 Token: Load from file → design-tokens.json
3. 应用到样式: Apply to styles
```

### 6.2 Sketch 中使用 Token

**插件: Sketch Tokens**

```
1. 下载插件: https://github.com/sketch-hq/sketch-tokens
2. 导入 JSON: Plugins → Sketch Tokens → Import
3. 应用样式
```

### 6.3 Pixso 中使用 Token

**手动应用** (Pixso 暂无官方 Token 插件):

```
1. 创建颜色库 (基于 design-tokens.json 的 colors 部分)
2. 创建文本样式 (基于 fontSize/lineHeight/fontWeight)
3. 创建组件 (基于 component 部分)
```

---

## 7. 常见问题

### Q1: 为什么不能直接导入 JSON 文件?

**A**: Pixso (以及 Figma/Sketch) 不支持直接导入 JSON 格式的设计文件。
JSON 是开发用的数据格式,设计工具需要可视化的设计文件 (.fig/.sketch/.xd)。

**解决方案**:
1. 使用 Figma/Sketch 创建设计
2. 应用 design-tokens.json (通过插件)
3. 导出为 .fig/.sketch 文件
4. 导入到 Pixso

### Q2: 没有 Mac,无法使用 Sketch 怎么办?

**A**: 使用 Figma (Web版),无需安装,跨平台。

### Q3: 如何确保设计和开发一致?

**A**:
1. **设计**: 基于 `design-tokens.json` 创建样式
2. **开发**: 直接使用 `design-tokens.json` 生成 CSS 变量

```css
/* 自动生成的 CSS */
:root {
  --color-primary: #409EFF;
  --spacing-md: 12px;
  --font-size-body: 14px;
}
```

### Q4: 导入后组件丢失怎么办?

**A**:
- **原因**: 使用了不兼容的功能 (如某些 Sketch 插件效果)
- **解决**: 使用 Figma (兼容性最好) 或 简化设计 (避免复杂效果)

### Q5: 可以从已有的 Vue 代码生成设计稿吗?

**A**: 不能直接转换,但可以:
1. **截图参考**: 运行项目 → 截图 → 导入 Pixso 作为参考
2. **HTML2Figma**: 使用插件 (实验性,效果有限)
3. **手动重绘**: 基于运行效果在 Pixso 中重新绘制

---

## 8. 快速上手流程 (推荐)

### 最快路径: Figma → Pixso (30分钟)

```
Step 1: 注册 Figma 账号 (5分钟)
  ↓
Step 2: 复制 Element Plus UI Kit (2分钟)
  ↓
Step 3: 创建新文件,添加基础组件 (10分钟)
  - 使用 Element Plus 组件库
  - 应用 design-tokens.json (通过 Tokens Studio 插件)
  ↓
Step 4: 创建关键页面 (10分钟)
  - 仪表盘 (基于模板)
  - TDX行情 (基于模板)
  ↓
Step 5: 导出 .fig 文件 (1分钟)
  ↓
Step 6: 导入到 Pixso (2分钟)
  ✓ 完成!
```

---

## 9. 资源清单

### 9.1 设计工具

| 工具 | 链接 | 价格 | 平台 |
|------|------|------|------|
| **Figma** | https://figma.com | 免费 (有付费版) | Web/Mac/Win |
| **Sketch** | https://sketch.com | $99/年 | Mac only |
| **Pixso** | https://pixso.cn | 免费 (有付费版) | Web |

### 9.2 UI Kit 资源

| 资源名称 | 平台 | 链接 |
|---------|------|------|
| Element Plus Figma Kit | Figma Community | 搜索: "Element Plus" |
| Ant Design Figma | Figma Community | https://www.figma.com/community/file/831698976089873405 |
| Admin Dashboard Template | Figma Community | 搜索: "Dashboard" |

### 9.3 插件工具

| 插件名称 | 用途 | 支持工具 |
|---------|------|----------|
| **Tokens Studio** | 应用设计 Token | Figma |
| **Sketch Tokens** | 应用设计 Token | Sketch |
| **Pixso插件市场** | 各种辅助插件 | Pixso |
| **HTML to Figma** | HTML转设计稿 (实验性) | Figma |

---

## 10. 总结

### 推荐方案

**对于 MyStocks 项目,强烈推荐:**

✅ **Figma → Pixso 路径**

**原因**:
1. Figma 免费且功能强大
2. Element Plus 有现成的 Figma 组件库
3. .fig 格式与 Pixso 100%兼容
4. 可应用 design-tokens.json
5. 跨平台,无需安装

### 下一步

1. ✅ 已生成: `MYSTOCKS_DESIGN_SPECIFICATION.md` - 设计规范
2. ✅ 已生成: `design-tokens.json` - 设计Token
3. ⏭️ 待完成: 在 Figma 中创建设计
4. ⏭️ 待完成: 导出并导入到 Pixso

---

**文档维护**: Claude Code
**最后更新**: 2025-11-09
**版本**: v1.0
